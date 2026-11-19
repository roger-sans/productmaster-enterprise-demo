"""ProductMaster / ProductIntelligence — independent synthetic portfolio application."""
from __future__ import annotations
import json
import re
import uuid
from collections import Counter, defaultdict
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Literal
import sqlite3
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .db import initialize, connect, now, DEFAULT_PATH

ROOT = Path(__file__).resolve().parent

class CreateRequest(BaseModel):
    sku: str
    kind: Literal['reclassification','attributes','dimensions']
    actor: str = Field(min_length=3,max_length=80)
    department: Literal['Product Management','Commercial','Procurement','Operations','Finance','Data & IT','Quality']
    reason: str = Field(min_length=12,max_length=1200)
    payload: dict[str, Any]

class Decision(BaseModel):
    reviewer: str=Field(min_length=3,max_length=80)
    decision: Literal['approve','reject']
    note: str=Field(min_length=5,max_length=800)

class NewTaxonomyNode(BaseModel):
    parent_id: str
    label: str=Field(min_length=2,max_length=70)
    code: str=Field(pattern=r'^[a-z][a-z0-9_]{3,100}$')
    actor: str=Field(min_length=3,max_length=80)

class NewAttributeDefinition(BaseModel):
    code: str=Field(pattern=r'^[a-z][a-z0-9_]{2,55}$')
    label: str=Field(min_length=3,max_length=70)
    data_type: Literal['string','integer','decimal','boolean','option']
    unit: str|None=None
    options: list[str]=Field(default_factory=list)
    family_node_id: str
    is_required: bool=False
    actor: str=Field(min_length=3,max_length=80)

class NewProduct(BaseModel):
    sku: str=Field(pattern=r'^[A-Z0-9]{12}$')
    description: str=Field(min_length=5,max_length=200)
    classification_node_id: str
    brand: str=Field(min_length=2,max_length=60)
    range_name: str=Field(min_length=2,max_length=60)
    sector: str
    lifecycle: str
    business_role: str
    source_system: str=Field(min_length=2,max_length=60)
    attributes: dict[str,Any]
    actor: str=Field(min_length=3,max_length=80)


def fail(code:int, message:str):
    raise HTTPException(status_code=code,detail=message)

def nodes_map(cn):
    return {r['id']:dict(r) for r in cn.execute('SELECT * FROM classification_node ORDER BY level,position,label')}

def classification_path(nid, nodes):
    chain=[];visited=set()
    while nid:
        if nid not in nodes or nid in visited:fail(409,'Invalid taxonomy reference or cycle')
        visited.add(nid); chain.insert(0,nodes[nid]);nid=nodes[nid]['parent_id']
    return chain

def is_terminal(nid,nodes):
    return nid in nodes and bool(nodes[nid]['is_active']) and not any(n['parent_id']==nid and n['is_active'] for n in nodes.values())

def rules_for(nid,cn,nodes):
    chain=classification_path(nid,nodes)
    ids=[x['id'] for x in chain]
    if not ids:return {}
    marks=','.join(['?']*len(ids))
    rows=cn.execute('''SELECT ca.node_id,ca.is_required,ad.* FROM classification_attribute ca
      JOIN attribute_definition ad ON ca.attribute_code=ad.code
      WHERE ca.node_id IN ('''+marks+') AND ad.is_active=1',ids).fetchall()
    rules={}
    for r in rows:
        d=dict(r);d['options']=json.loads(d['options']);d['is_required']=bool(d['is_required'])
        rules[d['code']]=d
    return rules

def validate_attributes(attrs, rules, accepted=True, partial=False):
    if not isinstance(attrs,dict):fail(422,'Attributes must be an object')
    for code,value in attrs.items():
        if code not in rules:fail(422,f'Attribute {code} is not applicable for this classification')
        r=rules[code];t=r['data_type']
        if t=='option' and (not isinstance(value,str) or value not in r['options']):fail(422,f'{code}: value outside approved vocabulary')
        if t=='string' and (not isinstance(value,str) or not value.strip()):fail(422,f'{code}: expected text')
        if t=='boolean' and not isinstance(value,bool):fail(422,f'{code}: expected boolean')
        if t=='integer' and (isinstance(value,bool) or not isinstance(value,int) or value<0):fail(422,f'{code}: expected nonnegative integer')
        if t=='decimal' and (isinstance(value,bool) or not isinstance(value,(int,float)) or value<0):fail(422,f'{code}: expected nonnegative number')
    if accepted and not partial:
        missing=[code for code,r in rules.items() if r['is_required'] and code not in attrs]
        if missing:fail(422,f'Missing required attributes: {", ".join(missing)}')

