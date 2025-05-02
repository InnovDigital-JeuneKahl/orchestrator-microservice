# File Orchestration Service for Microservice-Based Transcription

A service that handles routing uploaded files to appropriate transcription microservices based on file extensions and integrates with a RAG (Retrieval Augmented Generation) system.

## Overview

This service acts as an orchestrator between client applications and various specialized transcription microservices, each responsible for handling specific file types (e.g., audio, documents, images, videos). It:

1. Receives files from clients
2. Determines the appropriate transcription service based on file extension
3. Routes the file to the correct service for transcription
4. Extracts and enhances metadata
5. Integrates with a RAG system for advanced querying and generation

## Features

### File Type Routing
- Automatically routes files to appropriate microservices based on file extension
- Uses a configurable mapping between file extensions and service endpoints
- Supports runtime configuration updates

### Metadata Extraction
- Extracts basic metadata such as filename, size, and content type
- Accepts and merges additional user-provided metadata
- Example metadata structure:
```json
{
  "filename": "quarterly_meeting_2024Q1.mp3",
  "file_type": "audio",
  "author": "John Smith",
  "size_bytes": 15000000,
  "additional_metadata": {
    "meeting_title": "Q1 2024 Financial Review",
    "department": "Finance",
    "participants": "John Smith, Jane Doe, Robert Johnson",
    "duration_minutes": 45,
    "transcription_quality": "high"
  }
}
```

### Request Types

#### File Processing
- Upload a file for transcription
- Process and store in the RAG system for later retrieval

#### Question Answering
- Upload a file and ask a question about its contents
- Get relevant context and an AI-generated answer

## API Reference

### Process a File

```
POST /api/process
```

Processes a file and adds it to the RAG system.

**Request:**
- `file`: The file to process (multipart/form-data)
- `metadata`: Optional JSON string with additional metadata

**Response:**
```json
{
  "filename": "example.mp3",
  "file_type": "audio",
  "size_bytes": 15000000,
  "transcription_length": 12500,
  "rag_response": {
    "status": "success",
    "document_id": "doc_123456"
  }
}
```

### Ask a Question About a File

```
POST /api/question
```

Upload a file and ask a question about its content.

**Request:**
- `file`: The file to process (multipart/form-data)
- `question`: The question to answer (form field)
- `metadata`: Optional JSON string with additional metadata

**Response:**
```json
{
  "question": "What were the Q1 financial results?",
  "answer": {
    "response": "In Q1 2024, the company reported revenue of $10.2M, which represents a 15% increase year-over-year...",
    "model": "qwen2.5:3b-instruct"
  },
  "file_info": {
    "filename": "quarterly_meeting_2024Q1.mp3",
    "file_type": "audio",
    "size_bytes": 15000000
  },
  "relevant_passages": [
    {
      "text": "Our Q1 2024 financial results show revenue of $10.2M, a 15% increase from last year's Q1...",
      "score": 0.92
    },
    {
      "text": "The breakdown by department shows that Product contributed $6.8M, Services added $2.1M, and...",
      "score": 0.87
    }
  ]
}
```

### Get Service Mapping Configuration

```
GET /api/config/mapping
```

Get the current service mapping configuration.

**Response:**
```json
{
  "audio": {
    "extensions": [".mp3", ".wav", ".flac", ".m4a"],
    "service_endpoint": "http://audio-transcription-service:8080/transcribe",
    "content_type": "audio"
  },
  "document": {
    "extensions": [".pdf", ".docx", ".txt", ".rtf", ".odt"],
    "service_endpoint": "http://document-transcription-service:8081/extract",
    "content_type": "document"
  },
  "image": {
    "extensions": [".jpg", ".jpeg", ".png", ".tiff", ".bmp"],
    "service_endpoint": "http://ocr-service:8082/get-text",
    "content_type": "image"
  },
  "video": {
    "extensions": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
    "service_endpoint": "http://video-transcription-service:8083/transcribe",
    "content_type": "video"
  }
}
```

### Reload Service Mapping Configuration

```
POST /api/config/reload
```

Reload the service mapping configuration from disk.

**Response:**
```json
{
  "status": "success",
  "message": "Configuration reloaded"
}
```

## Setup and Configuration

### Requirements
- Python 3.8+
- FastAPI
- Uvicorn
- Other dependencies in requirements.txt

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/file-orchestration-service.git
   cd file-orchestration-service
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Edit the configuration file at `config/service_mapping.json` to match your microservices

4. Run the service
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker Deployment

```bash
docker build -t file-orchestration-service .
docker run -p 8000:8000 file-orchestration-service
```

## Integration Examples

### Python Client Example

```python
import requests

# Process a file
files = {"file": open("example.mp3", "rb")}
metadata = json.dumps({
    "author": "John Smith",
    "additional_metadata": {
        "meeting_title": "Q1 2024 Financial Review",
        "department": "Finance"
    }
})
response = requests.post(
    "http://localhost:8000/api/process", 
    files=files, 
    data={"metadata": metadata}
)
print(response.json())

# Ask a question about a file
files = {"file": open("example.mp3", "rb")}
response = requests.post(
    "http://localhost:8000/api/question", 
    files=files, 
    data={
        "question": "What were the Q1 financial results?",
        "metadata": metadata
    }
)
print(response.json())
```

## Extending the Service

To add support for new file types:

1. Update the `service_mapping.json` file with new extensions and service endpoints
2. Implement any specialized metadata extraction in the `MetadataExtractor` class
3. Reload the configuration via the API endpoint or by restarting the service

## License

[MIT License](LICENSE)

