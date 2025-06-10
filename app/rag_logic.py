from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from pathlib import Path



def build_vectorstore():
    markdown_dir = Path("data/markdown")
    md_files = list(markdown_dir.glob("*.md"))

    docs = []
    for file in md_files:
        loader = TextLoader(str(file), encoding="utf-8")  # Force UTF-8 to fix UnicodeDecodeError
        docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    embeddings = OllamaEmbeddings(model="phi3:mini")
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="chroma_db"
    )
    vectordb.persist()
    print(f"✅ Vector store created with {len(chunks)} chunks.")

if __name__ == "__main__":
    build_vectorstore()