def product_json(row,cn,nodes,rich=False):
    p=dict(row);p['attributes']=json.loads(p['attributes'])
    chain=classification_path(p['classification_node_id'],nodes)
    p['classification']={
      'path':' / '.join(n['label'] for n in chain),
      'nodes':[{'id':n['id'],'code':n['code'],'label':n['label'],'level':n['level']} for n in chain],
      'family':chain[0]['label'] if chain else None,
      'subfamily':chain[1]['label'] if len(chain)>1 else None,
      'type':chain[2]['label'] if len(chain)>2 else None
    }
    if rich:
        rules=rules_for(p['classification_node_id'],cn,nodes)
        p['attribute_definitions']=[{'code':r['code'],'label':r['label'],'data_type':r['data_type'], 'unit':r['unit'],
          'options':r['options'],'required':r['is_required'],'value':p['attributes'].get(r['code'])} for r in rules.values()]
        p['source_mappings']=[dict(r) for r in cn.execute('SELECT source_system,external_reference,source_description,is_primary FROM source_mapping WHERE sku=?',(p['sku'],))]
        p['audit']=[dict(r) for r in cn.execute('SELECT * FROM audit_event WHERE sku=? ORDER BY id DESC LIMIT 20',(p['sku'],))]
    return p

def request_json(row,cn,nodes):
    r=dict(row);r['payload']=json.loads(r['payload'])
    p=cn.execute('SELECT * FROM product WHERE sku=?',(r['sku'],)).fetchone()
    r['product_description']=p['description'] if p else ''
    if r['kind']=='reclassification':
        target=nodes.get(r['payload'].get('target_node_id'))
        if target:r['target_path']=' / '.join(n['label'] for n in classification_path(target['id'],nodes))
    return r

def audit(cn,sku,event_type,actor,old,new,req_id=None):
    cn.execute('''INSERT INTO audit_event(sku,event_type,actor,change_request_id,previous_value,next_value,created_at)
     VALUES(?,?,?,?,?,?,?)''',(sku,event_type,actor,req_id,json.dumps(old),json.dumps(new),now()))

