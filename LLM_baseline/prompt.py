PROMPT = '''### Task:
You will receive a section of text from medical literature. Analyze the medical text for named entities and their relations.
Focus on identifying instances of diseases, rare diseases, symptoms and signs, and anaphors. Provide the entities and their character position indices within the text.
Then, identify the relationships between these entities, such as anaphoric references or other specific relations mentioned in the text.


All entity types and relation types are listed as follow.
## Entity: "rare_disease", "disease", "symptom_and_sign", "anaphor"
## Relation: "produces", "increases_risk_of", "is_a", "is_acron", "is_synon", "anaphora"

"anaphora" is a relation between an antecedent and an anaphor entity. The antecedent must be a disease or a rare disease. Example: ["rare disease", "It"]


### Input Text:
{text}


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