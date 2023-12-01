STEP3_PROMPT_TEMPLATE = '''### Task:
You will receive a section of text from medical literature. Analyze the medical text for named entities.
Focus on identifying instances of diseases, rare diseases, symptoms and signs, and anaphors. Provide the entities and their character position indices within the text.


All entity types including their detailed definition are listed as follow.
### Definition:
## Entity:
"rare_disease": Diseases which affect a small number of people compared to the general population and specific issues are raised in relation to their rarity. In Europe, a disease is considered to be rare when it affects less than 1 person per 2000. Example: acquired aplastic anemia, Fryns syndrome, giant cell myocarditis.
"disease": An abnormal condition of a part, organ, or system of an organism resulting from various causes, such as infection, inflammation, environmental factors, or genetic defect, and characterised by an identifiable group of signs, symptoms, or both. Example: cancer, alzheimer, cardiovascular disease.
"symptom_and_sign": Signs and symptoms are abnormalities that may suggest a disease. Example: fatigue, dyspnea, paininflammation, rash, abnormal heart rate, hypothermia.
"anaphor": Pronouns, words or nominal phrases that refer to a rare disease (which is the antecedent of the anaphor). It must be a word that refer to a rare disease. Example: This disease, These diseases, It, (which and its is not a "anaphor").


### Notice:
1. Entities of rare_disease and disease always appear as proper nouns or terminologies. In contrast, entities of symptom_and_sign usually appear in the form of common words.
2. Some extracted medical terms maybe cannot be classified into "diseases", "rare_disease", or "symptoms_and_sign". In this case, you can discard these words.
3. Some medical terms may not have been extracted, so you need to re-extract more medical terms from the original text.
4. "symptom_and_sign" are usally appeared as reasons of "disease" and "rare_disease".
5. Do not identify all pronouns as "anaphor". "anaphor" must be a word that refer to a rare disease. "anaphor" here cannot refer to any other kinds of medical terms.
6. These very general terms (e.g., condition, disorder, symptom or manifestation, disease) should not be extracted as "disease".


### Exemplars
Here are some exemplers of input text and target entities:
{examplars}


### Input (Give Passage): {text}

### Extracted Medical Terms: {medical_terms}
### Extracted Anaphor: {anaphor}
### Rare Disease Knowledge: {rare_disease_knowledge}

### Output format
## Entity Representation:
- Each entity should be represented as E = ["entity_name", [position_start, position_end]], where 'position_start' is the position of the first character of the entity name in the text, and 'position_end' is the position of the last character of the entity name in the entire text.
- Position is a number and starts from 0. You must calculate every position exactly.
- The extracted entity name must be the same as in the original text.

## Your output should be a single JSON object in the following format:
{{
  "entities": {{
    "disease": [
      ["entity", [start, end]]
    ],
    "rare_disease": [],
    "symptom_and_sign": [],
    "anaphor": []
  }}
}}

### Output: '''