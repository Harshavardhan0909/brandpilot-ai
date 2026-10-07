import re
from pathlib import Path
from collections import Counter

STOPWORDS = {"the", "and", "for", "with", "that", "this", "from", "your", "into", "are", "use"}


def tokenize(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9#]+", text.lower()) if w not in STOPWORDS]


def split_text(text: str, chunk_size: int = 650, overlap: int = 80) -> list[str]:
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + chunk_size].strip())
        start += chunk_size - overlap
    return [chunk for chunk in chunks if chunk]


def retrieve(query: str, documents: list[str], top_k: int = 4) -> list[dict]:
    query_terms = Counter(tokenize(query))
    scored = []
    for index, document in enumerate(documents):
        terms = Counter(tokenize(document))
        overlap = sum(min(query_terms[t], terms[t]) for t in query_terms)
        score = overlap / max(len(query_terms), 1)
        scored.append({"text": document, "score": round(score, 3), "chunk": index})
    return sorted(scored, key=lambda item: item["score"], reverse=True)[:top_k]


def read_guideline_file(path: str | Path) -> str:
    file_path = Path(path)
    if file_path.suffix.lower() == ".txt":
        return file_path.read_text(encoding="utf-8")
    raise ValueError("MVP supports .txt guideline files; PDF extraction is the next extension")
