"""
ICGL Documentation Schemas
===========================

Schemas for the governed documentation refactor pipeline.

This module defines the data structures used throughout the documentation
pipeline, ensuring type safety and validation.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path


@dataclass
class DocumentFile:
    """Represents a single documentation file in the snapshot."""
    path: str  # Relative path from docs root
    content: str  # Full file content
    size_bytes: int  # File size
    modified_at: str  # ISO timestamp of last modification
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DocumentSnapshot:
    """
    Complete snapshot of documentation files.
    
    This is a read-only representation of the current documentation state,
    passed to agents for analysis.
    """
    files: List[DocumentFile]
    snapshot_time: str  # ISO timestamp
    total_files: int
    total_size_bytes: int
    docs_root: str  # Path where docs were read from
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "files": [f.to_dict() for f in self.files],
            "snapshot_time": self.snapshot_time,
            "total_files": self.total_files,
            "total_size_bytes": self.total_size_bytes,
            "docs_root": self.docs_root
        }
    
    def get_file_tree(self) -> List[str]:
        """Get sorted list of all file paths."""
        return sorted([f.path for f in self.files])


@dataclass
class ProposedFile:
    """A file structure proposed by DocumentationAgent."""
    path: str  # Relative path
    purpose: str  # What this file explains
    content_outline: List[str]  # High-level sections/topics
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class GeneratedFile:
    """A fully generated file ready for staging."""
    path: str  # Relative path
    content: str  # Complete markdown content
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate generated file.
        
        Returns:
            (is_valid, error_message)
        """
        # Path validation
        if not self.path:
            return False, "Path cannot be empty"
        
        if ".." in self.path or self.path.startswith("/"):
            return False, f"Unsafe path: {self.path}"
        
        if not self.path.endswith(".md"):
            return False, f"Only markdown files allowed: {self.path}"
        
        # Content validation
        if not self.content or len(self.content.strip()) == 0:
            return False, f"Content cannot be empty for {self.path}"
        
        return True, None


@dataclass
class RewritePlan:
    """
    DocumentationAgent's complete output schema.
    
    This is the structured result of agent analysis, containing:
    - Analysis summary and detected issues
    - Proposed new structure
    - Fully generated content
    - Risk assessment
    
    Governance: This object is validated before staging.
    """
    summary: str  # Brief analysis summary
    issues: List[str]  # Detected documentation issues
    proposed_structure: List[ProposedFile]  # Proposed file organization
    generated_files: List[GeneratedFile]  # Complete generated files
    risk_notes: List[str]  # Potential risks or breaking changes
    agent_id: str  # Agent that created this plan
    created_at: str  # ISO timestamp
    confidence_score: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "summary": self.summary,
            "issues": self.issues,
            "proposed_structure": [p.to_dict() for p in self.proposed_structure],
            "generated_files": [g.to_dict() for g in self.generated_files],
            "risk_notes": self.risk_notes,
            "agent_id": self.agent_id,
            "created_at": self.created_at,
            "confidence_score": self.confidence_score
        }
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate the entire plan.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Required fields
        if not self.summary:
            errors.append("Summary is required")
        
        if not self.agent_id:
            errors.append("Agent ID is required")
        
        # Confidence score
        if not (0.0 <= self.confidence_score <= 1.0):
            errors.append(f"Confidence score must be 0-1, got {self.confidence_score}")
        
        # Validate generated files
        if not self.generated_files:
            errors.append("At least one generated file is required")
        else:
            for i, gen_file in enumerate(self.generated_files):
                is_valid, error = gen_file.validate()
                if not is_valid:
                    errors.append(f"Generated file {i}: {error}")
        
        # Check for duplicate paths
        paths = [g.path for g in self.generated_files]
        if len(paths) != len(set(paths)):
            errors.append("Duplicate file paths detected")
        
        return len(errors) == 0, errors
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RewritePlan':
        """Create RewritePlan from dictionary (e.g., from LLM JSON)."""
        return cls(
            summary=data.get("summary", ""),
            issues=data.get("issues", []),
            proposed_structure=[
                ProposedFile(**p) for p in data.get("proposed_structure", [])
            ],
            generated_files=[
                GeneratedFile(**g) for g in data.get("generated_files", [])
            ],
            risk_notes=data.get("risk_notes", []),
            agent_id=data.get("agent_id", "unknown"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            confidence_score=data.get("confidence_score", 0.5)
        )


@dataclass
class StagingManifest:
    """
    Manifest file created for each staging session.
    
    This provides audit trail and metadata for staged content.
    """
    session_id: str
    plan_summary: str
    files_written: List[str]  # Absolute paths
    timestamp: str  # ISO timestamp
    agent_id: str
    confidence_score: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def save_to_file(self, path: Path) -> None:
        """Save manifest as JSON file."""
        import json
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def from_file(cls, path: Path) -> 'StagingManifest':
        """Load manifest from JSON file."""
        import json
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)
