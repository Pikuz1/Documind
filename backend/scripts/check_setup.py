"""Verify the installation.
Run:  python scripts/check_setup.py          (offline checks)
      python scripts/check_setup.py --real   (also calls the LLM with your API key)"""

import os
import sys
from importlib.metadata import PackageNotFoundError, version

PACKAGES = [
    "fastapi",
    "uvicorn",
    "python-multipart",
    "pydantic-settings",
    "langchain-core",
    "langchain-community",
    "langchain-text-splitters",
    "langchain-chroma",
    "langchain-huggingface",
    "langchain-google-genai",
    "chromadb",
    "pypdf",
    "sentence-transformers",
    "numpy",
    "pytest",
    "pytest-cov",
    "httpx",
    "ruff",
    "fpdf2",
]
MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def main() -> int:
    ok = sys.version_info >= (3, 12)
    print(f"{'✅' if ok else '❌'} Python {sys.version.split()[0]} (need 3.12+)")
    for pkg in PACKAGES:
        try:
            print(f"✅ {pkg:28} {version(pkg)}")
        except PackageNotFoundError:
            print(f"❌ {pkg:28} NOT INSTALLED")
            ok = False
    if not ok:
        print("\nFix the ❌ items above, then run again.")
        return 1

    # LangChain chain + ChromaDB with fake models (no download, no API key)
    from langchain_chroma import Chroma
    from langchain_core.documents import Document
    from langchain_core.embeddings import DeterministicFakeEmbedding
    from langchain_core.language_models import FakeListChatModel
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate

    store = Chroma(
        collection_name="setup_check", embedding_function=DeterministicFakeEmbedding(size=8)
    )
    store.add_documents([Document(page_content="hello vector db")], ids=["1"])
    assert store.similarity_search("hello", k=1)[0].page_content == "hello vector db"
    chain = (
        ChatPromptTemplate.from_template("{x}")
        | FakeListChatModel(responses=["ok"])
        | StrOutputParser()
    )
    assert chain.invoke({"x": "ping"}) == "ok"
    print("✅ LangChain chain + ChromaDB work")

    # The real local embedding model
    from langchain_huggingface import HuggingFaceEmbeddings

    vector = HuggingFaceEmbeddings(model_name=MODEL).embed_query("Kündigungsfrist")
    print(f"✅ Embedding model works ({len(vector)} dimensions)")

    if "--real" in sys.argv:
        from dotenv import load_dotenv
        from langchain_core.output_parsers import StrOutputParser
        from langchain_google_genai import ChatGoogleGenerativeAI

        load_dotenv()
        llm = ChatGoogleGenerativeAI(
            model=os.getenv("LLM_MODEL", "gemini-3.8-flash"),
            max_output_tokens=20,
            thinking_budget=0,
        )
        reply = (llm | StrOutputParser()).invoke("Reply with exactly: ready")
        print(f"✅ LLM replied: {reply}")

    print("\nAll good — You're ready for Step 0.1.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
