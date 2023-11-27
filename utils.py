import os
import json
import traceback

from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns



def load_data(data_path):
    data = []
    with open(data_path) as f:
        for line in f.readlines():
            D = json.loads(line)
            data.append(D)
    return data


def save_data(data, data_path):
    with open(data_path, 'w') as f:
        for D in data:
            f.write(json.dumps(D) + '\n')


def gather_llm_output(data_path, gathered_data_path):
    gathered_data = []
    for file in os.listdir(data_path):
        file_path = os.path.join(data_path, file)
        if os.path.isfile(file_path):
            D = json.load(open(file_path))
        gathered_data.append(D)

    with open(gathered_data_path, 'w') as f:
        for D in gathered_data:
            f.write(json.dumps(D) + '\n')



def is_word_boundary(text, index):
    if index == 0 or index == len(text):
        return True
    if not text[index-1].isalpha() and text[index].isalpha():
        return True
    if text[index].isalpha() and not text[index+1].isalpha():
        return True
    return False


def find_word_positions(text, entity_name, true_entity_set):
    start = 0
    while start < len(text):
        start = text.find(entity_name, start)
        if start == -1:
            return None
        end = start + len(entity_name) - 1
        if is_word_boundary(text, start) and is_word_boundary(text, end):
            if [start, end] not in true_entity_set:
                return [start, end]
        start += len(entity_name)
        

def calibrate_position(data):
    new_data = {
        'id': data['id'],
        'text': data['text'],
        'gold': data['gold'],
        'pred': {
            'entities': {},
            'relations': {},
        }
    }
    text = data['text']
    # data['pred']['entities']
    # data['pred']['relations']
    original_entity_map = {}
    # entity
    for entity_type in data['pred']['entities']:
        new_data['pred']['entities'][entity_type] = []
        true_entity_set = []
        for entity in data['pred']['entities'][entity_type]:
            entity_name = entity[0]
            old_position = tuple(entity[1].copy())
            if find_word_positions(text, entity_name, true_entity_set) == None:
                continue
            new_position = find_word_positions(text, entity_name, true_entity_set)
            
            # update
            original_entity_map[old_position] = new_position.copy()
            true_entity_set.append(new_position)

            new_data['pred']['entities'][entity_type].append([entity_name, new_position])

    # relation
    for relation_type in data['pred']['relations']:
        new_data['pred']['relations'][relation_type] = []
        for relation in data['pred']['relations'][relation_type]:
            if len(relation) != 2:
                continue
            subject, object = relation
            if len(subject) != 2 or len(object) != 2:
                continue
            subject_name, subject_position = subject
            object_name, object_position = object
            subject_position = tuple(subject_position.copy())
            object_position = tuple(object_position.copy())


            if subject_position not in original_entity_map or object_position not in original_entity_map:
                continue

            new_data['pred']['relations'][relation_type].append([
                [subject_name, original_entity_map[subject_position].copy()],
                [object_name, original_entity_map[object_position].copy()]
            ])

    return new_data


def get_pred_gold_from_scatterd_data(data_path):
    pred, gold = [], []
    for file in os.listdir(data_path):
        file_path = os.path.join(data_path, file)
        if os.path.isfile(file_path):
            D = json.load(open(file_path))
        D = calibrate_position(D)
        pred.append(D['pred'])
        gold.append(D['gold'])
    return pred, gold


def judge_same(range_1, range_2):
    a, b = range_1
    c, d = range_2
    if a == c and b == d:
        return True
    else:
        return False


def judge_overlapped(range_1, range_2):
    a, b = range_1
    c, d = range_2
    if b >= c and a <= d:
        return True
    else:
        return False


def calculate_entity_exact_match_number(pred_entities, gold_entities, p_r):
    if p_r == 'p':
        tmp = pred_entities
        pred_entities = gold_entities
        gold_entities = tmp
    elif p_r == 'r':
        pass
    cnt = 0
    for g in gold_entities:
        for p in pred_entities:
            if judge_same(p[1], g[1]) or p[0].lower() == g[0].lower():
                cnt += 1
                break
    return cnt


