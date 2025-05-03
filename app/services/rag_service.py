

import httpx
from typing import Dict, Any
import logging
from fastapi import HTTPException
from app.models.schemas import FileMetadata, TranscriptionResponse, QueryRequest, GenerateRequest, KeywordSearchRequest

logger = logging.getLogger(__name__)

class RagService:
    def __init__(self, rag_api_url: str = "http://127.0.0.1:8009"):
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
            print(f"Sending transcription to RAG API: {transcription[:50]}...")
            print(f"Metadata: {metadata}")
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

            print(response)
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
    
    async def get_processed_files(self) -> list:
        """
        Get a list of files that have been processed and stored in the RAG system.
        
        Returns:
            List of filenames that have been processed
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.rag_api_url}/processed-files",
                    timeout=10.0
                )
                
            if response.status_code != 200:
                logger.error(f"RAG API error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"RAG API error: {response.text}"
                )
                
            return response.json().get("files", [])
            
        except httpx.RequestError as e:
            logger.error(f"Error connecting to RAG API: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Error connecting to RAG API: {str(e)}"
            )
        
    async def keyword_search(self, keyword_request: KeywordSearchRequest) -> Dict[str, Any]:
        """
        Perform a keyword search in the RAG system.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.rag_api_url}/keyword-search",
                    json=keyword_request.dict(),
                    timeout=30.0
                )
                
            if response.status_code != 200:
                logger.error(f"RAG keyword search error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"RAG keyword search error: {response.text}"
                )
                
            return response.json()
            
        except httpx.RequestError as e:
            logger.error(f"Error connecting to RAG API: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Error connecting to RAG API: {str(e)}"
            )

    async def list_documents(self) -> Dict[str, Any]:
        """
        Get a list of all documents in the RAG system.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.rag_api_url}/documents",
                    timeout=10.0
                )
                
            if response.status_code != 200:
                logger.error(f"RAG documents listing error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"RAG documents listing error: {response.text}"
                )
                
            return response.json()
            
        except httpx.RequestError as e:
            logger.error(f"Error connecting to RAG API: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Error connecting to RAG API: {str(e)}"
            )

    async def delete_document(self, filename: str) -> Dict[str, Any]:
        """
        Delete a document from the RAG system.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.rag_api_url}/documents/{filename}",
                    timeout=10.0
                )
                
            if response.status_code != 200:
                logger.error(f"RAG document deletion error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"RAG document deletion error: {response.text}"
                )
                
            return response.json()
            
        except httpx.RequestError as e:
            logger.error(f"Error connecting to RAG API: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Error connecting to RAG API: {str(e)}"
            )

    async def reset_system(self, confirm: bool = False) -> Dict[str, Any]:
        """
        Reset the entire RAG system.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.rag_api_url}/system/reset",
                    params={"confirm": str(confirm).lower()},
                    timeout=30.0
                )
                
            if response.status_code != 200:
                logger.error(f"RAG system reset error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"RAG system reset error: {response.text}"
                )
                
            return response.json()
            
        except httpx.RequestError as e:
            logger.error(f"Error connecting to RAG API: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Error connecting to RAG API: {str(e)}"
            )

    async def list_models(self) -> Dict[str, Any]:
        """
        List available models from the RAG system.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.rag_api_url}/models",
                    timeout=10.0
                )
                
            if response.status_code != 200:
                logger.error(f"RAG models listing error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"RAG models listing error: {response.text}"
                )
                
            return response.json()
            
        except httpx.RequestError as e:
            logger.error(f"Error connecting to RAG API: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Error connecting to RAG API: {str(e)}"
            )