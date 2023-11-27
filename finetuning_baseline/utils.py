import json
import torch
import os
import random
import numpy as np
import json
import traceback



def seed_everything(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  
    np.random.seed(seed)
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    torch.manual_seed(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True



def load_data(data_path, tokenizer=None, load_part=None, few_shot=None):
    data = []
    with open(data_path) as f:
        for i, line in enumerate(f.readlines()):
            if load_part != None and i + 1 > load_part:
                break
            D = json.loads(line)
            data.append(D)
    if few_shot:
        data = random.sample(data, few_shot)
    return data



def get_label_id_map(labels):
    id2label = dict(enumerate(labels))
    label2id = {label: id for id, label in id2label.items()}
    label_num = len(labels)
    return id2label, label2id, label_num


 # auto filter words appear in the overlength area
def char_to_token_position(char_positions, tokenized_text, original_text):
    '''calculate token position
    char_positions: [[0,3],[6,10]], must be ordered
    tokenized_text: ['[CLS]', 'chromosome', '7', ',', 'partial', 'mon', '##oso', '##my', '[SEP]']
    original_text: 'chromosome 7, partial monosomy...'
    '''
    if char_positions == []:
        return []
    current_char_pos = 0
    j = 0
    token_positions = [] # [[span1],[span2]]
    tmp_pos = []
    save_pos = False
    for i, token in enumerate(tokenized_text):
        if token == '[CLS]' or token == '[SEP]':
            continue

        if char_positions[j][0] <= current_char_pos and current_char_pos <= char_positions[j][1]:
            tmp_pos.append(i)
            save_pos = True

        token_length = len(token.replace('##', ''))  # '##' denotes subwords
        current_char_pos += token_length
        # skip spaces in the original text to align with token positions
        while current_char_pos < len(original_text) and original_text[current_char_pos].isspace():
            current_char_pos += 1

        if current_char_pos > char_positions[j][1]:
            j += 1
            if save_pos:
                token_positions.append(tmp_pos)
                tmp_pos = []
                save_pos = False
                
        if j >= len(char_positions):
            break
    return token_positions


# BIO
def extract_entities(bio_tags, tokenized_text, original_text, labels=['rare_disease', 'disease', 'symptom_and_sign', 'anaphor']):
    entities = {label: [] for label in labels}
    current_entity = []
    current_span = [0, 0] # .copy
    current_type = None

    current_token_pos = [-1, -1]

    for token, tag in zip(tokenized_text, bio_tags):
        if token == '[CLS]' or token == '[SEP]':
            continue
        # get token span
        current_token_pos[0] = current_token_pos[1] + 1
        while current_token_pos[0] < len(original_text) and original_text[current_token_pos[0]].isspace():
            current_token_pos[0] += 1
        current_token_pos[1] = current_token_pos[0] + len(token.replace('##', '')) - 1

        if tag.startswith('B-'):
            if current_entity:
                entities[current_type].append([original_text[current_span[0]:current_span[1]+1], current_span.copy()])
            
            current_entity = [token]
            current_type = tag.split('-')[1]
            current_span = current_token_pos.copy()
        elif tag.startswith('I-') and current_type is not None:
            if current_type == tag.split('-')[1]:
                current_entity.append(token)
                current_span[1] = current_token_pos[1]
            else:
                # I- tag not matching B- tag, treat as a new entity
                entities[current_type].append([original_text[current_span[0]:current_span[1]+1], current_span.copy()])
                current_entity = [token]
                current_type = tag.split('-')[1]
                current_span = current_token_pos.copy()
        else:
            if current_entity:
                entities[current_type].append([original_text[current_span[0]:current_span[1]+1], current_span.copy()])
                current_entity = []
                current_type = None
                current_span = [0, 0]
        
        if current_token_pos[1] >= len(original_text):
            break

    # add the last entity if any
    if current_entity:
        entities[current_type].append([original_text[current_span[0]:current_span[1]+1], current_span.copy()])
    return entities


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
            if judge_same(p[1], g[1]) or p[0] == g[0]:
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
            if judge_overlapped(p[1], g[1]) or p[0] == g[0]:
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
                if (judge_same(p[0][1], g[0][1]) and judge_same(p[1][1], g[1][1]) ) or ( p[0] == g[0] and p[1] == g[1]):
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
                if (judge_overlapped(p[0][1], g[0][1]) and judge_overlapped(p[1][1], g[1][1]) ) or ( p[0] == g[0] and p[1] == g[1]):
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


