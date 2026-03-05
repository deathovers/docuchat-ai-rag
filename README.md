# DocuChat AI

DocuChat AI is a high-performance Retrieval-Augmented Generation (RAG) platform designed to allow users to interact with multiple PDF documents through natural language. The system prioritizes accuracy, strict grounding in provided context, and session-based data isolation.

## 🚀 Features

- **Multi-PDF Support:** Upload and query across up to 10 PDF documents simultaneously.
- **High-Fidelity Extraction:** Uses `PyMuPDF` to maintain page-level metadata for precise citations.
- **Contextual Retrieval:** Implements recursive character text splitting and vector search for relevant context matching.
- **Grounded Generation:** Custom-engineered prompts ensure the AI only answers based on uploaded content, preventing hallucinations.
- **Session Isolation:** Uses metadata filtering in the vector database to ensure users only access their own uploaded data.
- **Citations:** Every answer includes specific document names and page numbers.

## 🏗️ Architecture

The system follows a standard RAG pipeline:
1. **Ingestion:** PDFs are parsed -> Split into chunks (1000 chars, 200 overlap) -> Embedded using OpenAI `text-embedding-3-small`.
2. **Storage:** Vectors are stored in a Vector Database (e.g., Pinecone) with `session_id` metadata.
3. **Retrieval:** User queries are embedded -> Top-k relevant chunks are retrieved using `session_id` filters.
4. **Generation:** OpenAI GPT model generates a response using the retrieved chunks as the sole source of truth.

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- OpenAI API Key
- Pinecone API Key (or supported Vector DB)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/docuchat-ai.git
   cd docuchat-ai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables (`.env`):
   ```env
   OPENAI_API_KEY=your_openai_key
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_ENVIRONMENT=your_environment
   LLM_MODEL=gpt-4-turbo-preview
   ```

4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## 📖 Usage
1. **Upload:** Send your PDFs to the `/v1/upload` endpoint with a unique `session_id`.
2. **Chat:** Post queries to `/v1/chat` including your `session_id` and any previous message history.
3. **Cleanup:** Sessions are volatile; refreshing or terminating the session will trigger data cleanup.

## ⚠️ Constraints
- No OCR support (text-based PDFs only).
- Maximum of 10 PDFs per session.
- Responses are strictly limited to the provided document context.
