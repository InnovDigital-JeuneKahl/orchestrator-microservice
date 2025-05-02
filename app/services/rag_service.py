

import httpx
from typing import Dict, Any
import logging
from fastapi import HTTPException
from app.models.schemas import FileMetadata, TranscriptionResponse, QueryRequest, GenerateRequest

logger = logging.getLogger(__name__)

class RagService:
    def __init__(self, rag_api_url: str = "http://localhost:8000"):
        self.rag_api_url = rag_api_url
        
    async def process_transcription(self, transcription: str, metadata: FileMetadata) -> Dict[str, Any]:
        """
        Send the transcription and metadata to the RAG API for processing.
        
        Args:
            transcription: The transcription text
            metadata: The file metadata
            
        Returns:
            The RAG API response
        """
        try:
            payload = TranscriptionResponse(
                transcription=transcription,
                metadata=metadata
            )
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.rag_api_url}/process-transcription",
                    json=payload.dict(),
                    timeout=30.0
                )
                
            if response.status_code != 200:
                logger.error(f"RAG API error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"RAG API error: {response.text}"
                )
                
            return response.json()
            
        except httpx.RequestError as e:
            logger.error(f"Error connecting to RAG API: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Error connecting to RAG API: {str(e)}"
            )
    
    async def query_rag(self, query_request: QueryRequest) -> Dict[str, Any]:
        """
        Query the RAG API with the given request.
        
        Args:
            query_request: The query request object
            
        Returns:
            The RAG API response
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.rag_api_url}/query",
                    json=query_request.dict(),
                    timeout=30.0
                )
                
            if response.status_code != 200:
                logger.error(f"RAG query error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"RAG query error: {response.text}"
                )
                
            return response.json()
            
        except httpx.RequestError as e:
            logger.error(f"Error connecting to RAG API: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Error connecting to RAG API: {str(e)}"
            )
    
    async def generate(self, generate_request: GenerateRequest) -> Dict[str, Any]:
        """
        Send a generation request to the RAG API.
        
        Args:
            generate_request: The generation request object
            
        Returns:
            The RAG API response
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.rag_api_url}/generate",
                    json=generate_request.dict(),
                    timeout=60.0
                )
                
            if response.status_code != 200:
                logger.error(f"RAG generation error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"RAG generation error: {response.text}"
                )
                
            return response.json()
            
        except httpx.RequestError as e:
            logger.error(f"Error connecting to RAG API: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Error connecting to RAG API: {str(e)}"
            )