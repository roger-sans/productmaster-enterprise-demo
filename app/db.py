"""Local SQLite persistence for a fully synthetic ProductMaster demo.

SQLite is used to make the public demonstration zero-infrastructure. In an
enterprise deployment, this would be a persistent, protected database service.
"""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timezone
from .catalog import create_nodes, fake_products, SPECS, TREE, applicable_specs

DEFAULT_PATH = Path(__file__).resolve().parent.parent / 'data' / 'productmaster.sqlite3'


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

@contextmanager
def connect(path:Path|str=DEFAULT_PATH):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    cn=sqlite3.connect(str(path),timeout=20)
    cn.row_factory=sqlite3.Row
    cn.execute('PRAGMA foreign_keys = ON')
    cn.execute('PRAGMA busy_timeout = 20000')
    try:
        yield cn
        cn.commit()
    except BaseException:
        cn.rollback()
        raise
    finally:cn.close()

SCHEMA='''
CREATE TABLE IF NOT EXISTS classification_node (
 id TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, parent_id TEXT REFERENCES classification_node(id),
 label TEXT NOT NULL, level INTEGER NOT NULL CHECK(level>=1), position INTEGER NOT NULL,
 is_active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS attribute_definition (
 code TEXT PRIMARY KEY, label TEXT NOT NULL, data_type TEXT NOT NULL,
 unit TEXT, options TEXT NOT NULL DEFAULT '[]', is_active INTEGER NOT NULL DEFAULT 1,
 business_owner TEXT NOT NULL DEFAULT 'Product Management'
);
CREATE TABLE IF NOT EXISTS classification_attribute (
 node_id TEXT NOT NULL REFERENCES classification_node(id),
 attribute_code TEXT NOT NULL REFERENCES attribute_definition(code),
 is_required INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY(node_id,attribute_code)
);
CREATE TABLE IF NOT EXISTS product (
 sku TEXT PRIMARY KEY CHECK(length(sku)=12), description TEXT NOT NULL,
 classification_node_id TEXT NOT NULL REFERENCES classification_node(id),
 brand TEXT, range_name TEXT, sector TEXT, lifecycle TEXT, business_role TEXT,
 source_system TEXT NOT NULL, attributes TEXT NOT NULL DEFAULT '{}',
 status TEXT NOT NULL CHECK(status IN ('draft','accepted')),
 version INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS source_mapping (
 id INTEGER PRIMARY KEY AUTOINCREMENT, sku TEXT REFERENCES product(sku),
 source_system TEXT NOT NULL, external_reference TEXT NOT NULL,
 source_description TEXT NOT NULL, is_primary INTEGER NOT NULL DEFAULT 0,
 UNIQUE(sku,source_system)
);
CREATE TABLE IF NOT EXISTS change_request (
 id INTEGER PRIMARY KEY AUTOINCREMENT, sku TEXT NOT NULL REFERENCES product(sku),
 kind TEXT NOT NULL CHECK(kind IN ('reclassification','attributes','dimensions')),
 actor TEXT NOT NULL, department TEXT NOT NULL, reason TEXT NOT NULL,
 payload TEXT NOT NULL, expected_version INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
 reviewer TEXT, decision_note TEXT, created_at TEXT NOT NULL, decided_at TEXT
);
CREATE TABLE IF NOT EXISTS audit_event (
 id INTEGER PRIMARY KEY AUTOINCREMENT, sku TEXT NOT NULL, event_type TEXT NOT NULL,
 actor TEXT NOT NULL, change_request_id INTEGER, previous_value TEXT, next_value TEXT,
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS metric_observation (
 id INTEGER PRIMARY KEY AUTOINCREMENT, sku TEXT NOT NULL REFERENCES product(sku),
 metric_code TEXT NOT NULL, observation_value REAL,
 unit TEXT NOT NULL, period_start TEXT, period_end TEXT, source_system TEXT NOT NULL,
 source_revision TEXT NOT NULL, as_of TEXT NOT NULL,
 UNIQUE(sku,metric_code,period_start,period_end,source_revision)
);
CREATE INDEX IF NOT EXISTS idx_product_node ON product(classification_node_id);
CREATE INDEX IF NOT EXISTS idx_requests_status ON change_request(status);
CREATE INDEX IF NOT EXISTS idx_metrics_sku ON metric_observation(sku);
'''


