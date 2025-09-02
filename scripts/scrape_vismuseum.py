# scripts/scrape_vismuseum.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os, time, json
from collections import deque

BASE = "https://vismuseum.gov.in/"
OUT = "data/raw"
os.makedirs(OUT, exist_ok=True)

# Simple BFS crawler (polite)
seen=set()
q=deque([BASE])
max_pages=200

while q and len(seen) < max_pages:
    url=q.popleft()
    if url in seen: continue
    try:
        r=requests.get(url, timeout=15)
        if r.status_code!=200: continue
        soup=BeautifulSoup(r.text, "html.parser")
        title = (soup.title.string or "").strip()
        # extract visible text
        for s in soup(["script","style","noscript"]):
            s.extract()
        text = soup.get_text(separator="\n")
        meta = {"url": url, "title": title}
        fname = urlparse(url).path.strip("/").replace("/", "_") or "index"
        fname = f"{fname}.json"
        with open(os.path.join(OUT, fname), "w", encoding="utf8") as f:
            json.dump({"url":url, "title":title, "text": text}, f, ensure_ascii=False, indent=2)
        seen.add(url)
        # queue internal links
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full = urljoin(url, href)
            if full.startswith(BASE) and full not in seen:
                q.append(full)
        time.sleep(0.3)
    except Exception as e:
        print("skip", url, e)
