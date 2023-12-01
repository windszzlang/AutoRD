import json
import openai
import random
import time
from tqdm import tqdm

from utils import *
from prompts.step4_prompt import STEP4_PROMPT_TEMPLATE
from env import OPENAI_API_KEY


openai.api_key = OPENAI_API_KEY
model_name = 'gpt-4-0613' # official model: gpt-3.5-turbo, gpt-4
temperature = 0

data = load_data('cache_data/step3_res.jsonl')
output_path = 'cache_data/step4_res/'
new_data = []


raredisease_phenotype_triples = load_data('data/raredisease_phenotype_triples.jsonl')

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
                    "relations": sample['gold']['relations'],
                }
            })
        
        entities = D['cache']['step3']['entities']
        rare_disease_knowledge = ''
        for rd in entities['rare_disease']:
            rd = rd[0]
            for triple in raredisease_phenotype_triples:
                if rd in triple['source']['name']:
                    rare_disease_knowledge += json.dumps(triple)
                    break

        model_input = STEP4_PROMPT_TEMPLATE.format(text=D['text'], entities=entities, rare_disease_knowledge=rare_disease_knowledge, examplars=json.dumps(examplars))
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
            D['cache']['step4'] = json.loads(model_output)
            # D['pred'] = {
            #     'entities': D['cache']['step3']['entities'],
            #     'relations': D['cache']['step4']['relations'],
            # }
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


gather_llm_output('cache_data/step4_res', 'cache_data/step4_res.jsonl')




# pred, gold = get_pred_gold_from_scatterd_data('cache_data/step4_res')

# scores = evaluate(pred, gold)


# printout_result(scores, 'exact')
# printout_result(scores, 'relaxed')