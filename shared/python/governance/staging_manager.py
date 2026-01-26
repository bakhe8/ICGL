"""
ICGL Staging Manager
====================

Manages the staging area for documentation refactoring.

This module provides strict governance over file operations:
- ONLY writes to /staging
- NEVER modifies /docs
- Full audit logging
- Session-based organization
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import shutil
import json

from ..kb.docs_schemas import RewritePlan, StagingManifest, GeneratedFile
from ..kb.schemas import uid, now
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class StagingManagerError(Exception):
    """Base exception for staging manager errors."""
    pass


class UnsafePathError(StagingManagerError):
    """Raised when a path attempts to escape staging."""
    pass


class StagingManager:
    """
    Manages staging area with strict governance.
    
    Governance Rules:
    - All writes go to /staging/docs/{session_id}/
    - NO writes to /docs allowed
    - Path validation for safety
    - Full audit logging
    - Session-based isolation
    """
    
    def __init__(self, staging_root: Path = None):
        """
        Initialize staging manager.
        
        Args:
            staging_root: Root staging directory (default: ./staging)
        """
        if staging_root is None:
            staging_root = Path("staging")
        
        self.staging_root = Path(staging_root)
        self.docs_staging = self.staging_root / "docs"
        
        # Create staging directories
        self.docs_staging.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"StagingManager initialized: {self.docs_staging}")
    
    def _validate_path(self, path: str) -> None:
        """
        Validate path for safety.
        
        Args:
            path: Relative path to validate
            
        Raises:
            UnsafePathError: If path is unsafe
        """
        # Check for path traversal
        if ".." in path:
            raise UnsafePathError(f"Path contains '..': {path}")
        
        # Check for absolute paths
        if path.startswith("/") or path.startswith("\\"):
            raise UnsafePathError(f"Absolute path not allowed: {path}")
        
        # Check for drive letters (Windows)
        if len(path) > 1 and path[1] == ":":
            raise UnsafePathError(f"Drive letter not allowed: {path}")
        
        # Ensure it's under docs
        if path.startswith("../") or path == "..":
            raise UnsafePathError(f"Path escapes staging: {path}")
    
    def write_to_staging(
        self, 
        plan: RewritePlan,
        session_id: Optional[str] = None
    ) -> StagingManifest:
        """
        Write generated files to staging area.
        
        Governance:
        - NEVER writes to /docs
        - Creates session subdirectory
        - Validates all paths
        - Logs all operations
        - Returns manifest for audit
        
        Args:
            plan: RewritePlan with generated files
            session_id: Optional session ID (generates if None)
            
        Returns:
            StagingManifest with operation details
            
        Raises:
            StagingManagerError: On validation or write errors
        """
        # Validate plan first
        is_valid, errors = plan.validate()
        if not is_valid:
            error_msg = f"Invalid RewritePlan: {', '.join(errors)}"
            logger.error(error_msg)
            raise StagingManagerError(error_msg)
        
        # Generate session ID if not provided
        if session_id is None:
            session_id = f"docs_{uid()}"
        
        logger.info(f"Starting staging session: {session_id}")
        
        # Create session directory
        session_dir = self.docs_staging / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        written_files: List[str] = []
        
        # Write each generated file
        for gen_file in plan.generated_files:
            try:
                # Validate path
                self._validate_path(gen_file.path)
                
                # Construct target path
                target_path = session_dir / gen_file.path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write file
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(gen_file.content)
                
                written_files.append(str(target_path.absolute()))
                logger.info(f"✅ Staged: {gen_file.path} -> {target_path}")
                
            except Exception as e:
                logger.error(f"❌ Failed to stage {gen_file.path}: {e}")
                raise StagingManagerError(f"Failed to write {gen_file.path}: {e}")
        
        # Create manifest
        manifest = StagingManifest(
            session_id=session_id,
            plan_summary=plan.summary,
            files_written=written_files,
            timestamp=now(),
            agent_id=plan.agent_id,
            confidence_score=plan.confidence_score
        )
        
        # Save manifest
        manifest_path = session_dir / "_manifest.json"
        manifest.save_to_file(manifest_path)
        logger.info(f"📋 Manifest saved: {manifest_path}")
        
        logger.info(f"✅ Staging complete: {len(written_files)} files written to {session_dir}")
        
        return manifest
    
    def list_sessions(self) -> List[str]:
        """
        List all staging sessions.
        
        Returns:
            List of session IDs
        """
        if not self.docs_staging.exists():
            return []
        
        sessions = []
        for item in self.docs_staging.iterdir():
            if item.is_dir():
                sessions.append(item.name)
        
        return sorted(sessions)
    
    def get_session_manifest(self, session_id: str) -> Optional[StagingManifest]:
        """
        Get manifest for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            StagingManifest or None if not found
        """
        manifest_path = self.docs_staging / session_id / "_manifest.json"
        
        if not manifest_path.exists():
            return None
        
        return StagingManifest.from_file(manifest_path)
    
    def list_staged_files(self, session_id: str) -> List[Path]:
        """
        List all files in a staging session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of file paths
        """
        session_dir = self.docs_staging / session_id
        
        if not session_dir.exists():
            return []
        
        files = []
        for filepath in session_dir.rglob("*.md"):
            files.append(filepath)
        
        return sorted(files)
    
    def clear_session(self, session_id: str) -> None:
        """
        Remove a staging session.
        
        Args:
            session_id: Session identifier
        """
        session_dir = self.docs_staging / session_id
        
        if session_dir.exists():
            shutil.rmtree(session_dir)
            logger.info(f"🗑️  Cleared staging session: {session_id}")
        else:
            logger.warning(f"Session not found: {session_id}")
    
    def clear_all_staging(self, confirm: bool = False) -> None:
        """
        Clear ALL staging data.
        
        Args:
            confirm: Must be True to proceed (safety check)
        """
        if not confirm:
            raise StagingManagerError("Must confirm to clear all staging")
        
        if self.docs_staging.exists():
            shutil.rmtree(self.docs_staging)
            self.docs_staging.mkdir(parents=True, exist_ok=True)
            logger.warning("🗑️  Cleared ALL staging data")
    
    def get_staging_stats(self) -> Dict[str, Any]:
        """
        Get statistics about staging area.
        
        Returns:
            Dictionary with statistics
        """
        sessions = self.list_sessions()
        total_files = 0
        total_size = 0
        
        for session_id in sessions:
            files = self.list_staged_files(session_id)
            total_files += len(files)
            for filepath in files:
                total_size += filepath.stat().st_size
        
        return {
            "total_sessions": len(sessions),
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "sessions": sessions
        }
