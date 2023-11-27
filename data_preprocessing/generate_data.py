import os
import json
import numpy as np
from tqdm import tqdm



def load_data(data_path):
    data = {}
    for file in tqdm(os.listdir(data_path)):
        file_path = os.path.join(data_path, file)
        if os.path.isfile(file_path):
            if file_path.endswith('.txt') or file_path.endswith('.ann'):
                rd = file_path.split('/')[-1].split('.')[0]
                if rd not in data:
                    data[rd] = {
                        'id': rd,
                        'text': '',
                        'gold': {
                            'entities': {
                                'disease': [],
                                'rare_disease': [],
                                'symptom_and_sign': [],
                                'anaphor': [],
                            },
                            'relations': {
                                'produces': [],
                                'increases_risk_of': [],
                                'is_a': [],
                                'is_acron': [],
                                'is_synon': [],
                                'anaphora': []
                            }
                        }
                    }
                with open(file_path) as f:
                    if file_path.endswith('.txt'):
                        data[rd]['text'] = f.read().strip()
                    if file_path.endswith('.ann'):
                        tmp_entity_map = {}
                        
                        # print(file_path)
                        for i, line in enumerate(f.readlines()):
                            if line[0] == 'T':
                                line = line.strip()

                                entity_type, entity_start, entity_end = line.split('\t')[1].split()
                                entity = line.split('\t')[2]
                                # [start, end]
                                entity_start = int(entity_start)
                                entity_end = int(entity_end) - 1
                                item = (entity, (entity_start, entity_end))
                                tmp_entity_map['T' + str(i + 1)] = item
                                if entity_type == 'DISEASE':
                                    data[rd]['gold']['entities']['disease'].append(item)
                                elif entity_type == 'RAREDISEASE' or entity_type == 'SKINRAREDISEASE':
                                    data[rd]['gold']['entities']['rare_disease'].append(item)
                                elif entity_type == 'SYMPTOM' or entity_type == 'SIGN':
                                    data[rd]['gold']['entities']['symptom_and_sign'].append(item)
                                elif entity_type == 'ANAPHOR':
                                    data[rd]['gold']['entities']['anaphor'].append(item)
                                else:
                                    print(entity_type)
                            elif line[0] == 'R':
                                line = line.strip()

                                relation_type, subject, object = line.split('\t')[1].split()
                                subject = subject.split(':')[1]
                                object = object.split(':')[1]

                                item = (tmp_entity_map[subject], tmp_entity_map[object])

                                if relation_type == 'Produces':
                                    data[rd]['gold']['relations']['produces'].append(item)
                                elif relation_type == 'Increases_risk_of':
                                    data[rd]['gold']['relations']['increases_risk_of'].append(item)
                                elif relation_type == 'Is_a':
                                    data[rd]['gold']['relations']['is_a'].append(item)
                                elif relation_type == 'Is_acron':
                                    data[rd]['gold']['relations']['is_acron'].append(item)
                                elif relation_type == 'Is_synon':
                                    data[rd]['gold']['relations']['is_synon'].append(item)
                                elif relation_type == 'Anaphora':
                                    data[rd]['gold']['relations']['anaphora'].append(item)
                                else:
                                    print(relation_type)
                        # for key in data[rd]['entities']:
                            # data[rd]['entities'][key] = list(set(data[rd]['entities'][key]))
            else:
                continue

    data = list(data.values())
    return data



if __name__ == '__main__':
    train_data = load_data('data/RareDis-fixed/train')
    valid_data = load_data('data/RareDis-fixed/dev')
    test_data = load_data('data/RareDis-fixed/test')
    
    data = []
    data.extend(train_data)
    data.extend(valid_data)
    data.extend(test_data)

    # shuffle
    np.random.seed(42)
    np.random.shuffle(data)

    # ratio
    train_ratio = 0.6
    
    train_size = int(train_ratio * len(data))
    valid_size = int((1-train_ratio)/2 * len(data))

    train_data, valid_data, test_data = data[:train_size], data[train_size:train_size+valid_size], data[train_size+valid_size:]



    # with open('data/RareDis2023.jsonl', 'w') as f:
        # for D in data:
            # f.write(json.dumps(D) + '\n')

    with open('data/RareDis2023/train.jsonl', 'w') as f:
        for D in train_data:
            f.write(json.dumps(D) + '\n')
    with open('data/RareDis2023/valid.jsonl', 'w') as f:
        for D in valid_data:
            f.write(json.dumps(D) + '\n')
    with open('data/RareDis2023/test.jsonl', 'w') as f:
        for D in test_data:
            f.write(json.dumps(D) + '\n')
