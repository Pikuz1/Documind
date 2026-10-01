CREATE TABLE IF NOT EXISTS documents (
    id           TEXT PRIMARY KEY,
    filename     TEXT NOT NULL,
    page_count   INTEGER NOT NULL CHECK (page_count > 0),
    chunk_count  INTEGER NOT NULL CHECK (chunk_count >= 0),
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS query_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id  TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    question     TEXT NOT NULL,
    top_score    REAL,                 -- best retrieval relevance (NULL = nothing found)
    answered     INTEGER NOT NULL,     -- 1 = answered, 0 = "not found"
    latency_ms   INTEGER NOT NULL,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_query_log_document ON query_log(document_id);
