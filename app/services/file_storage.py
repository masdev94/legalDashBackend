import os
import uuid
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from loguru import logger
from app.core.config import UPLOAD_DIR
from app.models.document import Document

class FileStorage:
    
    def __init__(self):
        self.uploads_dir = Path(UPLOAD_DIR)
        self.uploads_dir.mkdir(exist_ok=True)
        # In-memory document storage (in production, this would be a database)
        self.documents: Dict[str, Document] = {}
        logger.info(f"File storage initialized at: {self.uploads_dir.absolute()}")
    
    def store_document(self, document: Document) -> str:
        """Store a document in memory and on disk"""
        try:
            # Store document metadata in memory
            self.documents[document.id] = document
            
            # Save file content to disk if it exists and is bytes
            if hasattr(document, 'content') and document.content:
                # Check if content is bytes (raw file data) or string (file path)
                if isinstance(document.content, bytes):
                    # Content is raw bytes, save it to disk
                    file_id, file_path = self.save_file(document.content, document.metadata.filename)
                    document.content = file_path
                    document.raw_bytes = document.content
                    logger.info(f"File content saved to disk: {file_path}")
                    
                    file_info = self.get_file_info(file_path)
                    if file_info:
                        logger.info(f"Stored file info: {file_info}")
                    
                elif isinstance(document.content, str):
                    # Content is already a file path, no need to save again
                    logger.info(f"Document content is already a file path: {document.content}")
                else:
                    logger.warning(f"Unexpected content type: {type(document.content)}")
            
            logger.info(f"Document stored: {document.id} - {document.metadata.filename}")
            return document.id
            
        except Exception as e:
            logger.error(f"Error storing document {document.id}: {str(e)}")
            raise
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """Retrieve a document by ID"""
        return self.documents.get(document_id)
    
    def get_all_documents(self) -> List[Document]:
        """Get all stored documents"""
        return list(self.documents.values())
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document from storage"""
        try:
            if document_id in self.documents:
                document = self.documents[document_id]
                
                # Delete file from disk if it exists
                if hasattr(document, 'content') and document.content:
                    self.delete_file(document.content)
                
                # Remove from memory
                del self.documents[document_id]
                
                logger.info(f"Document deleted: {document_id}")
                return True
            else:
                logger.warning(f"Document not found for deletion: {document_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            return False
    
    def get_document_count(self) -> int:
        """Get total number of stored documents"""
        return len(self.documents)
    
    def clear_all_documents(self) -> bool:
        """Clear all documents from storage"""
        try:
            # Delete all files from disk
            for document in self.documents.values():
                if hasattr(document, 'content') and document.content:
                    self.delete_file(document.content)
            
            # Clear memory
            self.documents.clear()
            
            logger.info("All documents cleared from storage")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing documents: {str(e)}")
            return False

    def save_file(self, file_content: bytes, original_filename: str) -> Tuple[str, str]:
        try:
            file_id = str(uuid.uuid4())
            
            file_extension = Path(original_filename).suffix
            if not file_extension:
                if original_filename.lower().endswith('pdf'):
                    file_extension = '.pdf'
                elif original_filename.lower().endswith(('doc', 'docx')):
                    file_extension = '.docx'
                elif original_filename.lower().endswith('txt'):
                    file_extension = '.txt'
                else:
                    file_extension = '.bin'
            
            filename = f"{file_id}{file_extension}"
            file_path = self.uploads_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(file_content)
                f.flush()
                os.fsync(f.fileno())
            
            logger.info(f"File saved: {original_filename} -> {file_path} ({len(file_content)} bytes)")
            return file_id, str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving file {original_filename}: {str(e)}")
            raise
    
    def get_file(self, file_path: str) -> Optional[bytes]:
        try:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                return None
            
            with open(file_path, 'rb') as f:
                content = f.read()
            
            logger.info(f"File retrieved: {file_path} ({len(content)} bytes)")
            return content
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            return {
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "exists": True
            }
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            return None
