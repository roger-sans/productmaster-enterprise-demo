import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path/'demo.sqlite3')) as client:
        yield client


def endpoint(client,p):
    r=client.get('/api/v1/'+p)
    assert r.status_code==200,r.text
    return r.json()


def test_overview_matches_taxonomy_and_fixture(client):
    o=endpoint(client,'overview')
    t=endpoint(client,'taxonomy')['nodes']
    assert o['products']==640 and o['families']==13
    assert o['taxonomy_nodes']==len(t)==o['families']+o['subfamilies']+o['types']
    assert o['attribute_definitions']==25
    assert o['attribute_coverage_pct']>80


def test_all_products_have_valid_terminal_classification(client):
    taxonomy=endpoint(client,'taxonomy')['nodes']
    leaves={x['id'] for x in taxonomy if x['is_terminal']}
    ids=[]
    for page in range(1,8):
        batch=endpoint(client,f'products?page={page}&limit=100')['items']
        for p in batch:
            ids.append(p['sku'])
            assert p['classification_node_id'] in leaves
            assert len(p['sku'])==12
            assert p['classification']['family']
            assert p['classification']['subfamily']
    assert len(ids)==len(set(ids))==640


def test_terminal_subfamily_has_no_fabricated_type(client):
    taxonomy=endpoint(client,'taxonomy')['nodes']
    subs=[n for n in taxonomy if n['level']==2 and n['is_terminal'] and n['product_count']>0]
    assert subs
    all_products=[p for page in range(1,8) for p in endpoint(client,f'products?page={page}&limit=100')['items']]
    record=next(p for p in all_products if p['classification_node_id']==subs[0]['id'])
    assert record['classification']['type'] is None


def test_attributes_are_scoped_and_typed(client):
    attrs=endpoint(client,'attributes')['definitions']
    assert any(a['data_type']=='option' for a in attrs)
    assert any(a['data_type']=='decimal' for a in attrs)
    assert any(a['data_type']=='boolean' for a in attrs)
    p=endpoint(client,'products/PRD000000001')
    assert p['attribute_definitions']
    assert all('required' in a and 'value' in a for a in p['attribute_definitions'])


def test_catalogue_filter_and_detail(client):
    page=endpoint(client,'products?search=PRD000000001')
    assert page['total']==1
    p=endpoint(client,'products/PRD000000001')
    by_family=endpoint(client,'products?family='+p['classification']['family'].replace(' ','%20'))
    assert by_family['total']>0
    assert p['source_mappings']


def test_missing_sku_404(client):
    assert client.get('/api/v1/products/NOTFOUND0000').status_code==404


def request(client,sku,kind,payload,actor='sam.commercial'):
    return client.post('/api/v1/requests',json={
      'sku':sku,'kind':kind,'actor':actor,'department':'Commercial',
      'reason':'Functional validation: correct the catalogue mapping after review.',
      'payload':payload})


def decision(client,id,actor='lee.steward',decision='approve'):
    return client.post(f'/api/v1/requests/{id}/decision',json={
     'reviewer':actor,'decision':decision,'note':'Reviewed the evidence and agreed business scope.'})


def test_classification_requires_approval_before_mutation(client):
    taxonomy=endpoint(client,'taxonomy')['nodes']
    p=endpoint(client,'products/PRD000000001')
    parent=next(x['parent_id'] for x in taxonomy if x['id']==p['classification_node_id'])
    sibling=next(x for x in taxonomy if x['parent_id']==parent and x['id']!=p['classification_node_id'])
    r=request(client,p['sku'],'reclassification',{'target_node_id':sibling['id']})
    assert r.status_code==201,r.text
    assert endpoint(client,'products/'+p['sku'])['classification_node_id']==p['classification_node_id']
    d=decision(client,r.json()['id'])
    assert d.status_code==200,d.text
    changed=endpoint(client,'products/'+p['sku'])
    assert changed['classification_node_id']==sibling['id']
    assert changed['version']==p['version']+1
    assert any(a['event_type']=='classification_approved' for a in changed['audit'])


