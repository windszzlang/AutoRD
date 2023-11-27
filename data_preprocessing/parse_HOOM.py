import os
import re
import threading
import concurrent.futures
import json
import xml.etree.ElementTree as ET
import requests
from tqdm import tqdm



xml_file_path = 'data/HOOM_en_2.0.owl'



pattern = r'#Orpha:\d+_HP:\d+_Freq:[A-Za-z]+'


tree = ET.parse(xml_file_path)
root = tree.getroot()


matches = []

def find_matches(element):
    for text in element.itertext():
        matches.extend(re.findall(pattern, text))

find_matches(root)


frequency_map = {
    'VF': 'Very frequent (99-80%)',
    'F': 'Frequent (79-30%)',
    'O': 'Occasional (29-5%)',
    'OC': 'Occasional (29-5%)',
    'VR': 'Very rare (<4-1%)'
}


# Excluded (0%)

def build_triples(i):
    file_path = 'cache/parse_HOOM/' + str(i) + '.json'
    match = matches[i]
    rd_id, pt_id, freq = match.replace('#', '').split('_')
    freq = frequency_map[freq.replace('Freq:', '')]

    # Rare Disease Request
    headers = {'apiKey': 'langcao'} # https://api.orphacode.org/#/Definition/list_definition
    rd_response = requests.get(f'https://api.orphacode.org/EN/ClinicalEntity/orphacode/{rd_id.split(":")[-1]}/Name', headers=headers).json()
    rd_names = [rd_response['Preferred term']]
    rd_response = requests.get(f'https://api.orphacode.org/EN/ClinicalEntity/orphacode/{rd_id.split(":")[-1]}/Synonym', headers=headers).json()
    if rd_response['Synonym']:
        rd_names.extend(rd_response['Synonym'])
    rd_response = requests.get(f'https://api.orphacode.org/EN/ClinicalEntity/orphacode/{rd_id.split(":")[-1]}/Definition', headers=headers).json()
    rd_definition = rd_response['Definition']

    # Phenotype Request
    pt_response = requests.get(f'https://hpo.jax.org/api/hpo/term/{pt_id}').json()
    pt_names = pt_response['details']['synonyms']
    pt_names.append(pt_response['details']['name'])
    triple = {
        'source': {
            'id': rd_id,
            'name': rd_names,
            'definition': rd_definition
        },
        'link': {
            'frequency': freq,
        },
        'target': {
            'id': pt_id,
            'name': pt_names,
            'definition': pt_response['details']['definition']
        }
    }
    with open(file_path, 'w') as f:
        json.dump(triple, f)


i_list = []
for i, match in enumerate(tqdm(matches)):
    file_path = 'cache/parse_HOOM/' + str(i) + '.json'
    if not os.path.exists(file_path):
        i_list.append(i)

print('Remaining:', len(i_list) / len(matches))

pool_size = 10

with concurrent.futures.ThreadPoolExecutor(max_workers=pool_size) as executor:
    results = executor.map(build_triples, i_list)


triples = []
for file in os.listdir('cache/parse_HOOM/'):
    file_path = os.path.join('cache/parse_HOOM/', file)
    if os.path.isfile(file_path):
        with open(file_path) as f:
            triple = json.load(f)
        triples.append(triple)



with open('data/raredisease_phenotype_triples.jsonl', 'w') as f:
    for t in triples:
        f.write(json.dumps(t) + '\n')