def create_app(db_path:Path|str=DEFAULT_PATH):
    db_path=Path(db_path)
    @asynccontextmanager
    async def lifespan(_app):
        initialize(db_path)
        yield
    app=FastAPI(title='ProductMaster Enterprise', version='1.0.0',
        description='Original synthetic product master and explainable product intelligence demo.',lifespan=lifespan)
    app.mount('/static',StaticFiles(directory=str(ROOT/'static')),name='static')

    @app.get('/',include_in_schema=False)
    def home():return FileResponse(ROOT/'static'/'index.html')

    @app.get('/api/v1/overview')
    def overview():
        with connect(db_path) as cn:
            nodes=nodes_map(cn);products=cn.execute('SELECT * FROM product').fetchall()
            byfam=Counter();quality=Counter()
            for p in products:
                chain=classification_path(p['classification_node_id'],nodes)
                byfam[chain[0]['label']]+=1
                rules=rules_for(p['classification_node_id'],cn,nodes)
                a=json.loads(p['attributes'])
                quality['total']+=len(rules)
                quality['covered']+=sum(1 for k in rules if k in a)
            counts=Counter(n['level'] for n in nodes.values())
            return {
                'products':len(products),'families':counts[1],'subfamilies':counts[2],
                'types':counts[3],'taxonomy_nodes':len(nodes),
                'attribute_definitions':cn.execute('SELECT COUNT(*) FROM attribute_definition').fetchone()[0],
                'pending_requests':cn.execute("SELECT COUNT(*) FROM change_request WHERE status='pending'").fetchone()[0],
                'accepted_products':sum(p['status']=='accepted' for p in products),
                'attribute_coverage_pct':round(100*quality['covered']/quality['total'],1) if quality['total'] else 0,
                'by_family':[{'name':k,'count':v} for k,v in sorted(byfam.items(),key=lambda x:-x[1])],
                'snapshot':'Synthetic dataset · 31 October 2026',
                'domains':[{'name':'Product Management','responsibility':'Classification & specifications'},
                           {'name':'Commercial','responsibility':'Market positioning & range'},
                           {'name':'Procurement','responsibility':'Supplier mapping'},
                           {'name':'Operations','responsibility':'Source reconciliation'},
                           {'name':'Finance','responsibility':'Economic metrics'},
                           {'name':'Data & IT','responsibility':'Platform, APIs and governance'}]
            }

    @app.get('/api/v1/taxonomy')
    def taxonomy():
        with connect(db_path) as cn:
            nodes=nodes_map(cn);counts=defaultdict(int)
            for r in cn.execute('SELECT classification_node_id FROM product'):
                for n in classification_path(r['classification_node_id'],nodes):counts[n['id']]+=1
            out=[]
            for n in nodes.values():
                d=dict(n);d['is_terminal']=is_terminal(n['id'],nodes)
                d['product_count']=counts[n['id']]
                d['path']=' / '.join(x['label'] for x in classification_path(n['id'],nodes))
                out.append(d)
            return {'nodes':sorted(out,key=lambda n:(n['path'])),'levels':['Family','Subfamily','Type']}

    @app.get('/api/v1/attributes')
    def attributes():
        with connect(db_path) as cn:
            rows=[]
            for r in cn.execute('SELECT * FROM attribute_definition ORDER BY label'):
                d=dict(r);d['options']=json.loads(d['options'])
                d['applicability']=[{'node_id':z['node_id'],'node_label':z['label'],'required':bool(z['is_required'])}
                     for z in cn.execute('''SELECT ca.node_id,ca.is_required,n.label FROM classification_attribute ca
                     JOIN classification_node n ON n.id=ca.node_id WHERE ca.attribute_code=?''',(d['code'],))]
                rows.append(d)
            return {'definitions':rows}

    @app.get('/api/v1/products')
    def products(search:str='', family:str='',page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=100)):
        with connect(db_path) as cn:
            nodes=nodes_map(cn);term=search.lower().strip()
            rows=cn.execute('SELECT * FROM product ORDER BY sku').fetchall()
            selected=[]
            for r in rows:
                p=product_json(r,cn,nodes)
                if term and term not in (p['sku']+' '+p['description']+' '+p['brand']).lower():continue
                if family and p['classification']['family']!=family:continue
                selected.append(p)
            return {'items':selected[(page-1)*limit:page*limit],'total':len(selected), 'page':page,'limit':limit}

    @app.get('/api/v1/products/{sku}')
    def product(sku:str):
        with connect(db_path) as cn:
            row=cn.execute('SELECT * FROM product WHERE sku=?',(sku,)).fetchone()
            if not row:fail(404,'Product not found')
            return product_json(row,cn,nodes_map(cn),rich=True)

    @app.post('/api/v1/products',status_code=201)
    def add_product(model:NewProduct):
        with connect(db_path) as cn:
            nodes=nodes_map(cn)
            if not is_terminal(model.classification_node_id,nodes):fail(422,'Classification must be an active terminal node')
            rules=rules_for(model.classification_node_id,cn,nodes)
            validate_attributes(model.attributes,rules)
            if cn.execute('SELECT 1 FROM product WHERE sku=?',(model.sku,)).fetchone():fail(409,'Duplicate corporate product identity')
            time=now()
            cn.execute('''INSERT INTO product(sku,description,classification_node_id,brand,range_name,sector,lifecycle,business_role,
                source_system,attributes,status,version,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (model.sku,model.description,model.classification_node_id,model.brand,model.range_name,
                 model.sector,model.lifecycle,model.business_role,model.source_system,json.dumps(model.attributes),'accepted',1,time,time))
            cn.execute('INSERT INTO source_mapping(sku,source_system,external_reference,source_description,is_primary) VALUES(?,?,?,?,1)',
                 (model.sku,model.source_system,f'DEMO-{model.sku}',model.description))
            audit(cn,model.sku,'product_created',model.actor,None,{'sku':model.sku})
            return {'sku':model.sku,'status':'created'}

    @app.get('/api/v1/requests')
    def requests(status:str=''):
        with connect(db_path) as cn:
            nodes=nodes_map(cn)
            rows=cn.execute('SELECT * FROM change_request WHERE status=? ORDER BY id DESC',(status,)).fetchall() if status else cn.execute('SELECT * FROM change_request ORDER BY id DESC').fetchall()
            return {'items':[request_json(r,cn,nodes) for r in rows]}

    @app.post('/api/v1/requests',status_code=201)
    def new_request(model:CreateRequest):
        with connect(db_path) as cn:
            row=cn.execute('SELECT * FROM product WHERE sku=?',(model.sku,)).fetchone()
            if not row:fail(404,'Product not found')
            nodes=nodes_map(cn)
            if model.kind=='reclassification':
                target=model.payload.get('target_node_id')
                if not isinstance(target,str) or not is_terminal(target,nodes):fail(422,'Target must be an active terminal classification')
                if target==row['classification_node_id']:fail(422,'Requested classification is already current')
                # Existing values can become inapplicable. They are kept only if
                # business submits a separate governed attribute update.
            elif model.kind=='attributes':
                attrs=model.payload.get('attributes')
                if not isinstance(attrs,dict) or not attrs:fail(422,'Provide at least one attribute change')
                validate_attributes(attrs,rules_for(row['classification_node_id'],cn,nodes),partial=True)
            else:
                changes=model.payload.get('dimensions')
                allowed={'brand','range_name','sector','lifecycle','business_role'}
                if not isinstance(changes,dict) or not changes or set(changes)-allowed:
                    fail(422,'Changes must contain supported governed commercial dimensions')
                if any(not isinstance(v,str) or not v.strip() or len(v)>100 for v in changes.values()):
                    fail(422,'Dimension values must be nonempty strings under 100 characters')
            if cn.execute("SELECT 1 FROM change_request WHERE sku=? AND kind=? AND status='pending'",(model.sku,model.kind)).fetchone():
                fail(409,'An open request of this kind already exists for this product')
            cur=cn.execute('''INSERT INTO change_request(sku,kind,actor,department,reason,payload,expected_version,status,created_at)
              VALUES(?,?,?,?,?,?,?,'pending',?)''',(model.sku,model.kind,model.actor,model.department,model.reason,
                 json.dumps(model.payload),row['version'],now()))
            audit(cn,model.sku,'change_requested',model.actor,None,{'kind':model.kind,'request_id':cur.lastrowid},cur.lastrowid)
            return {'id':cur.lastrowid,'status':'pending','product_unchanged':True}

    @app.post('/api/v1/requests/{request_id}/decision')
    def decide(request_id:int,model:Decision):
        with connect(db_path) as cn:
            cn.execute('BEGIN IMMEDIATE')
            req=cn.execute('SELECT * FROM change_request WHERE id=?',(request_id,)).fetchone()
            if not req:fail(404,'Request not found')
            if req['status']!='pending':fail(409,'Request is already decided')
            if model.reviewer.lower()==req['actor'].lower():fail(403,'Four-eyes rule: requester cannot approve own changes')
            row=cn.execute('SELECT * FROM product WHERE sku=?',(req['sku'],)).fetchone()
            nodes=nodes_map(cn)
            payload=json.loads(req['payload'])
            if model.decision=='approve':
                if row['version']!=req['expected_version']:fail(409,'Product has changed; submit a new request against its current version')
                if req['kind']=='reclassification':
                    target=payload['target_node_id']
                    if not is_terminal(target,nodes):fail(409,'Destination is no longer a valid terminal')
                    original=json.loads(row['attributes']);rules=rules_for(target,cn,nodes)
                    # Never delete technical values simply because classification changes.
                    # Cross-family transitions need a separately agreed attribute migration.
                    invalid=set(original)-set(rules)
                    if invalid:
                        fail(409,'Reclassification requires a governed attribute migration for: '+', '.join(sorted(invalid)))
                    validate_attributes(original,rules,accepted=row['status']=='accepted')
                    cn.execute('UPDATE product SET classification_node_id=?,version=version+1,updated_at=? WHERE sku=?',
                      (target,now(),row['sku']))
                    audit(cn,row['sku'],'classification_approved',model.reviewer,
                          {'node_id':row['classification_node_id']},{'node_id':target},request_id)
                elif req['kind']=='attributes':
                    old=json.loads(row['attributes']);updated={**old,**payload['attributes']}
                    validate_attributes(updated,rules_for(row['classification_node_id'],cn,nodes))
                    cn.execute('UPDATE product SET attributes=?,version=version+1,updated_at=? WHERE sku=?',
                          (json.dumps(updated),now(),row['sku']))
                    audit(cn,row['sku'],'attributes_approved',model.reviewer,old,updated,request_id)
                else:
                    dims=payload['dimensions']
                    old={key:row[key] for key in dims}
                    fields=list(dims)
                    cn.execute('UPDATE product SET '+','.join(x+'=?' for x in fields)+',version=version+1,updated_at=? WHERE sku=?',
                        [dims[x] for x in fields]+[now(),row['sku']])
                    audit(cn,row['sku'],'dimensions_approved',model.reviewer,old,dims,request_id)
            else:
                audit(cn,row['sku'],'change_rejected',model.reviewer,None,{'request_id':request_id,'reason':model.note},request_id)
            cn.execute('''UPDATE change_request SET status=?,reviewer=?,decision_note=?,decided_at=? WHERE id=?''',
                 ('approved' if model.decision=='approve' else 'rejected',model.reviewer,model.note,now(),request_id))
            return {'id':request_id,'status':'approved' if model.decision=='approve' else 'rejected'}

    @app.get('/api/v1/audit')
    def audit_list(limit:int=Query(30,ge=1,le=200)):
        with connect(db_path) as cn:return {'items':[dict(x) for x in cn.execute('SELECT * FROM audit_event ORDER BY id DESC LIMIT ?',(limit,))]}

    @app.post('/api/v1/taxonomy/nodes',status_code=201)
    def add_taxonomy_node(model:NewTaxonomyNode):
        with connect(db_path) as cn:
            nodes=nodes_map(cn);parent=nodes.get(model.parent_id)
            if not parent or not parent['is_active']:fail(404,'Parent node not found')
            if parent['level']>=3:fail(422,'Public demonstration supports at most three business-facing levels')
            if cn.execute('SELECT 1 FROM product WHERE classification_node_id=?',(parent['id'],)).fetchone():
                fail(409,'Parent has accepted products. An approved transition plan is required before adding children')
            if cn.execute('SELECT 1 FROM classification_node WHERE code=?',(model.code,)).fetchone():fail(409,'Code already exists')
            # Direct insertion is admin-only in demo and should be workflow-controlled in production.
            ident=str(uuid.uuid4());position=cn.execute('SELECT COUNT(*) FROM classification_node WHERE parent_id=?',(parent['id'],)).fetchone()[0]+1
            cn.execute('INSERT INTO classification_node(id,code,parent_id,label,level,position) VALUES(?,?,?,?,?,?)',
                (ident,model.code,parent['id'],model.label,parent['level']+1,position))
            audit(cn,'TAXONOMY','taxonomy_node_created',model.actor,None,{'code':model.code,'parent':parent['code']})
            return {'id':ident,'label':model.label}

    @app.post('/api/v1/attributes/definitions',status_code=201)
    def add_attribute_definition(model:NewAttributeDefinition):
        if model.data_type=='option' and not model.options:fail(422,'Option attributes require vocabulary')
        if model.data_type!='option' and model.options:fail(422,'Options only supported for option datatype')
        with connect(db_path) as cn:
            nodes=nodes_map(cn);root=nodes.get(model.family_node_id)
            if not root or root['level']!=1:fail(422,'Applicability must target a valid family node')
            if cn.execute('SELECT 1 FROM attribute_definition WHERE code=?',(model.code,)).fetchone():fail(409,'Definition code already exists')
            if model.is_required:
                # Do not invalidate existing accepted products by imposing a mandatory
                # attribute without a migration and owner-approved rollout.
                assigned=cn.execute("SELECT classification_node_id FROM product WHERE status='accepted'").fetchall()
                if any(classification_path(r['classification_node_id'],nodes)[0]['id']==model.family_node_id for r in assigned):
                    fail(409,'Requiredness needs an accepted-product backfill and approval plan. Create an optional definition first.')
            cn.execute('INSERT INTO attribute_definition(code,label,data_type,unit,options) VALUES(?,?,?,?,?)',
                  (model.code,model.label,model.data_type,model.unit,json.dumps(model.options)))
            cn.execute('INSERT INTO classification_attribute(node_id,attribute_code,is_required) VALUES(?,?,?)',
                  (model.family_node_id,model.code,int(model.is_required)))
            audit(cn,'METADATA','attribute_definition_created',model.actor,None,{'code':model.code,'family':root['code']})
            return {'code':model.code,'status':'created'}

    @app.get('/api/v1/intelligence')
    def intelligence(family:str='',evidence:str='',limit:int=Query(60,ge=1,le=300)):
        with connect(db_path) as cn:
            nodes=nodes_map(cn);products=cn.execute('SELECT * FROM product ORDER BY sku').fetchall()
            metric_rows=cn.execute('SELECT * FROM metric_observation').fetchall()
            observations=defaultdict(dict)
            for m in metric_rows:observations[m['sku']][m['metric_code']]=dict(m)
            rows=[];covered=0;missing=0;review=0
            for p in products:
                item=product_json(p,cn,nodes)
                if family and item['classification']['family']!=family:continue
                source=observations[p['sku']]
                def val(code):return source.get(code,{}).get('observation_value')
                sales=val('net_sales_qty_90d');stock=val('stock_available')
                open_d=val('open_demand_30d');inbound=val('inbound_supply_30d')
                revenue=val('net_sales_amount_90d');margin=val('gross_margin_amount_90d')
                daily=None if sales is None or sales<=0 else sales/90
                coverage=round(stock/daily,1) if stock is not None and daily else None
                shortfall=max(0,open_d-(stock+inbound)) if None not in (open_d,stock,inbound) else None
                margin_pct=round(100*margin/revenue,1) if revenue is not None and revenue>0 and margin is not None else None
                has_evidence=all(x is not None for x in (sales,stock,open_d,inbound))
                if has_evidence:covered+=1
                else:missing+=1
                facets=[]
                if shortfall is not None and shortfall>0: facets.append('Projected supply gap')
                if coverage is not None and coverage<30:facets.append('Below 30 days illustrative coverage')
                if stock is None or sales is None:facets.append('Missing core evidence')
                if sales==0:facets.append('No demand in sample period')
                if margin_pct is None:facets.append('Financial evidence incomplete')
                if facets and has_evidence:review+=1
                rows.append({'sku':p['sku'],'description':p['description'],'family':item['classification']['family'],
                   'type':item['classification']['type'],'sales_90d':sales,'stock':stock,'open_demand_30d':open_d,
                   'inbound_supply_30d':inbound,'coverage_days':coverage,'projected_shortfall':shortfall,
                   'margin_pct':margin_pct,'evidence':'complete' if has_evidence else 'partial',
                   'review_facets':facets,'source_revisions':sorted({x['source_revision'] for x in source.values()}),
                   'context_version':p['version']})
            complete=[x for x in rows if x['evidence']=='complete']
            partial=[x for x in rows if x['evidence']!='complete']
            complete.sort(key=lambda x:(-(x['projected_shortfall'] or 0), x['sku']))
            partial.sort(key=lambda x:x['sku'])
            # Surface missing evidence instead of burying every exception below the limit.
            mixed=[]
            while complete or partial:
                mixed.extend(complete[:5]); del complete[:5]
                if partial:mixed.append(partial.pop(0))
            selection=[x for x in mixed if not evidence or x['evidence']==evidence]
            return {'period':'Synthetic scenario: sales 90 days ending 2026-10-31; open demand next 30 days',
               'snapshot':'2026-10-31','rule_version':'illustrative-v1','rule_status':'Exploratory — not an approved commercial policy',
               'covered':covered,'missing':missing,'review_candidates':review,'total':len(rows),'selection_total':len(selection),'items':selection[:limit],
               'guardrail':'No automated purchasing, reclassification or changes to source systems. Financial values are synthetic.'}

    @app.get('/api/v1/contracts')
    def contracts():
        return {'version':'1.0','product_identity':'Stable 12-character synthetic SKU + internal taxonomy UUID',
          'master_authority':['approved_classification','technical_attributes','brand','range','sector','lifecycle','business_role'],
          'external_authority':['erp_description','stock','sales','orders','finance_values'],
          'analytics_policy':'External observations never become editable master attributes',
          'quality_rules':['active_terminal_classification','applicable_typed_attributes','requiredness','four_eyes_approvals','audit_trail'],
          'consumer_interfaces':['/api/v1/products','/api/v1/taxonomy','/api/v1/attributes','/api/v1/intelligence']}

    return app

app=create_app()
