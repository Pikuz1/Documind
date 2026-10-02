from langchain_core.prompts import ChatPromptTemplate

NOT_FOUND = "I could not find this in the document."

RAG_SYSTEM = f"""You are DocuMind, an assistant that answers questions about ONE contract.
Rules:
1. Use ONLY the context passages below. Never use outside knowledge.
2. If the passages do not contain the answer, reply exactly: "{NOT_FOUND}"
3. After each claim, cite the page like (p. 3).
4. The contract may be German or English. Always answer in the language of the QUESTION,
   not of the passages: if the question is English and the passages are German, translate.
5. Be concise: at most 5 sentences. This is not legal advice."""

# The language rule is repeated next to the question: smaller models follow the
# passages' language otherwise.
RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", RAG_SYSTEM),
        (
            "human",
            "Context passages:\n{context}\n\nQuestion: {question}\n\n"
            "Answer in the same language as the question above.",
        ),
    ]
)
