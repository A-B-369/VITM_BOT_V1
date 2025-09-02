# app/rag_server.py
import subprocess, json, textwrap
from fastapi import FastAPI
from pydantic import BaseModel
import chromadb

app = FastAPI()
client = chromadb.Client()
col = client.get_collection("vismuseum")

SYSTEM_PROMPT = """You MUST answer using only the provided Context. If the answer is not fully supported by the Context, answer exactly: "I don't know." Quote the exact snippet(s) you used (wrap them in quotes). Keep answers concise."""
TEMPLATE = """Question:
{question}

Context:
{context}

Rules:
- Only reply with information present in Context.
- If Context doesn't fully answer, reply EXACTLY: "I don't know."
- Quote the snippet(s) you used.
"""

class QRequest(BaseModel):
    question: str
    model: str = "llama3.2:instruct"  # replace with your Ollama model

def retrieve_context(q, k=4):
    res = col.query(query_texts=[q], n_results=k)
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    joined = []
    for d,m in zip(docs, metas):
        joined.append(f"URL: {m.get('source_url')}\nTitle: {m.get('page_title')}\n\n{d}")
    return "\n\n---\n\n".join(joined)

def call_ollama(model, messages):
    # Use ollama chat via subprocess JSON interface (or use OllamaClient)
    payload = {"messages": messages}
    cp = subprocess.run(["ollama", "chat", model, "--json"], input=json.dumps(payload).encode(), capture_output=True)
    out = cp.stdout.decode("utf8")
    # Ollama's output parsing may vary; adjust if needed.
    obj = json.loads(out)
    return obj["message"]["content"]

@app.post("/ask")
def ask(qreq: QRequest):
    ctx = retrieve_context(qreq.question, k=6)
    prompt = TEMPLATE.format(question=qreq.question, context=ctx)
    messages = [{"role":"system", "content":SYSTEM_PROMPT}, {"role":"user","content":prompt}]
    resp = call_ollama(qreq.model, messages)
    return {"answer": resp}
