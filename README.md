# HERO RAG Chatbot

This is HERO chatbot project — a Retrieval-Augmented Generation (RAG) chatbot that answers affordable housing questions.
 I used FastAPI for the backend, a modern HTML UI for the frontend, FAISS for vector search, and Ollama + TinyLlama for fast local inference.



## Setup Summary (Everything I Did)

### 🔧 Environment Setup

* Created a new Python virtual environment.
* Installed required packages with `pip install -r requirements.txt`.
* Installed `ollama` locally and pulled the `tinyllama` model.

### 🐳 Docker Setup

* Added a `Dockerfile` and `.dockerignore` for containerizing the backend.
* Created a `docker-compose.yml` file to manage services.
* Used `uvicorn` in the Docker container to serve the FastAPI app.
* Confirmed container runs and loads the chatbot successfully.

### 🧠 Data & Embeddings

* Created a `housing_faq.json` file with simple Q\&A about affordable housing.
* Built a FAISS vector index from the JSON using `HuggingFaceEmbeddings`.

  * Used `all-MiniLM-L6-v2` from `langchain_huggingface`.
  * Stored the FAISS index inside the `docs/faiss_index/` directory.

### ⚙️ Backend Code

* Used FastAPI to create the backend.
* Added endpoints:

  * `/ask` – main RAG chat endpoint
  * `/feedback` – logs ratings/comments to `feedback_log.txt`
  * `/` – serves frontend HTML file
  * `/health` – returns status
* Wrote logic to:

  * Detect unrelated questions using a keyword filter
  * Load the FAISS vector index
  * Use `OllamaLLM` with `tinyllama` to generate answers
  * Format results and return styled HTML

### 🧊 Vector Store

* Switched from Chroma to FAISS to improve performance.
* Updated import to use the latest module:

  ```python
  from langchain_community.vectorstores import FAISS
  ```

### 🌍 Language Support (Commented Out)

* **NOTE:** Language detection and translation logic was previously implemented using `deep_translator` and a `language` dropdown in the UI.
* That code has been commented out to improve speed and avoid translation overhead.
* **To re-enable:**

  * Uncomment the `language` field in the `ChatRequest` model.
  * Add translation logic to convert incoming non-English messages to English and outgoing responses back to the selected language.
  * Restore the dropdown UI in `chatbot.html` and `main.py` translation hooks.

### 🏁 Ollama Integration

* Warmed up Ollama using a background thread with a dummy request.
* Kept the model warm to reduce response latency.

### 💬 Chat UI

* Stored `chatbot.html` inside `frontend/` folder.
* Displays messages from user + Hero, with loading time below.
* **Includes:**

  * Basic language dropdown selector (currently disabled in backend).
  * Feedback mechanism: 👍👎 with optional text comment.

### ✅ Final Fixes

* Reorganized all imports.
* Added inline comments for everything (newbie-friendly).
* Verified response time (under 6 seconds).

### 📦 Updated Dependencies

* Updated `requirements.txt` to include:

  * `langchain-community`
  * `langchain-huggingface`
  * `faiss-cpu`
  * `uvicorn`
  * `fastapi`
  * `pydantic`
  * `deep_translator`

---

## Run the App

```bash
uvicorn app.main:app --reload
```

Make sure `faiss_index` exists inside `docs/` and `housing_faq.json` is there when building.

```bash
cd docs
python build_faiss_index.py
```

---


