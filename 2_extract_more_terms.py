import json
import openai
import random
import time
from tqdm import tqdm

from utils import *
from prompts.step2_prompt import STEP2_PROMPT_TEMPLATE
from env import OPENAI_API_KEY


openai.api_key = OPENAI_API_KEY
model_name = 'gpt-4-0613' # official model: gpt-3.5-turbo, gpt-4, gpt-4-0613
temperature = 0

data = load_data('cache_data/step1_res.jsonl')
output_path = 'cache_data/step2_res/'
new_data = []

train_data = load_data('data/RareDis2023/train.jsonl')
num_examplars = 5

for D in tqdm(data):
    file_path = output_path + D['id'] +  '.json'
    if not os.path.exists(file_path):
        
        medical_terms_str = ''
        for term, definition in D['cache']['step1']['medical_terms']:
            if term.islower() and len(term) <= 4:
                continue
            medical_terms_str += 'Term: ' + term + ', Definition: ' + definition + ';\n'

        model_input = STEP2_PROMPT_TEMPLATE.format(text=D['text'], medical_terms=medical_terms_str)
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
            D['cache']['step2'] = json.loads(model_output)
        except Exception as e:
            print(e)
            continue
        
        with open(file_path, 'w') as f:
            json.dump(D, f)

        # print(D)
        # break
        # time.sleep(10)



gather_llm_output('cache_data/step2_res', 'cache_data/step2_res.jsonl')