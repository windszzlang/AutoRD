import json
import os



data = []
with open('data/RareDis2023/test.jsonl') as f:
    for line in f.readlines():
        D = json.loads(line)
        data.append(D)


rare_disease_map = {}
with open('data/raredisease_phenotype_triples.json') as f:
    triples = json.load(f)
for triple in triples:
    for name in triple['source']['name']:
        rare_disease_map[name.lower()] = triple['source']['id']


ontology = []
all_terms = []
with open('data/rare_disease_ontology.jsonl') as f:
    for line in f.readlines():
        obj = json.loads(line)
        ontology.append(obj)
        all_terms.append(obj['name'].lower())
        # for name in obj['name']:
            # all_terms.append(name.lower())


rare_disease = []

for D in data:
    # for entity_type in D['entities']:
        # rare_disease.extend(D['entities'][entity_type])
    rare_disease.extend(D['entities']['Rare disease'])


cnt, total = 0, 0
for rd in rare_disease:
    if rd.lower() in all_terms:
    # if rd.lower() in rare_disease_map.keys():
        cnt += 1
    else:
        print(rd)
        # input()
    total += 1

print(cnt / total)