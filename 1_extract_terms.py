import re
from tqdm import tqdm

from utils import *



test_data = load_data('data/RareDis2023/test.jsonl')
new_data = []


def term_exist(term, text):
    # add negator detector
    negators = ['no', 'not', 'never', 'none', 'nobody', 'nothing', 'neither', 'nowhere', 'cannot']

    negator_pattern = r'(' + '|'.join(map(re.escape, negators)) + r')\s*\b{}\b'.format(re.escape(term))
    term_pattern = r'\b{}\b'.format(re.escape(term))

    combined_pattern = r'({})|({})'.format(negator_pattern, term_pattern)

    regex = re.compile(combined_pattern, re.IGNORECASE)

    match = regex.search(text)
    if match:
        return match.group(0)
    else:
        return False


ontology = []
term_mapping = {} # keys(): terms
with open('data/ontology.jsonl') as f:
    for line in f.readlines():
        obj = json.loads(line)
        ontology.append(obj)
        for name in obj['name']:
            term_mapping[name] = obj['definition']


cnt = 0
total = 0



for D in tqdm(test_data):
    text = D['text']
    flag = True
    total += 1
    medical_terms = []
    for term in term_mapping:
        matched_term = term_exist(term, text)
        if matched_term:
            if flag: # count
                cnt += 1
                flag = False

            medical_terms.append([matched_term, term_mapping[term]])

    D['cache'] = {'step1': {
        'medical_terms': medical_terms
    }}
    new_data.append(D)


print(cnt / total)

with open('cache_data/step1_res.jsonl', 'w') as f:
    for D in new_data:
        f.write(json.dumps(D) + '\n')
