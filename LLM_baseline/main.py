import json
import openai
from tqdm import tqdm
import random
import traceback

from utils import *
from prompt import PROMPT


from env import OPENAI_API_KEY


openai.api_key = OPENAI_API_KEY
# official model: gpt-3.5-turbo, gpt-4, gpt-4-0613
# model_name = 'gpt-4-1106-preview'
model_name = 'gpt-4-0613'


test_data = load_data('data/RareDis2023/test.jsonl')
train_data = load_data('data/RareDis2023/train.jsonl')

num_examplars = 5
use_examplars = False
'''
### Some Examplars are provided for you to refer:
{examplars}
'''


for D in tqdm(test_data):
    file_path = 'cache_data/' + D['id'] +  '.json'
    if not os.path.exists(file_path):

        examplars = []
        if use_examplars:
            random_samples = random.sample(train_data, num_examplars)
            for sample in random_samples:
                examplars.append({
                    'Input': sample['text'],
                    'Output': sample['gold']
                })
        # print(D['text'])
        # print(PROMPT)
        # model_input = PROMPT.format(text=D['text'], examplars=json.dumps(examplars))
        model_input = PROMPT.format(text=D['text'])
        try:
            resp = openai.ChatCompletion.create(
                model=model_name,
                messages=[
                    {'role': 'user', 'content': model_input}
                ],
                temperature=0
            )
            model_output = resp.choices[0].message.content
            # print(model_output)
            model_pred = json.loads(model_output)
            D['pred'] = model_pred
        except Exception as e:
            traceback.print_exc()
            continue
        
        with open(file_path, 'w') as f:
            json.dump(D, f)

        # break



pred, gold = get_pred_gold_from_scatterd_data('cache_data')


scores = evaluate(pred, gold)


printout_result(scores, 'exact')
printout_result(scores, 'relaxed')