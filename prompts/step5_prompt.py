STEP5_PROMPT_TEMPLATE = '''### Task:
You will receive a section of text from medical literature. Analyze the medical text for named entities and their relations.
You will also receive extracted entities and extracted relations, but there are still some errors in them. Therefore, you need to fix them and output these entities and relations again.
You need to focus on relations and then go back to fix errors in predicated entities.

All entity types and relation types including their detailed definition are listed as follow.
### Definition:
## Entity:
"rare_disease": Diseases which affect a small number of people compared to the general population and specific issues are raised in relation to their rarity. In Europe, a disease is considered to be rare when it affects less than 1 person per 2000. Example: acquired aplastic anemia, Fryns syndrome, giant cell myocarditis.
"disease": An abnormal condition of a part, organ, or system of an organism resulting from various causes, such as infection, inflammation, environmental factors, or genetic defect, and characterised by an identifiable group of signs, symptoms, or both. Example: cancer, alzheimer, cardiovascular disease.
"symptom_and_sign": Signs and symptoms are abnormalities that may suggest a disease. Symptom is a physical or mental problem that a person experiences that may indicate a disease or condition; cannot be seen and do not show up on medical tests. Sign is something found during a physical exam or from a laboratory test that shows that a person may have a condition or disease. Example: fatigue, dyspnea, paininflammation, rash, abnormal heart rate, hypothermia.
"anaphor": Pronouns, words or nominal phrases that refer to a disease or a rare disease (which is the antecedent of the anaphor). Example: This disease, These diseases.
## Relation:
"produces": relation between any disease and a sign or a symptom produced by that disease.
"increases_risk_of": relation between a disease and a disorder, in which the disease increases the likelihood of suffering from that disorder.
"is_a": relation between a given disease and its classification as a more general disease.
"is_acron": relation between an acronym and its full or expanded form.
"is_synon": relation between two different names designating the same disease.
"anaphora": relation between an antecedent and an anaphor entity. The antecedent must be a rare disease. Example: ["rare disease", "It"]


### Notice:
You need to based on these points to filter out wrong entities.
  1. "symptom_and_sign" are usally appeared as reasons of "disease" and "rare_disease".
  2. In a relationship, the reason needs to be "symptom_and_sign", the results need to be "disease" and "rare_disease".
  3. "disease" cannot appear independently in the absence of other reasons.
  4. Do not identify all pronouns as "anaphor". "anaphor" must be a word that refer to a rare disease. "anaphor" here cannot refer to any other kinds of medical terms.
  5. These very general terms (e.g., condition, disorder, symptom or manifestation, disease) should not be extracted as "disease".


### Input (Give Passage): {text}

### Extracted Entities: {entities} 
### Extracted Relations: {relations}


### Output format
## Entity Representation:
- Each entity should be represented as E = ["entity_name", [position_start, position_end]], where 'position_start' is the position of the first character of the entity name in the text, and 'position_end' is the position of the last character of the entity name in the entire text.
- Position is a number and starts from 0. You must calculate every position exactly.
- The extracted entity name must be the same as in the original text.

## Relation Representation:
- Each relation should be represented as R = [subject_entity, object_entity], where both entities are defined as above.

## Your output should be a single JSON object in the following format:
{{
  "entities": {{
    "disease": [
      ["entity", [start, end]]
    ],
    "rare_disease": [],
    "symptom_and_sign": [],
    "anaphor": []
  }},
  "relations": {{
    "produces": [
      [["entity_1", [start, end]], ["entity_2", [start, end]]]
    ],
    "increases_risk_of": [],
    "is_a": [],
    "is_acron": [],
    "is_synon": [],
    "anaphora": []
  }}
}}

### Output: '''