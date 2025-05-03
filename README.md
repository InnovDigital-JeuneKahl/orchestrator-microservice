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

## API Reference

### 1. File Processing Endpoints

#### Process a File

```http
POST /api/process
```

Processes a file and adds it to the RAG system.

**Request:**
- Content-Type: `multipart/form-data`
- Parameters:
  - `file`: The file to process (Required)
  - `metadata`: Optional JSON string with additional metadata (Optional)

Example using cURL:
```bash
curl -X POST "http://localhost:8000/api/process" \
  -H "accept: application/json" \
  -F "file=@quarterly_report.pdf" \
  -F 'metadata={"author": "Jane Smith", "additional_metadata": {"department": "Finance", "meeting_title": "Q1 Review"}}'
```

Example using Python:
```python
import requests
import json

# Process a file
files = {"file": open("quarterly_report.pdf", "rb")}
metadata = json.dumps({
    "author": "Jane Smith",
    "additional_metadata": {
        "department": "Finance",
        "meeting_title": "Q1 Review"
    }
})

response = requests.post(
    "http://localhost:8000/api/process", 
    files=files, 
    data={"metadata": metadata}
)
print(response.json())
```

**Response:**
```json
{
  "filename": "quarterly_report.pdf",
  "file_type": "document",
  "size_bytes": 1250000,
  "transcription_length": 15000,
  "rag_response": {
    "status": "success",
    "message": "Processed 8 chunks",
    "chunk_ids": ["chunk_001", "chunk_002", "..."],
    "processing_time_seconds": 1.25
  }
}
```

### 2. Question Answering

#### Ask a Question About a File

```http
POST /api/question
```

Upload a file and ask a question about its content. The system will check if the file has been processed previously to avoid redundant processing.

**Request:**
- Content-Type: `multipart/form-data`
- Parameters:
  - `file`: The file to process (Required)
  - `question`: The question to answer (Required)
  - `metadata`: Optional JSON string with additional metadata (Optional)

Example using cURL:
```bash
curl -X POST "http://localhost:8000/api/question" \
  -H "accept: application/json" \
  -F "file=@quarterly_report.pdf" \
  -F "question=What were the Q1 financial results?" \
  -F 'metadata={"author": "Jane Smith", "additional_metadata": {"department": "Finance"}}'
```

Example using Python:
```python
import requests
import json

# Ask a question about a file
files = {"file": open("quarterly_report.pdf", "rb")}
metadata = json.dumps({
    "author": "Jane Smith",
    "additional_metadata": {
        "department": "Finance"
    }
})

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

**Response:**
```json
{
  "question": "What were the Q1 financial results?",
  "answer": {
    "response": "In Q1 2024, the company reported revenue of $10.2M, which represents a 15% increase year-over-year...",
    "model": "qwen2.5:3b-instruct",
    "sources": [
      {
        "id": 1,
        "chunk_id": "chunk_002",
        "content_snippet": "Our Q1 2024 financial results show revenue growth of 15% YoY..."
      }
    ]
  },
  "file_info": {
    "filename": "quarterly_report.pdf",
    "file_type": "document",
    "size_bytes": 1250000
  },
  "relevant_passages": [
    {
      "content": "Our Q1 2024 financial results show revenue of $10.2M, a 15% increase from last year's Q1...",
      "chunk_id": "chunk_002",
      "score": 0.92
    },
    {
      "content": "The breakdown by department shows that Product contributed $6.8M, Services added $2.1M, and...",
      "chunk_id": "chunk_003",
      "score": 0.87
    }
  ]
}
```

### 3. Search Endpoints

#### Search Within a File

```http
POST /api/search
```

Search for specific terms within a file and get context around matches.

**Request:**
- Content-Type: `multipart/form-data`
- Parameters:
  - `file`: The file to search within (Required)
  - `search_terms`: Terms to search for in the document (Required)

Example using cURL:
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "accept: application/json" \
  -F "file=@quarterly_report.pdf" \
  -F "search_terms=revenue growth"
```

