# Retrieval evaluation

DocuMind can only answer from the passages it retrieves, so retrieval quality is measured on its own, before any LLM call. This page records how the default chunking settings were chosen.

## Setup

- **Document:** a synthetic 6-page German employment contract ([`backend/eval/arbeitsvertrag.pdf`](../backend/eval/arbeitsvertrag.pdf), 16 clauses). It's synthetic so it can be published; the generator is [`backend/scripts/make_eval_contract.py`](../backend/scripts/make_eval_contract.py).
- **Golden set:** 15 questions, each labeled with the page that holds the answer ([`backend/eval/golden_set.yaml`](../backend/eval/golden_set.yaml)). 13 are in English and 2 in German, so most of them test cross-lingual retrieval (English question, German text).
- **Pipeline:** the app's own `IngestionService` and Chroma store, with the local `paraphrase-multilingual-MiniLM-L12-v2` embeddings. No LLM is involved.
- **Metrics:**
  - **hit@4**: share of questions whose correct page is among the top 4 retrieved chunks. The app sends the top 4 to the LLM (`TOP_K=4`), so this is the metric that decides whether the LLM can see the answer.
  - **hit@1**: share of questions whose correct page is the top result.
  - **avg top score**: mean relevance score of the best chunk (cosine-based, higher is better).

## Results

| chunk_size | overlap | chunks | hit@1 | hit@4 | avg top score |
|---:|---:|---:|---:|---:|---:|
| 400 | 60 | 21 | 73% | 100% | 0.541 |
| **800** | **120** | **12** | **67%** | **100%** | **0.529** |
| 1200 | 200 | 7 | 67% | 93% | 0.502 |

The only miss: at 1200, *"How many days a week can I work from home?"* (expected p. 5, retrieved pages 4, 2, 6, 3).

## What the numbers say

- **Large chunks blur meaning.** At 1200 characters, page 5 becomes one chunk that holds three clauses: side jobs, confidentiality and remote work. Its vector averages all three topics, so the remote-work question no longer finds it. At 800, `§ 12 Mobiles Arbeiten` gets a chunk of its own and is retrieved.
- **Smaller chunks score slightly higher.** The average top score drops as chunks grow (0.541, 0.529, 0.502), the expected effect of each vector covering fewer topics.
- **Cross-lingual retrieval works.** At 400 and 800, every English question found its German clause within the top 4.

## Decision

The default stays at **`CHUNK_SIZE=800`, `CHUNK_OVERLAP=120`**:

- It ties 400 on hit@4 (100%), the metric that matters with `TOP_K=4`.
- Each passage gives the LLM more surrounding text to answer from.
- The hit@1 gap to 400 is a single question (11 vs. 10 of 15), too small to act on.
- 1200 is where retrieval starts to fail.

## Limitations

One document and 15 questions is a small sample. Differences of one question are noise. The clear signals are the 1200 miss and the score trend. The contract is also cleanly structured, with numbered `§` clauses; real scanned or messy contracts would likely score lower. Adding more documents and questions to the golden set is the next step before tuning further.

## Reproduce

```bash
cd backend && source .venv/bin/activate
python -m scripts.evaluate_retrieval
```
