import json
import sys
import datetime
import config
import socket
import traceback
import urllib3
import json
import logging
from datetime import datetime
from datetime import timedelta
from elasticsearch import Elasticsearch

urllib3.disable_warnings()
es = Elasticsearch(config.es_connection, verify_certs=False)

logger = logging.getLogger('helpers')

def pprint(r):
    s = json.dumps(r, indent=2, sort_keys=True)
    return(s)

def getValue(path, source):
    p = path.split('.')
    if p[0] in source:
        if len(p) > 1:
            return getValue('.'.join(p[1:]), source[p[0]])
        else:
            if p[0] == 'ip':
                return source[p[0]][0]
            else:
                return source[p[0]]
    else:
        return None

def getQuery(query, size="5000", index="redirtraffic-*"):
    q3 = {'query': {'query_string': {'query': query}}}
    r3 = es.search(index=index, body=q3, size=size)
    if(r3['hits']['total']['value'] == 0):
        return(None)
    return(r3['hits']['hits'])

def countQuery(query, index="redirtraffic-*"):
    print('count')
    q3 = {'query': {'query_string': {'query': query}}}
    r3 = es.search(index=index, body=q3, size=0)
    return(r3['hits']['total']['value'])

# Sets tag to all objects in lst
def setTags(tag, lst):
    for l in lst:
        if 'tags' in l['_source'] and tag not in l['_source']['tags']:
            l['_source']['tags'].append(tag)
        else:
            l['_source']['tags'] = [tag]
        r = es.update(index=l['_index'], id=l['_id'], body={'doc': l['_source']})

# Adds alarm extra data to the source doc in ES
def addAlarmData(doc, data, alarm_name):
    doc['_source']['alarm'] = {
        'timestamp': datetime.utcnow().isoformat(),
        alarm_name: data
    }
    r = es.update(index=doc['_index'], id=doc['_id'], body={'doc': doc['_source']})

# Takes a list of hits and a list of field names (dot notation) and returns a grouped list
def groupHits(hits, groupby, res=None):
    if(len(groupby) > 0):
        lHits = dict()
        # First time in the loop
        if res is None:
            for h in hits:
                v = getValue('_source.%s' % groupby[0], h)
                if v in lHits:
                    lHits[v].append(h)
                else:
                    lHits[v] = [h]
        else:
            for key, val in res.items():
                for h in val:
                    v = getValue('_source.%s' % groupby[0], h)
                    tmpKey = '%s / %s' % (key, v)
                    if tmpKey in lHits:
                        lHits[tmpKey].append(h)
                    else:
                        lHits[tmpKey] = [h]
        groupby.pop(0)
        return(groupHits(hits, groupby, lHits))
    else:
        if res is None:
            return hits
        else:
            tmpHits = []
            for k, v in res.items():
#                v[0]['_groupby'] = k
                tmpHits.append(v[0])
            return tmpHits


initial_alarm_result = {
    'info': {
        'version': 0.0,
        'name': 'unknown',
        'alarmmsg': 'unkown',
        'description': 'unknown',
        'type': 'redelk_alarm',
        'submodule': 'unknown'
    },
    'hits': {
        'hits': [],
        'total': 0
    },
    'mutations': {},
    'fields': ['host.name', 'user.name', '@timestamp', 'c2.message'],
    'groupby': []
}
