from pathlib import Path
from uuid import uuid4

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter, TextSplitter

from app.core.errors import EmptyDocumentError
from app.db.repository import DocumentRecord, Repository
from app.vectorstore.chroma_store import chunk_ids


def build_splitter(chunk_size: int, chunk_overlap: int) -> TextSplitter:
    # Tries to split on paragraphs first, then lines, then sentences, then words.
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


class IngestionService:
    def __init__(
        self, splitter: TextSplitter, vector_store: VectorStore, repository: Repository
    ) -> None:
        self._splitter = splitter
        self._vector_store = vector_store
        self._repository = repository

    def ingest(self, pdf_path: Path, filename: str) -> DocumentRecord:
        pages = PyPDFLoader(str(pdf_path)).load()  # 1 LangChain Document per page
        if not any(page.page_content.strip() for page in pages):
            raise EmptyDocumentError(f"'{filename}' has no extractable text (scanned PDF?)")

        document_id = uuid4().hex
        chunks = self._split(pages, document_id, filename)
        ids = chunk_ids(document_id, len(chunks))
        # Embeds every chunk (via the store's embedding function) and saves the vectors.
        self._vector_store.add_documents(chunks, ids=ids)
        record = DocumentRecord(
            id=document_id, filename=filename, page_count=len(pages), chunk_count=len(chunks)
        )
        try:
            return self._repository.add_document(record)
        except Exception:
            # Two stores, no shared transaction: undo the vectors so Chroma has no orphans.
            self._vector_store.delete(ids=ids)
            raise

    def delete(self, record: DocumentRecord) -> None:
        self._vector_store.delete(ids=chunk_ids(record.id, record.chunk_count))
        self._repository.delete_document(record.id)

    def _split(self, pages: list[Document], document_id: str, filename: str) -> list[Document]:
        chunks = self._splitter.split_documents(pages)  # keeps each page's metadata
        for index, chunk in enumerate(chunks):
            chunk.metadata = {  # Chroma metadata must be flat scalars
                "document_id": document_id,
                "filename": filename,
                "page": int(chunk.metadata.get("page", 0)) + 1,  # PyPDF pages are 0-based
                "chunk_index": index,
            }
        return chunks
