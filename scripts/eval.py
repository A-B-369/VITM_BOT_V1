# scripts/eval.py
import json, requests

EVAL_PATH="data/eval.jsonl"
URL="http://localhost:8000/ask"

def normalize(s):
    return "".join(c.lower() for c in s if c.isalnum())

total=0
ok=0
for line in open(EVAL_PATH,encoding="utf8"):
    total+=1
    obj=json.loads(line)
    q=obj["question"]
    gold=obj["gold"]
    resp=requests.post(URL, json={"question":q}).json()["answer"]
    if normalize(gold) in normalize(resp):
        ok+=1
    else:
        print("FAIL", q, "->", resp, "gold:", gold)
print(f"{ok}/{total} exact-match or substring")