def test_requester_cannot_review_own_request(client):
    existing=endpoint(client,'requests')['items'][0]
    r=decision(client,existing['id'],existing['actor'])
    assert r.status_code==403


def test_rejection_preserves_master(client):
    p=endpoint(client,'products/PRD000000001')
    r=request(client,p['sku'],'attributes',{'attributes':{'recyclable_packaging':False}})
    assert r.status_code==201,r.text
    d=decision(client,r.json()['id'],decision='reject')
    assert d.status_code==200
    again=endpoint(client,'products/'+p['sku'])
    assert again['version']==p['version'] and again['attributes']==p['attributes']


def test_reviewer_cannot_decide_twice(client):
    req=endpoint(client,'requests')['items'][0]
    assert decision(client,req['id']).status_code==200
    assert decision(client,req['id']).status_code==409


def test_duplicate_pending_request_blocked(client):
    r1=request(client,'PRD000000001','attributes',{'attributes':{'recyclable_packaging':False}})
    assert r1.status_code==201
    r2=request(client,'PRD000000001','attributes',{'attributes':{'recyclable_packaging':True}})
    assert r2.status_code==409


def test_attribute_value_validation(client):
    p=endpoint(client,'products/PRD000000001')
    code=next(a['code'] for a in p['attribute_definitions'] if a['data_type']=='decimal')
    r=request(client,p['sku'],'attributes',{'attributes':{code:'not-a-number'}})
    assert r.status_code==422
    r=request(client,p['sku'],'attributes',{'attributes':{'unapproved_field':'anything'}})
    assert r.status_code==422


def test_created_product_requires_valid_leaf_and_typed_required_values(client):
    p=endpoint(client,'products/PRD000000001')
    model={k:p[k] for k in ('description','classification_node_id','brand','range_name','sector','lifecycle','business_role','source_system','attributes')}
    model.update({'sku':'NEW000000001','actor':'demo.admin'})
    ok=client.post('/api/v1/products',json=model)
    assert ok.status_code==201,ok.text
    duplicate=client.post('/api/v1/products',json=model)
    assert duplicate.status_code==409
    model['sku']='NEW000000002';model['attributes']={}
    incomplete=client.post('/api/v1/products',json=model)
    assert incomplete.status_code==422


def test_taxonomy_extension_rejects_unsafe_subfamily_transition(client):
    nodes=endpoint(client,'taxonomy')['nodes']
    p=endpoint(client,'products/PRD000000001')
    parent=next(n for n in nodes if n['id']==p['classification_node_id'])
    x=client.post('/api/v1/taxonomy/nodes',json={'parent_id':parent['id'],'code':'custom_new_type','label':'Custom Type','actor':'demo.admin'})
    assert x.status_code==422 # cannot exceed three levels
    candidate=next(n for n in nodes if n['level']==2 and n['is_terminal'] and n['product_count']>0)
    y=client.post('/api/v1/taxonomy/nodes',json={'parent_id':candidate['id'],'code':'custom_type_two','label':'Custom Type','actor':'demo.admin'})
    assert y.status_code==409


def test_new_optional_attribute_definition(client):
    root=next(n for n in endpoint(client,'taxonomy')['nodes'] if n['level']==1)
    payload={'code':'test_feature','label':'Test feature','data_type':'option','options':['A','B'],
      'family_node_id':root['id'],'is_required':False,'actor':'demo.admin'}
    r=client.post('/api/v1/attributes/definitions',json=payload)
    assert r.status_code==201,r.text
    assert any(x['code']=='test_feature' for x in endpoint(client,'attributes')['definitions'])


def test_intelligence_is_read_only_and_keeps_missing_distinct(client):
    original=endpoint(client,'products/PRD000000001')
    view=endpoint(client,'intelligence?limit=300')
    assert view['rule_status'].startswith('Exploratory')
    assert view['covered']>0 and view['missing']>0
    assert any(x['coverage_days'] is None for x in view['items'])
    assert all('context_version' in x and 'source_revisions' in x for x in view['items'])
    assert endpoint(client,'products/PRD000000001')['version']==original['version']


