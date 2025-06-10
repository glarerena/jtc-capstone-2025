from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain_community.vectorstores import Chroma as DeprecatedChroma  # for fallback
from langchain.chains import RetrievalQA

# Load vector store
vectordb = Chroma(
    persist_directory="chroma_db",
    embedding_function=OllamaEmbeddings(model="phi3:mini")
)

# Set up retriever
retriever = vectordb.as_retriever()

# Use updated LLM class
llm = OllamaLLM(model="phi3:mini")

# Use RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# Ask a question
query = "How does Bloom Housing support accessible housing?"
response = qa_chain.invoke({"query": query})  # new preferred method

print("\n🧠 Question:", query)
print("💬 Answer:", response['result'])
