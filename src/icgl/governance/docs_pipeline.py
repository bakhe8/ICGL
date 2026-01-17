"""
ICGL Documentation Refactor Pipeline
=====================================

Orchestrates the governed documentation refactor workflow.

Pipeline Stages:
1. Snapshot: Load current docs (read-only)
2. Analyze: DocumentationAgent proposes improvements
3. Stage: Write to /staging (never /docs)
4. Review: Human approval gate
5. Promote: Manual (no auto-commit)

Governance:
- Full audit trail
- No auto-modifications
- Requires human approval
- Safe failures
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
import difflib

from ..governance.snapshot_loader import DocsSnapshotLoader
from ..governance.staging_manager import StagingManager
from ..agents.documentation_agent import DocumentationAgent
from ..kb.docs_schemas import DocumentSnapshot, RewritePlan, StagingManifest
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class DocsRefactorPipeline:
    """
    Orchestrates the governed documentation refactor pipeline.
    
    This is the main entry point for documentation improvement workflows.
    """
    
    def __init__(
        self,
        docs_path: Path = None,
        staging_root: Path = None
    ):
        """
        Initialize pipeline components.
        
        Args:
            docs_path: Path to documentation (default: ./docs)
            staging_root: Path to staging area (default: ./staging)
        """
        self.loader = DocsSnapshotLoader(docs_path)
        self.agent = DocumentationAgent()
        self.staging = StagingManager(staging_root)
        
        # Pipeline state
        self.current_snapshot: Optional[DocumentSnapshot] = None
        self.current_plan: Optional[RewritePlan] = None
        self.current_manifest: Optional[StagingManifest] = None
        
        logger.info("DocsRefactorPipeline initialized")
    
    def load_snapshot(self) -> DocumentSnapshot:
        """
        Phase 1: Load documentation snapshot.
        
        Returns:
            DocumentSnapshot with all current docs
        """
        logger.info("🔷 Phase 1: Loading documentation snapshot...")
        
        snapshot = self.loader.load_snapshot()
        self.current_snapshot = snapshot
        
        logger.info(f"✅ Snapshot loaded: {snapshot.total_files} files, "
                   f"{snapshot.total_size_bytes / 1024:.1f} KB")
        
        return snapshot
    
    async def analyze(
        self, 
        snapshot: Optional[DocumentSnapshot] = None,
        focus_areas: Optional[List[str]] = None
    ) -> RewritePlan:
        """
        Phase 2: Run DocumentationAgent analysis.
        
        Args:
            snapshot: Snapshot to analyze (uses current if None)
            focus_areas: Optional specific areas to focus on
            
        Returns:
            RewritePlan with agent's analysis and proposals
        """
        logger.info("🔷 Phase 2: Running DocumentationAgent analysis...")
        
        if snapshot is None:
            if self.current_snapshot is None:
                raise ValueError("No snapshot loaded. Call load_snapshot() first.")
            snapshot = self.current_snapshot
        
        plan = await self.agent.analyze_docs(snapshot, focus_areas)
        self.current_plan = plan
        
        logger.info(f"✅ Analysis complete. Confidence: {plan.confidence_score:.2%}")
        logger.info(f"   Issues detected: {len(plan.issues)}")
        logger.info(f"   Files to generate: {len(plan.generated_files)}")
        
        return plan
    
    def stage_files(
        self, 
        plan: Optional[RewritePlan] = None,
        session_id: Optional[str] = None
    ) -> StagingManifest:
        """
        Phase 3: Stage generated files.
        
        Args:
            plan: RewritePlan to stage (uses current if None)
            session_id: Optional session ID
            
        Returns:
            StagingManifest with staging details
        """
        logger.info("🔷 Phase 3: Staging generated files...")
        
        if plan is None:
            if self.current_plan is None:
                raise ValueError("No plan available. Call analyze() first.")
            plan = self.current_plan
        
        manifest = self.staging.write_to_staging(plan, session_id)
        self.current_manifest = manifest
        
        logger.info(f"✅ Staged {len(manifest.files_written)} files")
        logger.info(f"   Session ID: {manifest.session_id}")
        
        return manifest
    
    def get_diff(self, staged_path: str, original_path: str = None) -> Optional[str]:
        """
        Generate diff between staged file and original (if exists).
        
        Args:
            staged_path: Path to staged file
            original_path: Path in original docs (inferred if None)
            
        Returns:
            Unified diff string or None if original doesn't exist
        """
        staged_file = Path(staged_path)
        
        if not staged_file.exists():
            return None
        
        # Infer original path if not provided
        if original_path is None:
            # Extract relative path from staged path
            # Try to find the session directory pattern
            try:
                # Get relative path from staging root
                staging_root = self.staging.docs_staging
                rel_from_staging = staged_file.relative_to(staging_root)
                
                # Parts after session_id
                parts = rel_from_staging.parts
                if len(parts) > 1:
                    # Skip session_id (first part), rest is relative path
                    relative_path = Path(*parts[1:])
                    original_path = self.loader.docs_path / relative_path
                else:
                    return f"NEW FILE: {staged_path}\n(No original to compare)"
                    
            except ValueError:
                # Can't determine relative path
                return f"NEW FILE: {staged_path}\n(Path resolution failed)"
        else:
            original_path = Path(original_path)
        
        # Check if original exists
        if not original_path.exists():
            return f"NEW FILE: {staged_path}\n(No original to compare)"
        
        # Read both files
        with open(original_path, 'r', encoding='utf-8') as f:
            original_lines = f.readlines()
        
        with open(staged_file, 'r', encoding='utf-8') as f:
            staged_lines = f.readlines()
        
        # Generate unified diff
        diff = difflib.unified_diff(
            original_lines,
            staged_lines,
            fromfile=str(original_path),
            tofile=str(staged_path),
            lineterm=''
        )
        
        return '\n'.join(diff)
    
    def show_diffs(self, session_id: str) -> Dict[str, str]:
        """
        Show diffs for all staged files in a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary mapping file paths to their diffs
        """
        logger.info(f"Generating diffs for session: {session_id}")
        
        staged_files = self.staging.list_staged_files(session_id)
        diffs = {}
        
        for staged_file in staged_files:
            diff = self.get_diff(str(staged_file))
            if diff:
                diffs[str(staged_file)] = diff
        
        logger.info(f"Generated {len(diffs)} diffs")
        
        return diffs
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear a staging session (REJECT action).
        
        Args:
            session_id: Session identifier
        """
        logger.info(f"Clearing session: {session_id}")
        self.staging.clear_session(session_id)
        logger.info("✅ Session cleared")
    
    def get_promotion_instructions(self, session_id: str) -> str:
        """
        Get instructions for manually promoting staged files.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Shell commands for promotion
        """
        session_dir = self.staging.docs_staging / session_id
        docs_path = self.loader.docs_path
        
        instructions = f"""
To promote staged documentation to production:

1. Review the staged files:
   cd {session_dir}
   
2. Copy to production (BE CAREFUL):
   cp -r * {docs_path}/
   
3. Commit changes:
   cd {docs_path.parent}
   git add docs/
   git commit -m "docs: apply ICGL refactor {session_id}"
   git push
   
4. Clean up staging (optional):
   icgl docs clear-session {session_id}

⚠️  WARNING: This will OVERWRITE existing documentation files!
    Make sure you have reviewed the changes carefully.
"""
        return instructions
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current pipeline state.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            "snapshot_loaded": self.current_snapshot is not None,
            "analysis_complete": self.current_plan is not None,
            "files_staged": self.current_manifest is not None,
            "staging_stats": self.staging.get_staging_stats()
        }
        
        if self.current_snapshot:
            stats["snapshot"] = {
                "total_files": self.current_snapshot.total_files,
                "total_size_kb": self.current_snapshot.total_size_bytes / 1024
            }
        
        if self.current_plan:
            stats["plan"] = {
                "confidence": self.current_plan.confidence_score,
                "issues_count": len(self.current_plan.issues),
                "generated_files_count": len(self.current_plan.generated_files)
            }
        
        if self.current_manifest:
            stats["manifest"] = {
                "session_id": self.current_manifest.session_id,
                "files_written": len(self.current_manifest.files_written)
            }
        
        return stats