def calculate_entity_relaxed_match_number(pred_entities, gold_entities, p_r):
    if p_r == 'p':
        tmp = pred_entities
        pred_entities = gold_entities
        gold_entities = tmp
    elif p_r == 'r':
        pass
    cnt = 0
    for g in gold_entities:
        for p in pred_entities:
            if judge_overlapped(p[1], g[1]) or p[0].lower() == g[0].lower():
                cnt += 1
                break
    return cnt


def calculate_relation_exact_match_number(pred_relations, gold_relations, p_r):
    if p_r == 'p':
        tmp = pred_relations
        pred_relations = gold_relations
        gold_relations = tmp
    elif p_r == 'r':
        pass
    cnt = 0
    for g in gold_relations:
        for p in pred_relations:
            try:
                if (judge_same(p[0][1], g[0][1]) and judge_same(p[1][1], g[1][1]) ) or ( p[0][0].lower() == g[0][0].lower() and p[1][0].lower() == g[1][0].lower()):
                    cnt += 1
                    break
            except Exception as e:
                print('Unparsable Model Output!')
                traceback.print_exc()
                continue
    return cnt


def calculate_relation_relaxed_match_number(pred_relations, gold_relations, p_r):
    if p_r == 'p':
        tmp = pred_relations
        pred_relations = gold_relations
        gold_relations = tmp
    elif p_r == 'r':
        pass
    cnt = 0
    for g in gold_relations:
        for p in pred_relations:
            try:
                if (judge_overlapped(p[0][1], g[0][1]) and judge_overlapped(p[1][1], g[1][1]) ) or ( p[0][0].lower() == g[0][0].lower() and p[1][0].lower() == g[1][0].lower()):
                    cnt += 1
                    break
            except Exception as e:
                print('Unparsable Model Output!')
                traceback.print_exc()
                continue
    return cnt


