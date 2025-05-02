
import os
from typing import Dict, Any, Optional
import filetype
import mimetypes
from datetime import datetime
from app.models.schemas import FileMetadata, AdditionalMetadata

class MetadataExtractor:
    def extract_metadata(
        self, 
        filename: str, 
        file_content: bytes, 
        content_type: str,
        user_metadata: Optional[Dict[str, Any]] = None
    ) -> FileMetadata:
        """
        Extract metadata from a file.
        
        Args:
            filename: The name of the file
            file_content: The binary content of the file
            content_type: The type of content (audio, document, etc.)
            user_metadata: Optional user-provided metadata
            
        Returns:
            FileMetadata object with extracted information
        """
        # Basic metadata
        size_bytes = len(file_content)
        
        # Initialize additional metadata
        additional_metadata = {}
        
        # Merge user-provided metadata if available
        if user_metadata:
            author = user_metadata.get("author")
            if "additional_metadata" in user_metadata:
                additional_metadata.update(user_metadata["additional_metadata"])
        else:
            author = None
        
        # Try to get MIME type using filetype instead of magic
        kind = filetype.guess(file_content)
        mime_type = kind.mime if kind else mimetypes.guess_type(filename)[0] or "application/octet-stream"
        
        # Add content-type specific metadata
        if content_type == "audio":
            # For audio files we might want duration, etc.
            # This would require audio processing libraries in a real implementation
            if "duration_minutes" not in additional_metadata:
                # Placeholder - in a real implementation we would extract this
                additional_metadata["duration_minutes"] = None
                
        elif content_type == "document":
            # For documents we might want page count, etc.
            # This would require document processing libraries
            pass
            
        # Create and return the metadata object
        return FileMetadata(
            filename=filename,
            file_type=content_type,
            author=author,
            size_bytes=size_bytes,
            additional_metadata=AdditionalMetadata(**additional_metadata) if additional_metadata else None
        )