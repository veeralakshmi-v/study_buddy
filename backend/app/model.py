from typing import List, Tuple
import json
import re
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KB_PATH = Path(__file__).parent / "kb.json"

def _load_kb() -> List[dict]:
    with open(KB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

class Retriever:
    def __init__(self, kb_path: str = None):
        self.docs = _load_kb()
        self.texts = [d["content"] for d in self.docs]
        # You can tune TfidfVectorizer params
        self.vectorizer = TfidfVectorizer(strip_accents="unicode",
                                          stop_words="english",
                                          ngram_range=(1,2),
                                          max_features=20000)
        self.doc_vectors = self.vectorizer.fit_transform(self.texts)
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[dict, float]]:
        # vectorize query
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.doc_vectors).flatten()
        top_idx = np.argsort(sims)[::-1][:top_k]
        results = []
        for idx in top_idx:
            results.append((self.docs[int(idx)], float(sims[int(idx)])))
        return results

    @staticmethod
    def extract_answer_from_doc(question: str, doc_text: str, max_sentences: int = 3) -> str:
        # Very simple heuristic: return sentences that share keywords with the question
        sentences = re.split(r'(?<=[.!?]) +', doc_text)
        q_tokens = set(re.findall(r"\w+", question.lower()))
        scored = []
        for s in sentences:
            s_tokens = set(re.findall(r"\w+", s.lower()))
            overlap = len(q_tokens & s_tokens)
            scored.append((overlap, s))
        scored.sort(key=lambda x: x[0], reverse=True)
        # If nothing matches, return first few sentences as fallback
        chosen = [s for score, s in scored if score > 0][:max_sentences]
        if not chosen:
            chosen = sentences[:max_sentences]
        return " ".join(chosen).strip()
