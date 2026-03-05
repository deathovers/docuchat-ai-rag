# API Documentation - DocuChat AI v1

The DocuChat AI API provides endpoints for document management and RAG-based chat interactions. All requests must include a `Session-ID` to ensure data isolation.

## Base URL
`http://localhost:8000/v1`

## Headers
| Header | Description | Required |
| :--- | :--- | :--- |
| `Session-ID` | A unique UUID representing the user's current session. | Yes |

---

## Endpoints

### 1. Upload Documents
Uploads one or more PDF files and triggers the ingestion pipeline.

- **URL**: `/upload`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Payload**: 
    - `files`: List of PDF files.
- **Response**: `200 OK`
```json
{
  "message": "Files uploaded and processed successfully",
  "session_id": "uuid-string",
  "files": ["contract.pdf", "manual.pdf"]
}
```

### 2. List Files
Retrieves a list of all documents uploaded in the current session.

- **URL**: `/files`
- **Method**: `GET`
- **Response**: `200 OK`
```json
[
  {
    "document_id": "uuid",
    "file_name": "contract.pdf",
    "upload_timestamp": "2023-10-27T10:00:00Z"
  }
]
```

### 3. Delete File
Removes a specific document and its associated vectors from the session.

- **URL**: `/files/{file_id}`
- **Method**: `DELETE`
- **Response**: `204 No Content`

### 4. Chat
Sends a query to the RAG engine and receives a cited response.

- **URL**: `/chat`
- **Method**: `POST`
- **Payload**:
```json
{
  "query": "What is the termination clause?",
  "history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi, how can I help with your docs?"}
  ]
}
```
- **Response**: `200 OK`
```json
{
  "answer": "The contract may be terminated with 30 days notice.",
  "citations": [
    { "file_name": "Contract_v2.pdf", "page": 12 }
  ]
}
```

## Error Handling
- `400 Bad Request`: Invalid file format or missing parameters.
- `429 Too Many Requests`: OpenAI Rate limits exceeded.
- `500 Internal Server Error`: Processing or connectivity failure.
