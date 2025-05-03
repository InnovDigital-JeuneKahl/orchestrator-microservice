
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from typing import Optional, Dict, Any
import json

from app.core.file_router import FileRouter
from app.core.metadata_extractor import MetadataExtractor
from app.services.rag_service import RagService
from app.models.schemas import QuestionAnsweringRequest, QueryRequest, GenerateRequest, KeywordSearchRequest

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
    processed_files = await rag_service.get_processed_files()
    # Check if the file has already been processed
    print(f"Processed files: {processed_files}")
    file_already_processed = file.filename in processed_files

    if file_already_processed:
        print(f"File {file.filename} already processed. Skipping transcription.")
        return {
            "filename": file.filename,
            "status": "already_processed",
            "message": "File has already been processed."
        }
    
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

@router.get("/processed-files")
async def get_processed_files(rag_service: RagService = Depends(get_rag_service)):
    """Get list of processed files from the RAG system."""
    processed_files = await rag_service.get_processed_files()
    return {"files": processed_files}

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
    processed_files = await rag_service.get_processed_files()
    file_already_processed = file.filename in processed_files

    print(f"File already processed: {file_already_processed}")
    if file_already_processed:
        print(f"File {file.filename} already processed. Skipping transcription.")

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
    
    if not file_already_processed:
        # Send to transcription service
        transcription = await file_router.send_to_transcription_service(
            service_endpoint=service_endpoint,
            file_content=file_content,
            filename=file.filename
        )
        
        # Process with RAG service to store the document
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

@router.post("/search")
async def search_in_file(
    file: UploadFile = File(...),
    search_terms: str = Form(...),
    file_router: FileRouter = Depends(get_file_router)
):
    """
    Search for specific terms within a file and get context.
    
    Args:
        file: The file to search within
        search_terms: Comma-separated list of terms to search for
        
    Returns:
        Search results with context around each match
    """
    # Read file content
    file_content = await file.read()
    
    # Determine the appropriate service
    service_endpoint, content_type = file_router.get_service_for_file(file.filename)
    
    # Send search request to the appropriate service
    search_results = await file_router.send_to_search_service(
        service_endpoint=service_endpoint,
        file_content=file_content,
        filename=file.filename,
        search_terms=search_terms
    )
    
    return {
        "filename": file.filename,
        "file_type": content_type,
        "search_terms": search_terms,
        "results": search_results.get("results", []),
        "count": search_results.get("count", 0)
    }


@router.get("/documents")
async def list_documents(rag_service: RagService = Depends(get_rag_service)):
    """Get a list of all documents in the RAG system."""
    documents = await rag_service.list_documents()
    return documents

@router.delete("/documents/{filename}")
async def delete_document(
    filename: str,
    rag_service: RagService = Depends(get_rag_service)
):
    """Delete a document from the RAG system."""
    result = await rag_service.delete_document(filename)
    return result

@router.post("/keyword-search")
async def keyword_search(
    request: KeywordSearchRequest,
    rag_service: RagService = Depends(get_rag_service)
):
    """Perform a keyword search in the RAG system."""
    search_results = await rag_service.keyword_search(request)
    return search_results

@router.post("/system/reset")
async def reset_system(
    confirm: bool = False,
    rag_service: RagService = Depends(get_rag_service)
):
    """Reset the entire RAG system."""
    result = await rag_service.reset_system(confirm)
    return result

@router.get("/models")
async def list_models(rag_service: RagService = Depends(get_rag_service)):
    """List available models from the RAG system."""
    models = await rag_service.list_models()
    return models