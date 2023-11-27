import json
import os



data = []
max_len = 0
with open('data/RareDis2023/test.jsonl') as f:
    for line in f.readlines():
        D = json.loads(line)
        data.append(D)
        length = len(D['text'].split())
        max_len = max(max_len, length)

# print(max_len)