Example using Python:
```python
import requests

# Search within a file
files = {"file": open("quarterly_report.pdf", "rb")}

response = requests.post(
    "http://localhost:8000/api/search", 
    files=files, 
    data={"search_terms": "revenue growth"}
)
print(response.json())
```

**Response:**
```json
{
  "filename": "quarterly_report.pdf",
  "file_type": "document",
  "search_terms": "revenue growth",
  "results": [
    {
      "text": "Our Q1 2024 financial results show revenue growth of 15% year-over-year.",
      "timestamp_start": null,
      "timestamp_end": null,
      "context": {
        "before": "Executive Summary. The following report details our financial performance for Q1 2024.",
        "current": "Our Q1 2024 financial results show revenue growth of 15% year-over-year.",
        "after": "This exceeds our forecast of 12% and positions us well for the remainder of the fiscal year."
      }
    },
    {
      "text": "The drivers behind our revenue growth include new client acquisition and expansion of existing accounts.",
      "timestamp_start": null,
      "timestamp_end": null,
      "context": {
        "before": "This exceeds our forecast of 12% and positions us well for the remainder of the fiscal year.",
        "current": "The drivers behind our revenue growth include new client acquisition and expansion of existing accounts.",
        "after": "We added 15 new enterprise clients and expanded 28 existing accounts in Q1."
      }
    }
  ],
  "count": 2
}
```

#### Keyword Search in RAG System

```http
POST /api/keyword-search
```

Search across all processed documents in the RAG system using keywords.

**Request:**
- Content-Type: `application/json`
- Body:
```json
{
  "keywords": ["revenue", "growth", "forecast"],
  "filter_metadata": {
    "file_type": "document",
    "department": "Finance"
  },
  "model": "qwen2.5:3b-instruct",
  "top_k": 5,
  "query": "What was our revenue growth compared to forecast?"
}
```

All fields except `keywords` are optional.

Example using cURL:
```bash
curl -X POST "http://localhost:8000/api/keyword-search" \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["revenue", "growth", "forecast"], "filter_metadata": {"department": "Finance"}, "query": "What was our revenue growth compared to forecast?"}'
```

Example using Python:
```python
import requests

data = {
  "keywords": ["revenue", "growth", "forecast"],
  "filter_metadata": {
    "department": "Finance"
  },
  "query": "What was our revenue growth compared to forecast?"
}

response = requests.post(
    "http://localhost:8000/api/keyword-search", 
    json=data
)
print(response.json())
```

**Response:**
```json
{
  "query": "What was our revenue growth compared to forecast?",
  "results": [
    {
      "content": "Our Q1 2024 financial results show revenue growth of 15% year-over-year. This exceeds our forecast of 12%.",
      "chunk_id": "chunk_002",
      "metadata": {
        "filename": "quarterly_report.pdf",
        "file_type": "document",
        "department": "Finance"
      },
      "score": 0.95
    },
    {
      "content": "While we projected a 12% revenue growth this quarter, actual performance exceeded expectations at 15%.",
      "chunk_id": "chunk_015",
      "metadata": {
        "filename": "executive_summary.pdf",
        "file_type": "document",
        "department": "Finance"
      },
      "score": 0.87
    }
  ],
  "response": "The revenue growth was 15% year-over-year, which exceeded the forecast of 12% by 3 percentage points.",
  "keywords": ["revenue", "growth", "forecast"],
  "model": "qwen2.5:3b-instruct"
}
```

### 4. Document Management

#### List Processed Files

```http
GET /api/processed-files
```

Retrieve a list of all files that have been processed and stored in the RAG system.

Example using cURL:
```bash
curl -X GET "http://localhost:8000/api/processed-files"
```

Example using Python:
```python
import requests

response = requests.get("http://localhost:8000/api/processed-files")
print(response.json())
```

**Response:**
```json
{
  "files": {
    "quarterly_report.pdf": {
      "chunk_count": 8,
      "processing_time_seconds": 1.25,
      "modellm_used": "qwen2.5:3b-instruct",
      "file_type": "document",
      "processed_at": 1714924800
    },
    "executive_summary.pdf": {
      "chunk_count": 4,
      "processing_time_seconds": 0.75,
      "modellm_used": "qwen2.5:3b-instruct",
      "file_type": "document",
      "processed_at": 1714938000
    }
  }
}
```

