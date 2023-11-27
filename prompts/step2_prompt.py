STEP2_PROMPT_TEMPLATE = '''### Task:
You will receive a section of text from medical literature. Analyze the medical text for named entities.
Focus on identifying instances of diseases, rare diseases, symptoms and signs, and anaphors. Provide the entities and their character position indices within the text.


All entity types including their detailed definition are listed as follow.
### Definition:
## Entity:
"rare_disease": Diseases which affect a small number of people compared to the general population and specific issues are raised in relation to their rarity. In Europe, a disease is considered to be rare when it affects less than 1 person per 2000. Example: acquired aplastic anemia, Fryns syndrome, giant cell myocarditis.
"disease": An abnormal condition of a part, organ, or system of an organism resulting from various causes, such as infection, inflammation, environmental factors, or genetic defect, and characterised by an identifiable group of signs, symptoms, or both. Example: cancer, alzheimer, cardiovascular disease.
"symptom_and_sign": Signs and symptoms are abnormalities that may suggest a disease. Example: fatigue, dyspnea, paininflammation, rash, abnormal heart rate, hypothermia.
"anaphor": Pronouns, words or nominal phrases that refer to a rare disease (which is the antecedent of the anaphor). "anaphor" must be a word that refer to a rare disease. Example: This disease, These diseases, It, (which and its is not a "anaphor").
"medical_term": Medical terms include rare disease, disease, symptom_and_sign.


### Notice:
1. Some of other rare disease entities you should extract from in the input text exists in an abbreviated form or in other kinds of similar name. You need to extract these implicit rare disease entities as well.
2. You should try to find as many "rare_disease" as possible, which means you need to identify all the "rare_disease" you can. You don't need to worry about incorrectly identifying a "rare_disease".
3. You only need to extract "medical_term" and "anaphor" in the current step.
4. Do not identify all pronouns as "anaphor". "anaphor" must be a word that refer to a rare disease. "anaphor" here cannot refer to any other kinds of medical terms.
5. These very general terms (e.g., condition, disorder, symptom or manifestation, disease) should not be extracted as 'medical_term'.


Some medical terms which have been discovered:
{medical_terms}

Based on these terms, find more medical terms in the given passage. In your output, you should output old medical terms as well as new medical terms.
Besides, you also need to find anaphor which refer to a rare disease.


### Input Text:
{text}


### Output format
## Entity Representation:
- Each entity should be represented as E = ["entity_name", [position_start, position_end]], where 'position_start' is the position of the first character of the entity name in the text, and 'position_end' is the position of the last character of the entity name in the entire text.
- Position is a number and starts from 0. You must calculate every position exactly.
- The extracted entity name must be the same as in the original text.

## Your output should be a single JSON object in the following format:
{{
    "medical_term": [
      ["entity", [start, end]]
    ],
    "anaphor": []
}}

### Output: '''


