import json

from utils import *



data = load_data('cache_data/step4_res.jsonl')

triples = []


for D in data:
    cur_relations = D['pred']['relations']
    
    anaphor = {}
    for rel in cur_relations['anaphora']:
        rel = [(r[0], tuple([1])) for r in rel]
        anaphor[rel[1]] = rel[0]


    for relation_type in cur_relations:
        if relation_type == 'anaphora':
            continue
        for rel in cur_relations[relation_type]:
            rel = [(r[0], tuple([1])) for r in rel]
            if rel[0] in anaphor:
                subject = anaphor[rel[0]][0]
            else:
                subject = rel[0][0]
            if rel[1] in anaphor:
                object = anaphor[rel[1]][0]
            else:
                object = rel[1][0]
            predicate = relation_type
            triples.append([subject, predicate, object])



save_data(triples, 'cache_data/step5_res.jsonl')
