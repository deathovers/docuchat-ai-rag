# DocuChat AI - API Documentation

The DocuChat AI backend is built with FastAPI and provides endpoints for document management and RAG-based querying.

## Base URL
`http://localhost:8000`

---

## 1. Document Management

### Upload PDF
`POST /upload`

Uploads a PDF file, extracts text, generates embeddings, and stores them in the vector database.

**Request:**
- `multipart/form-data`
- `file`: Binary PDF file.
- `session_id`: String (Unique identifier for the user session).

**Response:**
```json
{
  "file_id": "uuid-string",
  "filename": "contract.pdf",
  "status": "processed"
}
```

### List Files
`GET /files/{session_id}`

Returns a list of all files currently indexed for the given session.

**Response:**
```json
[
  { "file_id": "uuid1", "filename": "manual.pdf" },
  { "file_id": "uuid2", "filename": "report.pdf" }
]
```

### Delete File
`DELETE /files/{file_id}`

Removes the document's vectors and metadata from the index.

---

## 2. Chat & Query

### Query Documents
`POST /query`

Performs a similarity search and generates a grounded response.

**Request Body:**
```json
{
  "question": "What is the termination clause?",
  "session_id": "user-session-123"
}
```

**Response Body:**
```json
{
  "answer": "The contract may be terminated with 30 days notice [Contract.pdf - Page 12].",
  "sources": [
    { "file_name": "Contract.pdf", "page": 12 }
  ]
}
```

### Clear Session
`DELETE /session/{session_id}`

Deletes all vectors associated with the session namespace and clears chat history.

---

## 3. Data Models

### Vector Metadata
Stored in Pinecone:
```json
{
  "text": "Chunk content...",
  "source_name": "filename.pdf",
  "page_number": 5,
  "session_id": "uuid"
}
```

## 4. Error Codes
- `400 Bad Request`: Invalid file format or missing parameters.
- `413 Payload Too Large`: File exceeds 10MB limit.
- `500 Internal Server Error`: Issues with OpenAI or Pinecone connectivity.
