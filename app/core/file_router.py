import os
import json
from typing import Dict, Any, Tuple, Optional
from fastapi import HTTPException
import httpx
import logging

logger = logging.getLogger(__name__)

class FileRouter:
    def __init__(self, config_path: str = "config/service_mapping.json"):
        self.config_path = config_path
        self.service_mapping = self._load_service_mapping()
        
    def _load_service_mapping(self) -> Dict[str, Any]:
        """Load the service mapping configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load service mapping: {str(e)}")
            # Provide default minimal configuration if file can't be loaded
            return {
                "document": {
                    "extensions": [".pdf", ".docx", ".txt"],
                    "service_endpoint": "http://document-service:8081/extract",
                    "content_type": "document"
                },
                "audio": {
                    "extensions": [".mp3", ".wav"],
                    "service_endpoint": "http://127.0.0.1:5000/transcribe",
                    "content_type": "audio"
                }
            }
    
    def reload_mapping(self) -> None:
        """Reload the service mapping from the config file."""
        self.service_mapping = self._load_service_mapping()
        
    def get_service_for_file(self, filename: str) -> Tuple[str, str]:
        """
        Determine the appropriate service endpoint for the given file.
        
        Args:
            filename: The name of the file to route
            
        Returns:
            Tuple of (service_endpoint, content_type)
            
        Raises:
            HTTPException: If no matching service is found for the file extension
        """
        _, extension = os.path.splitext(filename.lower())
        
        for service_type, config in self.service_mapping.items():
            if extension in config["extensions"]:
                return config["service_endpoint"], config["content_type"]
        
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {extension}. Supported types: "
                   f"{[ext for config in self.service_mapping.values() for ext in config['extensions']]}"
        )
    
    
    async def send_to_transcription_service(
        self, 
        service_endpoint: str, 
        file_content: bytes, 
        filename: str
    ) -> str:
        """
        Send the file to the appropriate transcription service.
        
        Args:
            service_endpoint: The API endpoint of the transcription service
            file_content: The binary content of the file
            filename: The name of the file
            
        Returns:
            The transcription result
            
        Raises:
            HTTPException: If the transcription service returns an error
        """
        try:
            files = {"file": (filename, file_content)}
            service_endpoint = f"{service_endpoint.rstrip('/')}/transcribe"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    service_endpoint,
                    files=files,
                    timeout=100.0  # Longer timeout for transcription
                )
                
            if response.status_code != 200:
                logger.error(f"Transcription service error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Transcription service error: {response.text}"
                )
            
            # Handle different response formats based on the service
            result = response.json()
            
            # OCR service returns text in an array of paragraphs
            if "text" in result and isinstance(result["text"], list):
                return "\n\n".join(result["text"])
            
            # Some services might return the transcription directly
            if "transcription" in result:
                return result["transcription"]
            
            # If the response is just text
            if isinstance(result, str):
                return result
            
            # Default fallback
            return str(result)
        
        except httpx.RequestError as e:
            logger.error(f"Error connecting to transcription service: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Error connecting to transcription service: {str(e)}"
            )
    
    async def send_to_search_service(
        self, 
        service_endpoint: str, 
        file_content: bytes, 
        filename: str, 
        search_terms: str
    ) -> dict:
        """
        Send a search request to the appropriate service.
        
        Args:
            service_endpoint: The base service endpoint
            file_content: The file content as bytes
            filename: The name of the file
            search_terms: Comma-separated search terms
            
        Returns:
            The search results
        """
        search_endpoint = f"{service_endpoint.rstrip('/')}/search"
        
        try:
            async with httpx.AsyncClient() as client:
                files = {"file": (filename, file_content)}
                data = {"searchTerm": search_terms}
                
                response = await client.post(
                    search_endpoint,
                    files=files,
                    data=data,
                    timeout=60.0
                )
            
            if response.status_code != 200:
                logger.error(f"Search service error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Search service error: {response.text}"
                )
            
            # Handle line-delimited JSON responses (NDJSON format)
            results = []
            contexts = []
            
            # Process each line as a separate JSON object
            for line in response.text.splitlines():
                if not line.strip():
                    continue
                    
                try:
                    json_obj = json.loads(line)
                    
                    # Collect match objects which contain the search results with context
                    if json_obj.get("type") == "match":
                        match_obj = json_obj.get("match", {})
                        context_obj = json_obj.get("context", {})
                        
                        results.append({
                            "text": match_obj.get("text", ""),
                            "timestamp_start": match_obj.get("start"),
                            "timestamp_end": match_obj.get("end"),
                            "context": {
                                "before": " ".join([seg.get("text", "") for seg in context_obj.get("before", [])]),
                                "current": match_obj.get("text", ""),
                                "after": " ".join([seg.get("text", "") for seg in context_obj.get("after", [])])
                            }
                        })
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON line: {line}")
                    continue
            
            return {
                "results": results,
                "count": len(results)
            }
            
        except httpx.RequestError as e:
            logger.error(f"Error connecting to search service: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Error connecting to search service: {str(e)}"
            )