def test_api_documentation_and_static_application(client):
    assert client.get('/').status_code==200
    assert 'ProductMaster' in client.get('/').text
    assert client.get('/docs').status_code==200
    assert client.get('/static/app.js').status_code==200


def test_source_authority_contract_separates_metrics(client):
    x=endpoint(client,'contracts')
    assert 'stock' in x['external_authority']
    assert 'technical_attributes' in x['master_authority']
    p=endpoint(client,'products/PRD000000001')
    assert 'stock_available' not in p['attributes']


def test_cross_family_reclassification_fails_without_attribute_migration(client):
    p=endpoint(client,'products/PRD000000001')
    nodes=endpoint(client,'taxonomy')['nodes']
    different_family=next(n for n in nodes if n['level']==3 and n['is_terminal'] and n['path'].split(' / ')[0]!=p['classification']['family'])
    r=request(client,p['sku'],'reclassification',{'target_node_id':different_family['id']})
    assert r.status_code==201
    res=decision(client,r.json()['id'])
    assert res.status_code in (409,422)
    after=endpoint(client,'products/'+p['sku'])
    assert after['classification_node_id']==p['classification_node_id']
    assert after['attributes']==p['attributes']


def test_new_required_attribute_fails_without_backfill(client):
    root=next(n for n in endpoint(client,'taxonomy')['nodes'] if n['level']==1)
    r=client.post('/api/v1/attributes/definitions',json={
      'code':'mandatory_feature','label':'New mandatory feature','data_type':'string',
      'family_node_id':root['id'],'is_required':True,'actor':'demo.admin'})
    assert r.status_code==409


def test_new_type_on_nonterminal_subfamily(client):
    nodes=endpoint(client,'taxonomy')['nodes']
    parent=next(n for n in nodes if n['level']==2 and not n['is_terminal'])
    response=client.post('/api/v1/taxonomy/nodes',json={
      'parent_id':parent['id'],'code':'demo_unique_type','label':'Demo Unique Type','actor':'demo.admin'})
    assert response.status_code==201,response.text
    new=next(n for n in endpoint(client,'taxonomy')['nodes'] if n['code']=='demo_unique_type')
    assert new['is_terminal'] and new['level']==3 and new['parent_id']==parent['id']


def test_create_product_rejects_unknown_attributes(client):
    p=endpoint(client,'products/PRD000000001')
    model={k:p[k] for k in ('description','classification_node_id','brand','range_name','sector','lifecycle','business_role','source_system','attributes')}
    model.update({'sku':'NEW000000001','actor':'demo.admin'})
    model['attributes']['unrelated_metric']=12.1
    assert client.post('/api/v1/products',json=model).status_code==422


def test_governed_dimension_update(client):
    before=endpoint(client,'products/PRD000000001')
    created=request(client,before['sku'],'dimensions',{'dimensions':{'sector':'Research retail'}})
    assert created.status_code==201,created.text
    assert endpoint(client,'products/'+before['sku'])['sector']==before['sector']
    done=decision(client,created.json()['id'])
    assert done.status_code==200,done.text
    after=endpoint(client,'products/'+before['sku'])
    assert after['sector']=='Research retail' and after['version']==before['version']+1
    assert any(a['event_type']=='dimensions_approved' for a in after['audit'])


def test_source_owned_fields_cannot_be_governed_dimension_changes(client):
    req=request(client,'PRD000000001','dimensions',{'dimensions':{'source_system':'pretend_source'}})
    assert req.status_code==422


def test_intelligence_evidence_filter(client):
    all_data=endpoint(client,'intelligence?limit=15')
    missing=endpoint(client,'intelligence?evidence=partial&limit=100')
    assert all_data['total']==640
    assert missing['selection_total']>0
    assert all(x['evidence']=='partial' for x in missing['items'])
    assert all_data['covered']+all_data['missing']==640
