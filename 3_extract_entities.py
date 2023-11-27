import json
import openai
import random
import time
from tqdm import tqdm

from utils import *
from prompts.step3_prompt import STEP3_PROMPT_TEMPLATE
from env import OPENAI_API_KEY


openai.api_key = OPENAI_API_KEY
model_name = 'gpt-4-0613' # official model: gpt-3.5-turbo, gpt-4
temperature = 0

data = load_data('cache_data/step2_res.jsonl')
output_path = 'cache_data/step3_res/'
new_data = []

rare_disease_ontology = load_data('data/rare_disease_ontology.jsonl')

train_data = load_data('data/RareDis2023/train.jsonl')
num_examplars = 5

for D in tqdm(data):
    file_path = output_path + D['id'] +  '.json'
    if not os.path.exists(file_path):

        examplars = []
        random_samples = random.sample(train_data, num_examplars)
        for sample in random_samples:
            examplars.append({
                'Input': sample['text'],
                'Output': {
                    "entities": sample['gold']['entities']
                }
            })

        medical_terms = D['cache']['step2']['medical_term']
        rare_disease_knowledge = ''
        for term in medical_terms:
            term = term[0]
            if len(term) <= 6:
                continue
            for rd in rare_disease_ontology:
                if term == rd['name']:
                    rare_disease_knowledge += json.dumps(rd)
                    break


        model_input = STEP3_PROMPT_TEMPLATE.format(text=D['text'], medical_terms=medical_terms, rare_disease_knowledge=rare_disease_knowledge, anaphor=D['cache']['step2']['anaphor'], examplars=json.dumps(examplars))
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
            D['cache']['step3'] = json.loads(model_output)
        except Exception as e:
            print(e)
            continue
        
        with open(file_path, 'w') as f:
            json.dump(D, f)

        # print(D)
        # break
        # time.sleep(10)


gather_llm_output('cache_data/step3_res', 'cache_data/step3_res.jsonl')
