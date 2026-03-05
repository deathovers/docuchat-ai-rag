# DocuChat AI

DocuChat AI is a high-performance Retrieval-Augmented Generation (RAG) application that allows users to upload multiple PDF documents and interact with them using natural language. The system ensures data privacy through session-based isolation and provides verifiable answers with direct citations to source files and page numbers.

## 🚀 Features

- **Multi-PDF Support**: Upload and query multiple documents simultaneously (up to 10 per session).
- **Session Isolation**: Uses metadata filtering in Pinecone to ensure users only access their own uploaded data.
- **Cited Responses**: Every answer includes the source filename and page number for transparency.
- **Strict Grounding**: The AI is configured to answer only based on provided documents, preventing hallucinations.
- **Asynchronous Pipeline**: Built with FastAPI and AsyncOpenAI for low-latency performance.

## 🏗️ Architecture

The system follows a standard RAG pipeline:

1.  **Ingestion**: PDFs are parsed (PyMuPDF), chunked (Recursive Character Splitting), embedded (OpenAI `text-embedding-3-small`), and stored in Pinecone.
2.  **Retrieval**: User queries are vectorized and used to perform a similarity search against the session-specific vectors.
3.  **Generation**: Top-k relevant chunks are fed into GPT-4o-mini with a strict system prompt to generate the final cited response.

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: React (SPA)
- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector Database**: Pinecone
- **PDF Processing**: PyMuPDF / pdfplumber

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js & npm
- OpenAI API Key
- Pinecone API Key and Index

### Backend Setup
1. Clone the repository.
2. Navigate to the backend directory: `cd backend`.
3. Create a `.env` file:
   ```env
   OPENAI_API_KEY=your_openai_key
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_INDEX_NAME=your_index_name
   ```
4. Install dependencies: `pip install -r requirements.txt`.
5. Run the server: `uvicorn app.main:app --reload`.

### Frontend Setup
1. Navigate to the frontend directory: `cd frontend`.
2. Install dependencies: `npm install`.
3. Start the development server: `npm start`.

## 🔒 Security & Privacy
- **Statelessness**: Data is partitioned by `session_id`.
- **TTL**: Vectors and temporary files are intended to be purged after session expiry (MVP uses ephemeral session logic).
