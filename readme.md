# **Public Service Commission RAG Chatbot**

## **📌 Project Overview**

Meet REGGIE (REGulatory Governance Inquiry Engine)!! This project implements a **Retrieval-Augmented Generation (RAG) pipeline** using **Weaviate** as a vector database, **Cohere embeddings**, and **FastAPI** for backend processing. The frontend interface is built with **Streamlit**, allowing users to search **YouTube transcripts** from **Public Service Commission (PSC) meetings** and retrieve relevant insights.

## **📂 Project Structure**

```
Entergy-AI/
├── parsers/                  # Various transcript data, parsing scripts, etc.
├── RAG/                      # Retrieval Augmented Generation system
│   ├── streamlit/            # 🚨 Streamlit frontend directory
│   ├── __init__.py
│   ├── batch_upload.ipynb    # Notebook for batch uploading transcripts to Weaviate
│   ├── load_transcripts.py   # Script for loading transcript data
│   ├── routes.py             # 🚨 FastAPI routes for the backend
│   ├── upload_transcripts.ipynb  # Notebook for transcript upload workflows
│   ├── weaviate_class.py     # 🚨 Weaviate client wrapper class
│   ├── weviate.py            # Weaviate utilities            
├── .gitignore                # Git ignore file
├── readme.md                 # Project documentation
└── requirements.txt          # 🚨 Dependencies for the project
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
ANTHROPIC_KEY='your_claude_api_key'

```

### **5️⃣ Run Weaviate Schema Initialization**

Before uploading transcripts, ensure the schema exists in Weaviate:

```python
python weviate_class.py --init-schema ## WORK IN PROGRESS
```

---

## **🚀 Running the Application**

### **1️⃣ Start FastAPI Backend**

```bash
cd RAG
uvicorn routes:app --reload
```

✅ FastAPI will be running at: **`http://127.0.0.1:8000`**

#### **Available API Endpoints:**

| Method | Endpoint  | Description            |
| ------ | --------- | ---------------------- |
| `POST` | `/ask`    | Query the RAG pipeline |
| `GET`  | `/health` | Check service health   |

### **2️⃣ Start Streamlit Frontend**

```bash
cd rag/streamlit
streamlit run app.py
```

✅ Open **`http://localhost:8501`** in your browser.

---

## **📥 Uploading Transcripts to Weaviate**

To upload **Louisiana PSC transcripts**, run:

```python
python weviate_class.py --upload "data/example_transcripts.json" ## WORK IN PROGRESS
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
✅ **Cohere Vectorizer** - Generates embeddings for transcript search  
✅ **FastAPI Backend** - Handles RAG pipeline & queries  
✅ **Streamlit Frontend** - User-friendly search interface  
✅ **Batch Processing** - Uploads & indexes transcripts in chunks  
✅ **State-Based Search** - Filter results by transcript source (Louisiana, Mississippi, etc.)

---

A Tulane Computer Science Capstone project built by Peter Sapountzis, Jack Zemke, Bryan Flanagan, Rhon Farber, Griffin Olimpio
