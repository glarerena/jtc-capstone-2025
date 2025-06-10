from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema.document import Document
import json
import os

# Load your JSON document
with open("housing_faq.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert each Q&A pair into a LangChain Document
docs = [
    Document(page_content=f"Q: {entry['question']}\nA: {entry['answer']}")
    for entry in data
]

# Create embeddings and FAISS index
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
vectordb = FAISS.from_documents(docs, embedding_function)

# Save index to disk
vectordb.save_local("faiss_index")
print("✅ FAISS index created and saved to 'faiss_index/'")
