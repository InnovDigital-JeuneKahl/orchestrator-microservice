from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class AdditionalMetadata(BaseModel):
    meeting_title: Optional[str] = None
    department: Optional[str] = None
    participants: Optional[str] = None
    duration_minutes: Optional[int] = None
    transcription_quality: Optional[str] = None
    # Add any other fields as needed

class FileMetadata(BaseModel):
    filename: str
    file_type: str
    author: Optional[str] = None
    size_bytes: int
    additional_metadata: Optional[AdditionalMetadata] = None

class TranscriptionResponse(BaseModel):
    transcription: str
    metadata: FileMetadata

class QuestionAnsweringRequest(BaseModel):
    question: str

class RagRequest(BaseModel):
    # Empty as it only needs the file
    pass

class QueryRequest(BaseModel):
    query: str
    filter_metadata: Optional[Dict[str, Any]] = None
    model: str = "qwen2.5:3b-instruct"
    top_k: int = 3

class GenerateRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = "You are a helpful assistant."
    model: str = "qwen2.5:3b-instruct"
    temperature: float = 0.3
    max_tokens: int = 1500
    use_rag: bool = True
    top_k: int = 3

class KeywordSearchRequest(BaseModel):
    keywords: List[str]
    filter_metadata: Optional[Dict[str, Any]] = None
    model: str = "default_model"
    top_k: int = 3
    query: Optional[str] = None