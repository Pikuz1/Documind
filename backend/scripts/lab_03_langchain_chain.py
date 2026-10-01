"""Lab 3 — LangChain LCEL. Run: python scripts/lab_03_langchain_chain.py

Needs GOOGLE_API_KEY in backend/.env (free Gemini tier).
"""

from dotenv import load_dotenv  # installed alongside pydantic-settings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Answer ONLY from the context. If it's not there, say 'Not found'."),
        ("human", "Context: {context}\n\nQuestion: {question}"),
    ]
)
llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0)
chain = prompt | llm | StrOutputParser()

print(
    chain.invoke({"context": "Notice period: 3 months.", "question": "What is the notice period?"})
)
print(chain.invoke({"context": "Notice period: 3 months.", "question": "What is my salary?"}))

# Peek inside: what does the prompt actually produce?
print(prompt.invoke({"context": "X", "question": "Y"}).to_messages())
