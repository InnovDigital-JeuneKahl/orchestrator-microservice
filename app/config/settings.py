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