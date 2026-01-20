import os
import time
from pathlib import Path
from typing import Optional, List
from fastapi import Header, HTTPException
from utils.logging_config import get_logger

logger = get_logger(__name__)

# --- Paths ---
root_dir = Path(__file__).resolve().parent.parent
project_root = root_dir

# AI workspace
AI_WORKSPACE = root_dir

# --- ICGL Singletons ---
_consensus_service = None
_agent_registry = None

def get_consensus_service():
    global _consensus_service
    if _consensus_service is None:
        from api.services.consensus_service import ConsensusService
        _consensus_service = ConsensusService()
    return _consensus_service

def get_agent_registry():
    global _agent_registry
    if _agent_registry is None:
        from agents.registry import AgentRegistry
        from agents import (
            ArchitectAgent, FailureAgent, PolicyAgent, ConceptGuardian,
            SentinelAgent, BuilderAgent, MonitorAgent, SecretaryAgent,
            ArchivistAgent, DevelopmentManagerAgent
        )
        from agents.hr_agent import HRAgent
        from agents.engineer import EngineerAgent
        
        try:
            _agent_registry = AgentRegistry()
            # Register core loop agents
            _agent_registry.register(ArchitectAgent())
            _agent_registry.register(PolicyAgent())
            _agent_registry.register(SentinelAgent())
            _agent_registry.register(EngineerAgent())
            _agent_registry.register(BuilderAgent())
            _agent_registry.register(MonitorAgent())
            _agent_registry.register(ArchivistAgent())
            _agent_registry.register(HRAgent())
            _agent_registry.register(SecretaryAgent())
        except Exception as e:
            logger.critical(f"CRITICAL: Failed to initialize AgentService: {e}")
            if _agent_registry is None:
                # Fallback to bare registry if possible, or re-raise
                from agents.registry import AgentRegistry
                _agent_registry = AgentRegistry() # This might fail again if key is missing
            
    return _agent_registry

# --- API Key Guard ---
def _require_api_key(x_icgl_api_key: str = Header(default=None)):
    """
    Simple API key gate. If env ICGL_API_KEY is set, header X-ICGL-API-KEY must match.
    """
    master_key = os.getenv("ICGL_API_KEY")
    if master_key and x_icgl_api_key != master_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return True

# --- Workspace Helpers ---
def _safe_workspace_path(rel_path: str) -> Path:
    return Path(rel_path).expanduser().resolve()

def _list_workspace(root: Path = AI_WORKSPACE, limit: Optional[int] = None) -> List[str]:
    results = []
    for p in root.rglob("*"):
        if p.is_file():
            results.append(str(p.relative_to(AI_WORKSPACE)))
        if limit and len(results) >= limit:
            break
    return results

def _detect_intent(text: str) -> str:
    text_lower = text.lower()
    if any(k in text_lower for k in ["policy", "سياسة", "rule"]): return "policy"
    if any(k in text_lower for k in ["adr", "decision", "قرار"]): return "adr"
    if any(k in text_lower for k in ["architect", "بناء", "design"]): return "architect"
    return "general"