def evaluate(pred, gold):
    scores = {
        'exact': {
            'disease': {}, 'rare_disease': {}, 'symptom_and_sign': {}, 'anaphor': {}, 'entity_overall': {},
            'produces': {}, 'increases_risk_of': {}, 'is_a': {}, 'is_acron': {}, 'is_synon': {}, 'anaphora': {}, 'relation_overall': {},
            'overall': {'precision': 0., 'recall': 0., 'f1': 0.}
        },
        'relaxed': {
            'disease': {}, 'rare_disease': {}, 'symptom_and_sign': {}, 'anaphor': {}, 'entity_overall': {},
            'produces': {}, 'increases_risk_of': {}, 'is_a': {}, 'is_acron': {}, 'is_synon': {}, 'anaphora': {}, 'relation_overall': {},
            'overall': {'precision': 0., 'recall': 0., 'f1': 0.}
        }
    }
    for match_level in ['exact', 'relaxed']:
        # entity
        TP_p = {'overall': 0, 'disease': 0, 'rare_disease': 0, 'symptom_and_sign': 0, 'anaphor': 0, 'entity_overall': 0,
                'produces': 0, 'increases_risk_of': 0, 'is_a': 0, 'is_acron': 0, 'is_synon': 0, 'anaphora': 0, 'relation_overall': 0}
        TP_r = {'overall': 0, 'disease': 0, 'rare_disease': 0, 'symptom_and_sign': 0, 'anaphor': 0, 'entity_overall': 0,
                'produces': 0, 'increases_risk_of': 0, 'is_a': 0, 'is_acron': 0, 'is_synon': 0, 'anaphora': 0, 'relation_overall': 0}
        TP_FP = {'overall': 0, 'disease': 0, 'rare_disease': 0, 'symptom_and_sign': 0, 'anaphor': 0, 'entity_overall': 0,
                'produces': 0, 'increases_risk_of': 0, 'is_a': 0, 'is_acron': 0, 'is_synon': 0, 'anaphora': 0, 'relation_overall': 0}
        TP_FN = {'overall': 0, 'disease': 0, 'rare_disease': 0, 'symptom_and_sign': 0, 'anaphor': 0, 'entity_overall': 0,
                'produces': 0, 'increases_risk_of': 0, 'is_a': 0, 'is_acron': 0, 'is_synon': 0, 'anaphora': 0, 'relation_overall': 0}
        for p, g, in zip(pred, gold):
            for entity_type in p['entities']:
                pred_entities = p['entities'][entity_type]
                gold_entities = g['entities'][entity_type]
                if match_level == 'exact':
                    num_p = calculate_entity_exact_match_number(pred_entities, gold_entities, p_r='p')
                    num_r = calculate_entity_exact_match_number(pred_entities, gold_entities, p_r='r')
                elif match_level == 'relaxed':
                    num_p = calculate_entity_relaxed_match_number(pred_entities, gold_entities, p_r='p')
                    num_r = calculate_entity_relaxed_match_number(pred_entities, gold_entities, p_r='r')
                TP_p[entity_type] += num_p
                TP_p['entity_overall'] += num_p
                TP_r[entity_type] += num_r
                TP_r['entity_overall'] += num_r
                TP_FP[entity_type] += len(pred_entities)
                TP_FN[entity_type] += len(gold_entities)
                TP_FP['entity_overall'] += len(pred_entities)
                TP_FN['entity_overall'] += len(gold_entities)

        # relation
        for p, g, in zip(pred, gold):
            for relation_type in p['relations']:
                
                # if relation_type == 'anaphora':
                    # print()
                    # print(p['relations'][relation_type])
                    # print(g['relations'][relation_type])
                
                pred_relations = p['relations'][relation_type]
                gold_relations = g['relations'][relation_type]
                if match_level == 'exact':
                    num_p = calculate_relation_exact_match_number(pred_relations, gold_relations, p_r='p')
                    num_r = calculate_relation_exact_match_number(pred_relations, gold_relations, p_r='r')
                elif match_level == 'relaxed':
                    num_p = calculate_relation_relaxed_match_number(pred_relations, gold_relations, p_r='p')
                    num_r = calculate_relation_relaxed_match_number(pred_relations, gold_relations, p_r='r')
                TP_p[relation_type] += num_p
                TP_p['relation_overall'] += num_p
                TP_r[relation_type] += num_r
                TP_r['relation_overall'] += num_r
                TP_FP[relation_type] += len(pred_relations)
                TP_FN[relation_type] += len(gold_relations)
                TP_FP['relation_overall'] += len(pred_relations)
                TP_FN['relation_overall'] += len(gold_relations)

        for key in scores[match_level]:
            if key == 'overall':
                continue
            scores[match_level][key]['precision'] = TP_p[key] / TP_FP[key] if TP_FP[key] else 0.
            scores[match_level][key]['recall'] = TP_r[key] / TP_FN[key] if TP_FN[key] else 0.
            precision_recall = scores[match_level][key]['precision'] + scores[match_level][key]['recall']
            scores[match_level][key]['f1'] = 2 * scores[match_level][key]['precision'] * scores[match_level][key]['recall'] / precision_recall if precision_recall else 0.
        for m in scores[match_level]['overall']:
            scores[match_level]['overall'][m] = (scores[match_level]['entity_overall'][m] + scores[match_level]['relation_overall'][m]) / 2
    return scores


def printout_result(scores, match_level):
    # exact or relaxed
    print('############', match_level, '#############')
    print('Entity:')
    print('rare_disease:', scores[match_level]['rare_disease'])
    print('disease:', scores[match_level]['disease'])
    print('symptom_and_sign:', scores[match_level]['symptom_and_sign'])
    print('anaphor:', scores[match_level]['anaphor'])
    print('entity_overall:', scores[match_level]['entity_overall'])
    print('\nRelation:')
    print('produces', scores[match_level]['produces'])
    print('increases_risk_of', scores[match_level]['increases_risk_of'])
    print('is_a', scores[match_level]['is_a'])
    print('is_acron', scores[match_level]['is_acron'])
    print('is_synon', scores[match_level]['is_synon'])
    print('anaphora:', scores[match_level]['anaphora'])
    print('relation_overall:', scores[match_level]['relation_overall'])
    print('\nOverall:')
    print('overall:', scores[match_level]['overall'])
    print('#################################')


def prepare_confusion_matrix_data(pred, gold, match_level):
    # exact, relaxed
    new_pred, new_gold, labels = [], [], []
    return new_pred, new_gold, labels
    

def get_confusion_matrix(pred, gold, labels):
    cm = confusion_matrix(gold, pred)
    plt.figure(figsize=(10,7))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.show()


