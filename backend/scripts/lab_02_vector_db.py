"""Lab 2 — ChromaDB raw API. Run: python scripts/lab_02_vector_db.py"""

import chromadb
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
client = chromadb.EphemeralClient()  # in-memory; PersistentClient(path=...) saves to disk
collection = client.create_collection("lab", metadata={"hnsw:space": "cosine"})

texts = [
    ("Notice period is three months.", {"doc": "employment", "page": 4}),
    ("Rent is 950 EUR per month, due on the 3rd.", {"doc": "rental", "page": 1}),
    ("Vacation: 30 working days per year.", {"doc": "employment", "page": 5}),
]
collection.add(
    ids=[f"chunk-{i}" for i in range(len(texts))],
    documents=[t for t, _ in texts],
    metadatas=[m for _, m in texts],
    embeddings=embeddings.embed_documents([t for t, _ in texts]),
)

question = "How many holidays do I get?"
result = collection.query(
    query_embeddings=[embeddings.embed_query(question)],
    n_results=2,
    where={"doc": "employment"},  # metadata filter, like SQL WHERE
)
zipped = zip(result["documents"][0], result["metadatas"][0], result["distances"][0], strict=True)
for text, meta, dist in zipped:
    print(f"distance={dist:.3f}  page={meta['page']}  {text}")
