import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F

from utils import *



class CustomDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __getitem__(self, idx):
        assert idx < len(self.data)
        return self.data[idx]

    def __len__(self):
        return len(self.data)
    

class CustomCollator():
    def __init__(self, entity_label2id, entity_label_num, relation_label2id, relation_label_num, tokenizer, device, is_predict=False):
        self.max_seq_len = 512
        self.entity_label2id = entity_label2id
        self.entity_label_num = entity_label_num
        self.relation_label2id = relation_label2id
        self.relation_label_num = relation_label_num
        self.tokenizer = tokenizer
        self.device = device
        self.is_predict = is_predict

    def __call__(self, batch_data):

        new_batch_data = {}

        batch_size = len(batch_data)
        batch_text = [D['text'] for D in batch_data]
        new_batch_data['text'] = batch_text

        text_encodings = self.tokenizer(
            batch_text,
            add_special_tokens=True,
            max_length=self.max_seq_len,
            padding='longest',
            return_tensors='pt',
            truncation=True,
            # return_length=True,
        )
        new_batch_data['input_ids'] = text_encodings['input_ids'].to(self.device)
        new_batch_data['attention_mask'] = text_encodings['attention_mask'].to(self.device)
        seq_len = len(new_batch_data['input_ids'][0])

        tokens = [self.tokenizer.convert_ids_to_tokens(ids) for ids in new_batch_data['input_ids']]
        new_batch_data['tokenized_text'] = tokens

        if self.is_predict:
            return new_batch_data

        # entity
        entity_labels = [[self.entity_label2id['O']] * seq_len for i in range(batch_size)]
        for i in range(batch_size):
            for entity_type in batch_data[i]['gold']['entities']:
                char_positions = []
                for name, span in batch_data[i]['gold']['entities'][entity_type]:
                    char_positions.append(span)
                token_positions = char_to_token_position(char_positions, tokens[i], batch_data[i]['text'])
                
                for tmp_pos in token_positions:
                    for j, pos in enumerate(tmp_pos):
                        if j == 0:
                            entity_labels[i][pos] = self.entity_label2id['B-' + entity_type]
                        else:
                            entity_labels[i][pos] = self.entity_label2id['I-' + entity_type]
        entity_labels = torch.tensor(entity_labels).to(self.device)
        new_batch_data['entity_labels'] = F.one_hot(entity_labels, num_classes=len(self.entity_label2id))
        new_batch_data['entity_labels'] = new_batch_data['entity_labels'].float()
        
        # relation
        entity_pairs = []
        relation_labels = []
        for i in range(batch_size):
            tmp_entity_pairs = []
            tmp_relation_labels = []
            entities = []
            for relation_type in batch_data[i]['gold']['relations']:
                for subject, object in batch_data[i]['gold']['relations'][relation_type]:
                    _, s_span = subject
                    _, o_span = object
                    subject_token_position = char_to_token_position([s_span], tokens[i], batch_data[i]['text'])
                    object_token_position = char_to_token_position([o_span], tokens[i], batch_data[i]['text'])
                    if subject_token_position == []:
                        continue
                    else:
                        entities.append(subject_token_position[0])
                    if object_token_position == []:
                        continue
                    else:
                        entities.append(object_token_position[0])
                    tmp_entity_pairs.append([subject_token_position[0], object_token_position[0]])
                    tmp_relation_labels.append(self.relation_label2id[relation_type])
        

            for e_1 in entities:
                for e_2 in entities:
                    if e_1 != e_2 and [e_1, e_2] not in tmp_entity_pairs:
                        tmp_entity_pairs.append([e_1, e_2])
                        tmp_relation_labels.append(self.relation_label2id['none'])
            entity_pairs.append(tmp_entity_pairs)
            relation_labels.extend(tmp_relation_labels)

        new_batch_data['entity_pairs'] = entity_pairs

        if relation_labels == []:
            new_batch_data['relation_labels'] = torch.tensor([]).to(self.device)
        else:
            relation_labels = torch.tensor(relation_labels).to(self.device)
            relation_labels = F.one_hot(relation_labels, num_classes=len(self.relation_label2id))
            new_batch_data['relation_labels'] = relation_labels.float()

        new_batch_data['original_data'] = batch_data
        return new_batch_data


def get_dataloader(data, batch_size, entity_label2id, entity_label_num, relation_label2id, relation_label_num, tokenizer, device, is_shuffle=False, is_predict=False):
    convert_to_features = CustomCollator(entity_label2id, entity_label_num, relation_label2id, relation_label_num, tokenizer, device, is_predict)
    dataset = CustomDataset(data)
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=is_shuffle,
        collate_fn=convert_to_features
    )
    return dataloader