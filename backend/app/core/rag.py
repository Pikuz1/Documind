from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.vectorstores import VectorStore

from app.ai.prompts import NOT_FOUND, RAG_PROMPT


@dataclass(frozen=True)
class Source:
    page: int
    text: str
    score: float


@dataclass(frozen=True)
class RagAnswer:
    answer: str
    sources: list[Source]

    @property
    def top_score(self) -> float | None:
        return max((s.score for s in self.sources), default=None)


def format_context(docs: list[Document]) -> str:
    return "\n\n---\n\n".join(f"[Page {d.metadata['page']}]\n{d.page_content}" for d in docs)


class RagService:
    def __init__(
        self,
        vector_store: VectorStore,
        llm: BaseChatModel,
        top_k: int = 4,
        min_score: float = 0.3,
    ) -> None:
        self._vector_store = vector_store
        self._top_k = top_k
        self._min_score = min_score
        self._chain = RAG_PROMPT | llm | StrOutputParser()  # LCEL chain

    def answer(self, question: str, document_id: str) -> RagAnswer:
        hits = self._vector_store.similarity_search_with_relevance_scores(
            question,
            k=self._top_k,
            filter={"document_id": document_id},
        )
        relevant = [(doc, score) for doc, score in hits if score >= self._min_score]
        if not relevant:  # don't even call the LLM
            return RagAnswer(answer=NOT_FOUND, sources=[])

        docs = [doc for doc, _ in relevant]
        answer = self._chain.invoke({"context": format_context(docs), "question": question})
        return RagAnswer(
            answer=answer,
            sources=[
                Source(page=d.metadata["page"], text=d.page_content, score=round(s, 3))
                for d, s in relevant
            ],
        )
