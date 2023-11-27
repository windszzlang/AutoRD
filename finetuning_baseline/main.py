from utils import *
from dataloader import get_dataloader
from network import *

import torch
from transformers import AutoTokenizer, AutoModel
from tqdm import tqdm
import random



os.environ["CUDA_VISIBLE_DEVICES"] = '7'

seed = 67

save_path = './saved_weights/best.pt'

if seed != None:
    seed_everything(seed)


def train(epochs=20, patience=3, lr=2e-5, batch_size=16, max_seq_len=512, device='cpu'):

    _entity_labels = ['rare_disease', 'disease', 'symptom_and_sign', 'anaphor']
    entity_labels = []
    for e in _entity_labels:
        entity_labels.append('B-' + e)
        entity_labels.append('I-' + e)
    entity_labels.append('O')
    relation_labels = ['produces', 'increases_risk_of', 'is_a', 'is_acron', 'is_synon', 'anaphora', 'none']

    entity_id2label, entity_label2id, entity_label_num = get_label_id_map(entity_labels)
    relation_id2label, relation_label2id, relation_label_num = get_label_id_map(relation_labels)
    print(entity_id2label)
    print(relation_id2label)
    print('Seed: ' + str(seed))

    # load tokenizer and model
    PLM = 'emilyalsentzer/Bio_ClinicalBERT'
    tokenizer = AutoTokenizer.from_pretrained(PLM)
    bert_model = AutoModel.from_pretrained(PLM)
    model = Network(bert_model, entity_id2label, relation_id2label).to(device)
    
    # load data and create data lodaer
    train_data = load_data('data/RareDis2023/train.jsonl', few_shot=5)
    # train_data = load_data('data/RareDis2023/train.jsonl')
    valid_data = load_data('data/RareDis2023/valid.jsonl')
    test_data = load_data('data/RareDis2023/test.jsonl')

    # train_data = load_data('data/RareDis2023/train.jsonl', load_part=1)
    # valid_data = load_data('data/RareDis2023/train.jsonl', load_part=1)
    # test_data = load_data('data/RareDis2023/train.jsonl', load_part=1)

    train_dataloader = get_dataloader(train_data, batch_size, entity_label2id, entity_label_num, relation_label2id, relation_label_num, tokenizer, device, is_shuffle=True)
    valid_dataloader = get_dataloader(valid_data, batch_size, entity_label2id, entity_label_num, relation_label2id, relation_label_num, tokenizer, device)
    test_dataloader = get_dataloader(test_data, batch_size, entity_label2id, entity_label_num, relation_label2id, relation_label_num, tokenizer, device)

    # load optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # start training
    best_epoch = 0
    best_score = 0.
    patience_cnt = 0
    print('Start Training............')
    for epoch in range(1, epochs + 1):
        patience_cnt += 1

        model.train()
        train_loss = 0
        cnt_train = 0
        train_bar = tqdm(train_dataloader, position=0, leave=True)

        for batch_data in train_bar:
            optimizer.zero_grad()
            loss = model.compute_loss(batch_data)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            cnt_train += batch_size
            train_bar.set_description(f'Epoch {epoch}')
            train_bar.set_postfix(loss=train_loss / cnt_train)
    
        print(f'Epoch: [{epoch}/{epochs}], Loss: {train_loss / cnt_train}')
        
        if epoch < 3:
            continue

        ## valid
        model.eval()
        pred = []
        gold = []
        with torch.no_grad():
            valid_bar = tqdm(valid_dataloader, position=0, leave=True)
            for batch_data in valid_bar:
                predictions = model.predict(batch_data)
                pred.extend(predictions)
                for D in batch_data['original_data']:
                    gold.append(D['gold'])
                valid_bar.set_description(f'Epoch {epoch}')
        
        scores = evaluate(pred, gold)
        print('********* valid *********')
        printout_result(scores, 'exact')
        printout_result(scores, 'relaxed')
        cur_score = scores['exact']['overall']['f1']

        ## test
        # pred = []
        # gold = []
        # with torch.no_grad():
        #     test_bar = tqdm(test_dataloader, position=0, leave=True)
        #     for batch_data in test_bar:
        #         predictions = model.predict(batch_data)
        #         pred.extend(predictions)
        #         for D in batch_data['original_data']:
        #             gold.append(D['gold'])
        #         test_bar.set_description(f'Epoch {epoch}')
        
        # scores = evaluate(pred, gold)
        # print('********* test *********')
        # printout_result(scores, 'exact')
        # printout_result(scores, 'relaxed')


        if cur_score > best_score:
            patience_cnt = 0
            best_score = cur_score
            best_epoch = epoch
            # checkpoint = {'net': model.state_dict(), 'optimizer':optimizer.state_dict(), 'epoch': epoch}
            # torch.save(checkpoint, save_path)
            torch.save(model, save_path)
            print('***** new score *****')
            print(f'The best epoch is: {best_epoch}, with the best score is: {best_score}')
            print('********************')
        elif patience_cnt >= patience and epoch > 10: # early stop
            # if stage == 'init':
            #     stage = 'train'
            #     patience_cnt = 0
            # elif stage == 'train':
            print(f'Early Stop with best epoch {best_epoch}.......')
            break

    # test
    test_model = torch.load(save_path)
    test_model.eval()
    pred = []
    gold = []
    with torch.no_grad():
        test_bar = tqdm(test_dataloader, position=0, leave=True)
        for batch_data in test_bar:
            predictions = test_model.predict(batch_data)
            pred.extend(predictions)
            for D in batch_data['original_data']:
                gold.append(D['gold'])
    
    scores = evaluate(pred, gold)
    print('********* final *********')
    printout_result(scores, 'exact')
    printout_result(scores, 'relaxed')

    return test_model



if __name__ == '__main__':
    model = train(epochs=30, patience=2, lr=2e-4, batch_size=16, max_seq_len=512, device='cuda')