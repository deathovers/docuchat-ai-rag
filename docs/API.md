# API Documentation: DocuChat AI

This document outlines the available API endpoints for the DocuChat AI service.

## Base URL
`http://localhost:8000/v1`

---

## 1. Document Management

### Upload Documents
`POST /upload`

Uploads one or more PDF files to be processed and indexed for the current session.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:**
    - `files`: List of PDF files.
    - `session_id`: A unique string identifying the user session.

**Response (200 OK):**
```json
[
  {
    "id": "uuid-v4",
    "name": "annual_report.pdf",
    "status": "processed",
    "page_count": 15
  }
]
```

### Delete Document
`DELETE /documents/{doc_id}`

Removes a specific document and its associated vector embeddings.

**Parameters:**
- `doc_id` (path): The unique ID of the document.
- `session_id` (query): The session ID associated with the document.

**Response (204 No Content):**
- Success.

---

## 2. Chat Interface

### Query Documents
`POST /chat`

Performs a RAG-based query against the documents uploaded in the current session.

**Request Body:**
```json
{
  "session_id": "string",
  "query": "What is the total revenue mentioned in the report?",
  "history": [
    { "role": "user", "content": "Hello" },
    { "role": "assistant", "content": "Hi! How can I help with your docs?" }
  ]
}
```

**Response (200 OK):**
```json
{
  "answer": "The total revenue for fiscal year 2023 was $5.2 billion.",
  "citations": [
    {
      "document": "annual_report.pdf",
      "page": 12
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request`: Missing session ID or invalid file format.
- `500 Internal Server Error`: AI service failure or processing error.

---

## 3. Data Models

### Message Object
Used in the `history` array for the chat endpoint.
```json
{
  "role": "user" | "assistant",
  "content": "string",
  "timestamp": "ISO-8601"
}
```
