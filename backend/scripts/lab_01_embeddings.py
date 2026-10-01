"""Lab 1 — what is an embedding? Run: python scripts/lab_01_embeddings.py"""
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings

# First run downloads the model (~450 MB) into ~/.cache/huggingface. Runs locally afterwards.
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

sentences = [
    "Die Kündigungsfrist beträgt drei Monate zum Monatsende.",    # German: notice period
    "The notice period is three months.",                        # English: same meaning
    "The employee receives 30 days of paid vacation per year.",  # related domain, other topic
    "The cat sat on the mat.",                                   # unrelated
]
vectors = embeddings.embed_documents(sentences)   # list[list[float]]
print(f"Each text → vector with {len(vectors[0])} dimensions")


def cosine(a: list[float], b: list[float]) -> float:
    a, b = np.array(a), np.array(b)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


query = embeddings.embed_query("How long before I can quit my job?")
for sentence, vector in zip(sentences, vectors):
    print(f"{cosine(query, vector):.3f}  {sentence}")