def initialize(path=DEFAULT_PATH):
    with connect(path) as cn:
        cn.executescript(SCHEMA)
        if cn.execute('SELECT 1 FROM classification_node LIMIT 1').fetchone():return
        nodes=create_nodes()
        for n in nodes:
            cn.execute('INSERT INTO classification_node(id,code,parent_id,label,level,position) VALUES(?,?,?,?,?,?)',
                (n['id'],n['code'],n['parent_id'],n['label'],n['level'],n['position']))
        root_by_label={n['label']:n for n in nodes if not n['parent_id']}
        for code,label,datatype,unit,options,match,required in SPECS:
            cn.execute('INSERT INTO attribute_definition(code,label,data_type,unit,options) VALUES(?,?,?,?,?)',
                (code,label,datatype,unit,json.dumps(options)))
            for family,root in root_by_label.items():
                if any(k.lower() in family.lower() for k in match):
                    cn.execute('INSERT INTO classification_attribute(node_id,attribute_code,is_required) VALUES(?,?,?)',
                        (root['id'],code,int(required)))
        products=fake_products(nodes)
        stamp='2026-10-31T12:00:00+00:00'
        for i,p in enumerate(products):
            cn.execute('''INSERT INTO product(sku,description,classification_node_id,brand,range_name,sector,lifecycle,business_role,
               source_system,attributes,status,version,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (p['sku'],p['description'],p['classification_node_id'],p['brand'],p['range_name'],p['sector'],p['lifecycle'],
                 p['business_role'],p['source_system'],json.dumps(p['attributes']),p['status'],1,stamp,stamp))
            cn.execute('INSERT INTO source_mapping(sku,source_system,external_reference,source_description,is_primary) VALUES(?,?,?,?,?)',
                (p['sku'],p['source_system'],f"SYS-{(i*31+1717):07d}",p['description'],1))
            if i%4==0:
                cn.execute('INSERT INTO source_mapping(sku,source_system,external_reference,source_description,is_primary) VALUES(?,?,?,?,?)',
                    (p['sku'],'Commerce Portal',f'WEB-{i+10000}',p['description'],0))
            # Source observations are separate from governed master values.
            # Snapshot is fictional and fixed; deliberate missing and zero cases.
            net_qty=None if i%19==0 else (0 if i%23==0 else ((i*17+28)%750)+5)
            observations={
              'net_sales_qty_90d':net_qty,
              'stock_available':None if i%31==0 else ((i*13+11)%340),
              'open_demand_30d':None if i%29==0 else ((i*11+7)%140),
              'inbound_supply_30d':None if i%37==0 else ((i*3+15)%110),
              'net_sales_amount_90d':None if net_qty is None else round(net_qty*[3.2,6.7,9.5,14.2][i%4],2),
              'gross_margin_amount_90d':None if i%13==0 or net_qty is None else round(net_qty*[0.8,1.7,2.4,3.6][i%4],2)
            }
            for code,val in observations.items():
                if val is None:continue
                unit='EUR' if 'amount' in code else 'units'
                period_start='2026-08-03' if '90d' in code else '2026-10-31'
                period_end='2026-10-31' if '90d' in code else '2026-11-30'
                source='Finance Analytics' if unit=='EUR' else ('Sales Ledger' if 'sales' in code else 'Inventory Operations')
                cn.execute('''INSERT INTO metric_observation(sku,metric_code,observation_value,unit,
                   period_start,period_end,source_system,source_revision,as_of) VALUES(?,?,?,?,?,?,?,?,?)''',
                   (p['sku'],code,val,unit,period_start,period_end,source,'synthetic-snapshot-v1',stamp))

        # A real queued cross-functional dispute: product never auto-updates.
        sample=products[9]
        parent=next(n['parent_id'] for n in nodes if n['id']==sample['classification_node_id'])
        alternatives=[n for n in nodes if n['parent_id']==parent and n['id']!=sample['classification_node_id']]
        # A sibling category shares the same family-level required metadata.
        target=alternatives[0] if alternatives else next(n for n in nodes if n['id']==sample['classification_node_id'])
        cn.execute('''INSERT INTO change_request(sku,kind,actor,department,reason,payload,expected_version,status,created_at)
          VALUES(?,?,?,?,?,?,?,?,?)''',(sample['sku'],'reclassification','alex.sales','Commercial',
          'Review whether this SKU should follow the proposed product grouping before publishing the next catalogue release.',
          json.dumps({'target_node_id':target['id']}),1,'pending',stamp))
        cn.execute('''INSERT INTO audit_event(sku,event_type,actor,previous_value,next_value,created_at)
          VALUES(?,?,?,?,?,?)''',(sample['sku'],'catalogue_import','demo-seed',None,json.dumps({'version':1}),stamp))
