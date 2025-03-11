# **Public Service Commission RAG Chatbot**

## **📌 Project Overview**

This project implements a **Retrieval-Augmented Generation (RAG) pipeline** using **Weaviate** as a vector database, **Cohere embeddings**, and **FastAPI** for backend processing. The frontend interface is built with **Streamlit**, allowing users to search **YouTube transcripts** from **Public Service Commission (PSC) meetings** and retrieve relevant insights.

## **📂 Project Structure**

```
Entergy-AI/
├── RAG/                      # Retrieval Augmented Generation system
│   ├── streamlit/            # Streamlit frontend
│   │   ├── __init__.py
│   │   └── app.py            # Streamlit frontend for querying transcripts
│   ├── __init__.py
│   ├── batch_upload.ipynb    # Notebook for batch uploading transcripts to Weaviate
│   ├── load_transcripts.py   # Script for loading transcript data
│   ├── routes.py             # FastAPI routes for the backend
│   ├── upload_transcripts.ipynb  # Notebook for transcript upload workflows
│   ├── weaviate_class.py     # Weaviate client wrapper class
│   ├── weviate.py            # Weaviate utilities            
├── .gitignore                # Git ignore file
├── readme.md                 # Project documentation
└── requirements.txt          # Dependencies for the project
```

---

## **⚙️ Setup Instructions**

### **1️⃣ Clone the Repository**

```bash
git clone https://github.com/[yourusername]/Entergy-AI.git
cd Entergy-AI/RAG
```

### **2️⃣ Create & Activate Virtual Environment**

```bash
python3 -m venv psc_env
source psc_env/bin/activate  # macOS/Linux
psc_env\Scripts\activate    # Windows
```

### **3️⃣ Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4️⃣ Set Up Environment Variables**

Create a `.env` file in the root directory and add your API keys:

```
WEAVIATE_URL="https://your-weaviate-instance.weaviate.cloud"
WEAVIATE_KEY="your_weaviate_api_key"
HUGGINGFACE_API_KEY="your_huggingface_api_key"
OPENAI_KEY="your_openai_api_key"
COHERE_KEY="your_cohere_api_key"
```

### **5️⃣ Run Weaviate Schema Initialization**

Before uploading transcripts, ensure the schema exists in Weaviate:

```python
python rag_demo.py --init-schema ## WORK IN PROGRESS
```

---

## **🚀 Running the Application**

### **1️⃣ Start FastAPI Backend**

```bash
uvicorn fastapi_app:app --reload
```

✅ FastAPI will be running at: **`http://127.0.0.1:8000`**

#### **Available API Endpoints:**

| Method | Endpoint  | Description            |
| ------ | --------- | ---------------------- |
| `POST` | `/ask`    | Query the RAG pipeline |
| `GET`  | `/health` | Check service health   |

### **2️⃣ Start Streamlit Frontend**

```bash
streamlit run streamlit/app.py
```

✅ Open **`http://localhost:8501`** in your browser.

---

## **📥 Uploading Transcripts to Weaviate**

To upload **Louisiana PSC transcripts**, run:

```python
python rag_demo.py --upload "data/Louisiana_Transcript_2024.json" ## WORK IN PROGRESS
```

---

## **🔍 Querying Transcripts**

### **Using API**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/ask' \
  -H 'Content-Type: application/json' \
  -d '{"question": "What were the discussions on rate increases?"}'
```

### **Using Streamlit Interface**

Simply enter your query in the UI and view relevant transcript excerpts

---

## **📌 Features & Capabilities**

✅ **Weaviate Integration** - Stores & retrieves transcripts efficiently  
✅ **Hugging Face Vectorizer** - Generates embeddings for transcript search  
✅ **FastAPI Backend** - Handles RAG pipeline & queries  
✅ **Streamlit Frontend** - User-friendly search interface  
✅ **Batch Processing** - Uploads & indexes transcripts in chunks  
✅ **State-Based Search** - Filter results by transcript source (Louisiana, etc.)

---

## **🛠️ Future Enhancements**

- [ ] Add support for **multiple states** & filtering
- [ ] Implement **Hybrid Search** (BM25 + Vector Search)
- [ ] Improve **document chunking strategy** for better retrieval

---
