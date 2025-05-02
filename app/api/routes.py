
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from typing import Optional, Dict, Any
import json

from app.core.file_router import FileRouter
from app.core.metadata_extractor import MetadataExtractor
from app.services.rag_service import RagService
from app.models.schemas import QuestionAnsweringRequest, QueryRequest, GenerateRequest

router = APIRouter()

# Dependencies
def get_file_router():
    return FileRouter()

def get_metadata_extractor():
    return MetadataExtractor()

def get_rag_service():
    return RagService()

@router.post("/process")
async def process_file(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
    file_router: FileRouter = Depends(get_file_router),
    metadata_extractor: MetadataExtractor = Depends(get_metadata_extractor),
    rag_service: RagService = Depends(get_rag_service)
):
    """
    Process a file and add it to the RAG system.
    
    Args:
        file: The file to process
        metadata: Optional JSON string with additional metadata
        
    Returns:
        The processed file information
    """
    # Read file content
    file_content = await file.read()
    
    # Parse user metadata if provided
    user_metadata = json.loads(metadata) if metadata else None
    
    # Determine the appropriate service
    service_endpoint, content_type = file_router.get_service_for_file(file.filename)
    
    # Extract metadata
    file_metadata = metadata_extractor.extract_metadata(
        filename=file.filename,
        file_content=file_content,
        content_type=content_type,
        user_metadata=user_metadata
    )
    
    # Send to transcription service
    transcription = await file_router.send_to_transcription_service(
        service_endpoint=service_endpoint,
        file_content=file_content,
        filename=file.filename
    )
    
    # Process with RAG service
    rag_response = await rag_service.process_transcription(
        transcription=transcription,
        metadata=file_metadata
    )
    
    return {
        "filename": file.filename,
        "file_type": content_type,
        "size_bytes": file_metadata.size_bytes,
        "transcription_length": len(transcription),
        "rag_response": rag_response
    }

@router.post("/question")
async def ask_question(
    file: UploadFile = File(...),
    question: str = Form(...),
    metadata: Optional[str] = Form(None),
    file_router: FileRouter = Depends(get_file_router),
    metadata_extractor: MetadataExtractor = Depends(get_metadata_extractor),
    rag_service: RagService = Depends(get_rag_service)
):
    """
    Upload a file and ask a question about its content.
    
    Args:
        file: The file to process
        question: The question to answer
        metadata: Optional JSON string with additional metadata
        
    Returns:
        The answer to the question
    """
    # Read file content
    file_content = await file.read()
    
    # Parse user metadata if provided
    user_metadata = json.loads(metadata) if metadata else None
    
    # Determine the appropriate service
    service_endpoint, content_type = file_router.get_service_for_file(file.filename)
    
    # Extract metadata
    file_metadata = metadata_extractor.extract_metadata(
        filename=file.filename,
        file_content=file_content,
        content_type=content_type,
        user_metadata=user_metadata
    )
    
    # Send to transcription service
    transcription = await file_router.send_to_transcription_service(
        service_endpoint=service_endpoint,
        file_content=file_content,
        filename=file.filename
    )
    
    # First, process with RAG service to store the document
    await rag_service.process_transcription(
        transcription=transcription,
        metadata=file_metadata
    )
    
    # Then create a query request to ask the question
    query_request = QueryRequest(
        query=question,
        filter_metadata={"filename": file.filename},
        top_k=3
    )
    
    # Query the RAG system
    query_result = await rag_service.query_rag(query_request)
    
    # Finally, generate an answer based on the query results
    generate_request = GenerateRequest(
        prompt=question,
        system_prompt="Answer the question based on the provided document content.",
        use_rag=True,
        top_k=3
    )
    
    # Generate answer
    answer = await rag_service.generate(generate_request)
    
    return {
        "question": question,
        "answer": answer,
        "file_info": {
            "filename": file.filename,
            "file_type": content_type,
            "size_bytes": file_metadata.size_bytes
        },
        "relevant_passages": query_result.get("results", [])
    }

@router.get("/config/mapping")
async def get_service_mapping(file_router: FileRouter = Depends(get_file_router)):
    """Get the current service mapping configuration."""
    return file_router.service_mapping

@router.post("/config/reload")
async def reload_service_mapping(file_router: FileRouter = Depends(get_file_router)):
    """Reload the service mapping configuration from disk."""
    file_router.reload_mapping()
    return {"status": "success", "message": "Configuration reloaded"}