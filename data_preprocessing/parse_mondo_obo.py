import json
import re


term_list = []


with open('data/mondo.obo', 'r') as f:
    current_term = None
    for line in f.readlines():
        line = line.strip()
        # print(current_term)
        if line.startswith('[Term]'):
            current_term = {'synonym': []}
        elif current_term is not None:
            if line == '':
                term_list.append(current_term)
                current_term = None
            else:
                key, value = line.split(': ', 1)
                if key == 'synonym':
                    pattern = re.compile(r'"(.*?)"')
                    value = pattern.search(value).group(1)
                    current_term[key].append(value)
                elif key == 'def':
                    pattern = re.compile(r'"(.*?)"')
                    value = pattern.search(value).group(1)
                    current_term[key] = value
                else:
                    current_term[key] = value


if current_term:
    term_list.append(current_term)



new_term_list = []



for term in term_list:
    name = [term['name']]
    for sy in term['synonym']:
        if sy not in name:
            name.append(sy)
    new_term = {
        'id': term['id'],
        'name': name,
        'definition': term['def'] if 'def' in term else ''
    }
    new_term_list.append(new_term)
    # print(new_term)
    # break



with open('data/ontology.jsonl', 'w') as f:
    for D in new_term_list:
        f.write(json.dumps(D) + '\n')



