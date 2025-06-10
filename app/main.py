# ─── Standard Library ──────────────────────────────────────────────────────────
from pathlib import Path
from datetime import datetime
import requests
import threading
import time
import re

# ─── Third-Party Libraries ─────────────────────────────────────────────────────
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
# from deep_translator import GoogleTranslator  # ⛔ Commented out for now — re-enable for multilingual support

# ─── LangChain and LLM Tools ───────────────────────────────────────────────────
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA

# ─── App Initialization ────────────────────────────────────────────────────────
app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    # language: str = "en"  # ⛔ Temporarily removed for simplicity; uncomment if enabling translation

# ─── Feedback Logging ──────────────────────────────────────────────────────────
@app.post("/feedback")
def feedback(data: dict):
    with open("feedback_log.txt", "a", encoding="utf-8") as f:
        comment = data.get("comment", "").strip()
        line = f"{datetime.now()} | Question: {data['question']} | Rating: {data['rating']}"
        if comment:
            line += f" | Comment: {comment}"
        f.write(line + "\n")
    return {"message": "Feedback received!"}

# ─── Housing Filter ────────────────────────────────────────────────────────────
HOUSING_KEYWORDS = [
    "housing", "apply", "rent", "affordable", "home",
    "apartment", "eligibility", "section 8", "voucher", "unit"
]

def is_unrelated_to_housing(message: str) -> bool:
    unrelated_keywords = ["weather", "sports", "stocks", "Biden", "Trump", "AI models", "Taylor Swift", "Elon Musk"]
    return all(keyword.lower() not in message.lower() for keyword in HOUSING_KEYWORDS) and any(keyword.lower() in message.lower() for keyword in unrelated_keywords)

# ─── Utility ───────────────────────────────────────────────────────────────────
def linkify(text):
    url_pattern = r'(https?://[^\s]+)'
    return re.sub(url_pattern, r'<a href="\1" target="_blank" style="color:#2563eb; text-decoration:underline;">\1</a>', text)

# ─── Static Routes ─────────────────────────────────────────────────────────────
@app.get("/", response_class=FileResponse)
def serve_chat_ui():
    html_path = Path(__file__).parent.parent / "frontend" / "chatbot.html"
    if not html_path.exists():
        raise RuntimeError(f"File not found: {html_path}")
    return FileResponse(html_path)

@app.get("/health")
def read_root():
    return {"message": "RAG chatbot is running!"}

# ─── Ollama Warm-Up ────────────────────────────────────────────────────────────
def warm_up_ollama():
    try:
        requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "tinyllama", "prompt": "Hello!", "stream": False}
        )
        print("✅ Ollama warm-up complete.")
    except Exception as e:
        print(f"⚠️ Ollama warm-up failed: {e}")

threading.Thread(target=warm_up_ollama).start()

# ─── Embeddings + Vector Store ─────────────────────────────────────────────────
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectordb = FAISS.load_local("docs/faiss_index", embeddings=embedding_function, allow_dangerous_deserialization=True)

# ─── Language Model Setup ──────────────────────────────────────────────────────
llm = OllamaLLM(model="tinyllama", temperature=0.3)
retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 3})

prompt = PromptTemplate.from_template(
    """You are a helpful housing assistant. Use the information in the context below to answer the user's question.

Context:
{context}

Question:
{question}

Answer:
"""
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt}
)

# ─── Main Chat Endpoint ────────────────────────────────────────────────────────
@app.post("/ask", response_class=HTMLResponse)
def ask_with_rag(request: ChatRequest):
    total_start = time.time()

    # ─── Translation Logic (DISABLED) ───────────────────────────────────────────
    # Uncomment below if you want automatic translation using `deep_translator`
    #
    # if request.language.lower() != "en":
    #     translated = GoogleTranslator(source=request.language, target="en").translate(request.message)
    #     print(f"🔁 Translated '{request.message}' → '{translated}'")
    #     user_question = translated
    # else:
    #     user_question = request.message
    #
    # ────────────────────────────────────────────────────────────────────────────

    # 🔧 Temporary bypass — using message directly (no translation)
    user_question = request.message

    if is_unrelated_to_housing(user_question):
        html = f"""
        <div style='font-family: sans-serif; line-height: 1.5;'>
            <p><strong>You:</strong> {request.message}</p>
            <p><strong>Hero:</strong> I'm here to help with affordable housing. Please ask about applying, documents, eligibility, or senior/disability housing.</p>
        </div>
        """
        return HTMLResponse(content=html)

    docs = retriever.get_relevant_documents(user_question)
    for i, doc in enumerate(docs):
        print(f"Doc {i+1}: {doc.page_content}\n")

    response = qa_chain.invoke({"query": user_question})
    response_text = re.sub(r'^(Hero:\s*)+', '', response['result']).strip()

    # ─── Translate Back to User Language (DISABLED) ─────────────────────────────
    # Uncomment this section if translation was applied above
    #
    # if request.language.lower() != "en":
    #     response_text = GoogleTranslator(source="en", target=request.language).translate(response_text)
    #
    # ────────────────────────────────────────────────────────────────────────────

    total_time = time.time() - total_start

    html = f"""
    <div style='font-family: sans-serif; line-height: 1.5;'>
        <p><strong>You:</strong> {request.message}</p>
        <p>{linkify(response_text)}</p>
        <p style='color: gray; font-size: small;'>⏱️ {round(total_time, 1)}s</p>
    </div>
    """
    return HTMLResponse(content=html)
