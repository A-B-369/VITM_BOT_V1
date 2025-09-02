# scripts/ingest_to_chroma.py
import os, json
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import chromadb
from chromadb.config import Settings

MODEL_NAME="VITM-Bot"  # small, local
emb_model = SentenceTransformer(MODEL_NAME)

client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="data/chroma_db"))
col = client.get_or_create_collection("vismuseum", metadata={"source":"vismuseum.gov.in"})

def chunk_text(text, max_chars=3000, overlap_chars=300):
    i=0
    chunks=[]
    while i < len(text):
        chunk = text[i:i+max_chars]
        chunks.append(chunk.strip())
        i += max_chars - overlap_chars
    return chunks

raw_dir = "data/raw"
for f in tqdm(os.listdir(raw_dir)):
    path=os.path.join(raw_dir, f)
    with open(path, encoding="utf8") as fh:
        j=json.load(fh)
    url=j.get("url")
    title=j.get("title","")
    text=j.get("text","")
    chunks = chunk_text(text)
    if not chunks: continue
    ids = [f"{f}__{idx}" for idx in range(len(chunks))]
    metadatas = [{"source_url":url, "page_title":title, "chunk_id":i} for i in range(len(chunks))]
    docs = chunks
    col.add(documents=docs, metadatas=metadatas, ids=ids)
client.persist()
print("done")
