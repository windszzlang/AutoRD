import json
import openai
import random
import time
from tqdm import tqdm

from utils import *
from prompts.step5_prompt import STEP5_PROMPT_TEMPLATE
from env import OPENAI_API_KEY


openai.api_key = OPENAI_API_KEY
model_name = 'gpt-4-0613' # official model: gpt-3.5-turbo, gpt-4
temperature = 0

data = load_data('cache_data/step4_res.jsonl')
output_path = 'cache_data/step5_res/'
new_data = []


for D in tqdm(data):
    file_path = output_path + D['id'] +  '.json'
    if not os.path.exists(file_path):

        entities = D['cache']['step3']['entities']
        relations = D['cache']['step4']['relations']

        model_input = STEP5_PROMPT_TEMPLATE.format(text=D['text'], entities=entities, relations=relations)
        try:
            resp = openai.ChatCompletion.create(
                model=model_name,
                messages=[
                    {'role': 'user', 'content': model_input}
                ],
                temperature=temperature
            )
            model_output = resp.choices[0].message.content
            # print(model_output)
            # D['cache']['step5'] = json.loads(model_output)
            D['pred'] = json.loads(model_output)
            # D['model_output'] = model_output
        except Exception as e:
            print(e)
            continue
        
        with open(file_path, 'w') as f:
            json.dump(D, f)

        # print(D)
        # break
        # time.sleep(10)


# gather_llm_output('cache_data/step4_res', 'cache_data/step4_res.jsonl')
# pred, gold = gather_data('cache_data/step4_res')

pred, gold = get_pred_gold_from_scatterd_data('cache_data/step5_res')

gather_llm_output('cache_data/step5_res', 'cache_data/step5_res.jsonl')

scores = evaluate(pred, gold)


printout_result(scores, 'exact')
# printout_result(scores, 'relaxed')