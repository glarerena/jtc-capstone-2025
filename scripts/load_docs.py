import json
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.docstore.document import Document

# Load JSON file
with open("docs/housing_faq.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Convert to LangChain Documents — no splitting!
documents = [
    Document(page_content=f"Q: {item['question']}\nA: {item['answer']}")
    for item in raw_data
]

# Optional: Preview content
for doc in documents:
    print(doc.page_content)

# Embed and persist using llama3:8b
embedding_function = OllamaEmbeddings(model="llama3:8b")
db = Chroma.from_documents(documents, embedding_function, persist_directory="chroma_db")
db.persist()

print("✅ Vector store persisted from JSON.")
