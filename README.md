# DocuChat AI

DocuChat AI is a high-performance, multi-document Retrieval-Augmented Generation (RAG) system. It allows users to upload multiple PDF documents and engage in a context-aware chat where every response is grounded in the provided text and includes precise page-level citations.

## 🚀 Features

- **Multi-Document Context**: Query across multiple PDFs simultaneously.
- **Strict Grounding**: The AI is constrained to answer only based on uploaded content to prevent hallucinations.
- **Page-Level Citations**: Responses include references in the format `[Filename - Page X]`.
- **Session Isolation**: Uses Pinecone namespaces to ensure data from one user session never leaks into another.
- **Streaming Responses**: Real-time feedback for a smooth user experience.

## 🏗️ Architecture

The system follows a modern RAG pipeline:
1. **Ingestion**: PDFs are processed using `PyMuPDF`.
2. **Chunking**: Text is split using `RecursiveCharacterTextSplitter` (1000 chars, 200 overlap).
3. **Vector Storage**: Embeddings (`text-embedding-3-small`) are stored in Pinecone with session-specific namespaces.
4. **Retrieval**: Similarity search fetches the top 5 relevant chunks.
5. **Generation**: OpenAI GPT-4o generates the final answer based strictly on the retrieved context.

## 🛠️ Tech Stack

- **Frontend**: Next.js, Tailwind CSS, Lucide React.
- **Backend**: FastAPI (Python), LangChain.
- **Database**: Pinecone (Vector DB).
- **LLM**: OpenAI GPT-4o.

## ⚙️ Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenAI API Key
- Pinecone API Key

### Backend Setup
1. Navigate to the `backend` directory.
2. Create a virtual environment: `python -m venv venv`.
3. Activate it: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows).
4. Install dependencies: `pip install -r requirements.txt`.
5. Create a `.env` file:
   ```env
   OPENAI_API_KEY=your_key
   PINECONE_API_KEY=your_key
   PINECONE_ENVIRONMENT=your_env
   PINECONE_INDEX_NAME=docuchat
   ```
6. Run the server: `uvicorn main:app --reload`.

### Frontend Setup
1. Navigate to the `frontend` directory.
2. Install dependencies: `npm install`.
3. Create a `.env.local` file:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
4. Run the development server: `npm run dev`.

## 📝 Usage
1. Open the browser to `http://localhost:3000`.
2. Upload one or more PDF files (Max 10MB per file).
3. Wait for the "Processing Complete" notification.
4. Start asking questions about your documents!