#### List All Documents

```http
GET /api/documents
```

Get detailed information about all documents in the RAG system.

Example using cURL:
```bash
curl -X GET "http://localhost:8000/api/documents"
```

Example using Python:
```python
import requests

response = requests.get("http://localhost:8000/api/documents")
print(response.json())
```

**Response:**
```json
{
  "count": 2,
  "filenames": [
    "executive_summary.pdf",
    "quarterly_report.pdf"
  ]
}
```

#### Delete a Document

```http
DELETE /api/documents/{filename}
```

Delete a specific document and all its chunks from the RAG system.

Example using cURL:
```bash
curl -X DELETE "http://localhost:8000/api/documents/quarterly_report.pdf"
```

Example using Python:
```python
import requests

response = requests.delete("http://localhost:8000/api/documents/quarterly_report.pdf")
print(response.json())
```

**Response:**
```json
{
  "status": "success",
  "message": "Deleted document quarterly_report.pdf with 8 chunks"
}
```

#### Reset RAG System

```http
POST /api/system/reset
```

Reset the entire RAG system, deleting all documents and clearing the vector store.

**Request:**
- Query Parameters:
  - `confirm`: Set to `true` to confirm the reset action (Required)

Example using cURL:
```bash
curl -X POST "http://localhost:8000/api/system/reset?confirm=true"
```

Example using Python:
```python
import requests

response = requests.post("http://localhost:8000/api/system/reset", params={"confirm": "true"})
print(response.json())
```

**Response:**
```json
{
  "status": "success",
  "message": "RAG system reset successfully. All documents and indices have been removed."
}
```

### 5. Configuration Management

#### Get Service Mapping Configuration

```http
GET /api/config/mapping
```

Get the current service mapping configuration.

Example using cURL:
```bash
curl -X GET "http://localhost:8000/api/config/mapping"
```

Example using Python:
```python
import requests

response = requests.get("http://localhost:8000/api/config/mapping")
print(response.json())
```

**Response:**
```json
{
  "audio": {
    "extensions": [".mp3", ".wav", ".flac", ".m4a"],
    "service_endpoint": "http://127.0.0.1:5000",
    "content_type": "audio"
  },
  "document": {
    "extensions": [".pdf", ".docx", ".txt", ".rtf", ".odt"],
    "service_endpoint": "http://document-transcription-service:8081/extract",
    "content_type": "document"
  },
  "image": {
    "extensions": [".jpg", ".jpeg", ".png", ".tiff", ".bmp"],
    "service_endpoint": "http://127.0.0.1:8089/",
    "content_type": "image"
  },
  "video": {
    "extensions": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
    "service_endpoint": "http://video-transcription-service:8083/transcribe",
    "content_type": "video"
  }
}
```

#### Reload Service Mapping Configuration

```http
POST /api/config/reload
```

Reload the service mapping configuration from disk.

Example using cURL:
```bash
curl -X POST "http://localhost:8000/api/config/reload"
```

Example using Python:
```python
import requests

response = requests.post("http://localhost:8000/api/config/reload")
print(response.json())
```

**Response:**
```json
{
  "status": "success",
  "message": "Configuration reloaded"
}
```

### 6. Model Management

#### List Available Models

```http
GET /api/models
```

List all available language models from the RAG system.

Example using cURL:
```bash
curl -X GET "http://localhost:8000/api/models"
```

Example using Python:
```python
import requests

response = requests.get("http://localhost:8000/api/models")
print(response.json())
```

**Response:**
```json
{
  "models": [
    "qwen2.5:3b-instruct",
    "qwen2.5:7b-instruct",
    "mistral:7b-instruct-v0.2",
    "llama2:13b-chat"
  ]
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

## Extending the Service

To add support for new file types:

1. Update the `service_mapping.json` file with new extensions and service endpoints
2. Implement any specialized metadata extraction in the `MetadataExtractor` class
3. Reload the configuration via the API endpoint or by restarting the service

## License

[MIT License](LICENSE)

