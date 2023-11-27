import torch
from torch import nn
import torch.nn.functional as F

from utils import *



class Network(nn.Module):
    def __init__(self, bert_model, entity_id2label, relation_id2label):
        super().__init__()
        ## basic
        self.bert_model = bert_model # PLM
        # self.top_k = top_k
        self.plm_config = self.bert_model.config
        self.entity_id2label = entity_id2label
        self.relation_id2label = relation_id2label
        self.max_seq_len = 512
        self.device = self.bert_model

        self.dropout = nn.Dropout(0.2)
        self.token_classifier = nn.Linear(self.plm_config.hidden_size, len(entity_id2label))
        self.relation_classifier = nn.Linear(2 * self.plm_config.hidden_size, len(relation_id2label))

        self.alpha = 0.2
        self.criterion = nn.BCEWithLogitsLoss()


    def forward(self, input_ids, attention_mask):
        batch_size = input_ids.size()[0]

        last_hidden_state = self.bert_model(input_ids, attention_mask, return_dict=True)['last_hidden_state'] # [batch_size, seq_len, hidden_size]
        text_embeddings = self.dropout(last_hidden_state) # dim=[batch_size, seq_len, hidden_size]

        logits_entity = self.token_classifier(text_embeddings)

        return logits_entity, text_embeddings


    def compute_loss(self, batch_data):
        self.train()
        logits_entity, text_embeddings = self(batch_data['input_ids'], batch_data['attention_mask'])
        loss_entity = self.criterion(logits_entity, batch_data['entity_labels'])


        if batch_data['relation_labels'].size()[0] == 0:
            loss_relation = 0
        else:
            relation_embeddings = []
            for i, entity_pairs in enumerate(batch_data['entity_pairs']):
                for entity_pair in entity_pairs:
                    subject, object = entity_pair
                    subject_embedding = torch.mean(text_embeddings[i, subject[0]:subject[-1]+1, :], dim=0)  # dim=[hidden_size]
                    object_embedding = torch.mean(text_embeddings[i, object[0]:object[-1]+1, :], dim=0)  # dim=[hidden_size]
                    relation_embedding = torch.cat([subject_embedding, object_embedding])  # dim=[hidden_size*2]
                    relation_embeddings.append(relation_embedding)
            relation_embeddings = torch.stack(relation_embeddings, dim=0)  # dim=[num, hidden_size*2]

            logits_relation = self.relation_classifier(relation_embeddings)
            loss_relation = self.criterion(logits_relation, batch_data['relation_labels']) / text_embeddings.size()[0]

        # loss = self.alpha * loss_entity + (1 - self.alpha) * loss_relation
        loss = loss_entity + loss_relation
        # print(loss_relation)
        return loss


    def predict(self, batch_data):
        self.eval()
        logits_entity, text_embeddings = self(batch_data['input_ids'], batch_data['attention_mask'])     
        
        # entity
        probabilities = F.softmax(logits_entity, dim=-1)
        predictions = torch.argmax(probabilities, dim=-1)
        bio_tags = []
        for pred in predictions:
            tmp_tags = []
            for p in pred:
                tmp_tags.append(self.entity_id2label[p.item()])
            bio_tags.append(tmp_tags)

        predicted_entities = []
        for i in range(len(bio_tags)):
            tmp_entities = extract_entities(bio_tags[i], batch_data['tokenized_text'][i], batch_data['text'][i])
            predicted_entities.append(tmp_entities)

        # relation
        predicted_relations = []
        for data_i in range(len(predicted_entities)):

            # test
            # predicted_relations.append([])
            # continue

            entity_set = []
            for key in predicted_entities[data_i]:
                entity_set.extend(predicted_entities[data_i][key])

            entity_pairs = []
            x_y = [] # relocate e_1, e_2
            for i in range(len(entity_set)):
                for j in range(len(entity_set)):
                    if i != j:
                        x_y.append([i, j])
                        # char2token
                        s_span = entity_set[i][1]
                        o_span = entity_set[j][1]
                        subject_token_position = char_to_token_position([s_span], batch_data['tokenized_text'][data_i], batch_data['text'][data_i])
                        object_token_position = char_to_token_position([o_span], batch_data['tokenized_text'][data_i], batch_data['text'][data_i])
                        entity_pairs.append([subject_token_position[0], object_token_position[0]])

            relation_embeddings = []
            for entity_pair in entity_pairs:
                subject, object = entity_pair
                subject_embedding = torch.mean(text_embeddings[data_i, subject[0]:subject[-1]+1, :], dim=0)  # dim=[hidden_size]
                object_embedding = torch.mean(text_embeddings[data_i, object[0]:object[-1]+1, :], dim=0)  # dim=[hidden_size]
                relation_embedding = torch.cat([subject_embedding, object_embedding])  # dim=[hidden_size*2]
                relation_embeddings.append(relation_embedding)

            rs = ['produces', 'increases_risk_of', 'is_a', 'is_acron', 'is_synon', 'anaphora']
            tmp_pred_relations = {r:[] for r in rs}
            if relation_embeddings != []:
                relation_embeddings = torch.stack(relation_embeddings, dim=0)  # dim=[num, hidden_size*2]

                logits_relation = self.relation_classifier(relation_embeddings)
                probabilities = F.softmax(logits_relation, dim=-1)
                predictions = torch.argmax(probabilities, dim=-1)
                
                for i, pred in enumerate(predictions):
                    if self.relation_id2label[pred.item()] != 'none':
                        tmp_pred_relations[self.relation_id2label[pred.item()]].append([entity_set[x_y[i][0]], entity_set[x_y[i][1]]])

            predicted_relations.append(tmp_pred_relations)

        self.train()
        results = []
        for e, r in zip(predicted_entities, predicted_relations):
            results.append({
                'entities': e,
                'relations': r,
            })
        return results