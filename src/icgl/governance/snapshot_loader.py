"""
ICGL Documentation Snapshot Loader
===================================

Loads documentation files into a structured snapshot for analysis.

This module provides read-only access to documentation:
- NO file modifications
- NO writes
- Full metadata capture
- Error handling for encoding issues
"""

from pathlib import Path
from typing import List, Optional
from datetime import datetime

from ..kb.docs_schemas import DocumentFile, DocumentSnapshot
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class SnapshotLoaderError(Exception):
    """Base exception for snapshot loader errors."""
    pass


class DocsSnapshotLoader:
    """
    Loads documentation snapshot (read-only).
    
    Governance:
    - Read-only operations ONLY
    - NO file modifications
    - Handles errors gracefully
    - Full metadata capture
    """
    
    def __init__(self, docs_path: Path = None):
        """
        Initialize snapshot loader.
        
        Args:
            docs_path: Path to docs directory (default: ./docs)
        """
        if docs_path is None:
            docs_path = Path("docs")
        
        self.docs_path = Path(docs_path)
        
        if not self.docs_path.exists():
            raise SnapshotLoaderError(f"Documentation path not found: {self.docs_path}")
        
        if not self.docs_path.is_dir():
            raise SnapshotLoaderError(f"Path is not a directory: {self.docs_path}")
        
        logger.info(f"DocsSnapshotLoader initialized: {self.docs_path}")
    
    def load_snapshot(self, file_ext: str = "*.md") -> DocumentSnapshot:
        """
        Load all documentation files into a structured snapshot.
        
        Args:
            file_ext: File extension glob pattern (default: *.md)
            
        Returns:
            DocumentSnapshot with all files and metadata
            
        Raises:
            SnapshotLoaderError: On critical errors
        """
        logger.info(f"Loading documentation snapshot from {self.docs_path}")
        
        files: List[DocumentFile] = []
        total_size = 0
        errors = []
        
        # Find all matching files
        file_paths = list(self.docs_path.rglob(file_ext))
        logger.info(f"Found {len(file_paths)} files matching {file_ext}")
        
        for filepath in file_paths:
            try:
                # Read file content
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Get file metadata
                stat = filepath.stat()
                relative_path = filepath.relative_to(self.docs_path)
                
                # Create DocumentFile
                doc_file = DocumentFile(
                    path=str(relative_path).replace("\\", "/"),  # Normalize path separators
                    content=content,
                    size_bytes=stat.st_size,
                    modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat()
                )
                
                files.append(doc_file)
                total_size += stat.st_size
                
                logger.debug(f"Loaded: {relative_path} ({stat.st_size} bytes)")
                
            except UnicodeDecodeError as e:
                error_msg = f"Encoding error in {filepath}: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)
                # Skip this file but continue
                
            except Exception as e:
                error_msg = f"Failed to load {filepath}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
                # Skip this file but continue
        
        # Log any errors encountered
        if errors:
            logger.warning(f"Encountered {len(errors)} errors during snapshot loading")
        
        # Create snapshot
        snapshot = DocumentSnapshot(
            files=files,
            snapshot_time=datetime.now().isoformat(),
            total_files=len(files),
            total_size_bytes=total_size,
            docs_root=str(self.docs_path.absolute())
        )
        
        logger.info(f"✅ Snapshot loaded: {len(files)} files, "
                   f"{total_size:,} bytes ({total_size / 1024:.1f} KB)")
        
        return snapshot
    
    def get_file_tree_summary(self, snapshot: DocumentSnapshot) -> str:
        """
        Generate a text summary of the file tree.
        
        Args:
            snapshot: DocumentSnapshot to summarize
            
        Returns:
            Formatted tree structure as string
        """
        lines = ["Documentation File Tree:", ""]
        
        # Sort files by path
        sorted_files = sorted(snapshot.files, key=lambda f: f.path)
        
        for doc_file in sorted_files:
            # Simple tree representation
            depth = doc_file.path.count("/")
            indent = "  " * depth
            filename = doc_file.path.split("/")[-1]
            size_kb = doc_file.size_bytes / 1024
            
            lines.append(f"{indent}├─ {filename} ({size_kb:.1f} KB)")
        
        lines.append("")
        lines.append(f"Total: {snapshot.total_files} files, "
                    f"{snapshot.total_size_bytes / 1024:.1f} KB")
        
        return "\n".join(lines)
    
    def get_content_summary(self, snapshot: DocumentSnapshot, max_chars: int = 200) -> str:
        """
        Generate a content summary for LLM context.
        
        Args:
            snapshot: DocumentSnapshot to summarize
            max_chars: Maximum characters per file summary
            
        Returns:
            Formatted content summary
        """
        lines = ["Documentation Content Summary:", ""]
        
        for doc_file in snapshot.files:
            # File header
            lines.append(f"📄 {doc_file.path}")
            
            # First N characters of content
            content_preview = doc_file.content[:max_chars].strip()
            if len(doc_file.content) > max_chars:
                content_preview += "..."
            
            lines.append(f"   {content_preview}")
            lines.append("")
        
        return "\n".join(lines)
