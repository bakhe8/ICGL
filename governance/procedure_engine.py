from typing import List, Optional
from ..kb.schemas import Procedure, ID, uid, now
from ..kb import PersistentKnowledgeBase
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class ProcedureEngine:
    """
    Manages the lifecycle of Standard Operating Procedures (SOPs).
    Responsible for:
    - Creating new SOPs
    - Validating SOP structure
    - Retrieving SOPs for execution
    """
    
    def __init__(self, kb: PersistentKnowledgeBase = None):
        self.kb = kb or PersistentKnowledgeBase()
        
    def create_sop(self, 
                   title: str, 
                   code: str, 
                   steps: List[str], 
                   tools: List[str],
                   type: str = "SOP") -> Procedure:
        """
        Creates and registers a new SOP in the Knowledge Base.
        """
        
        # Check uniqueness
        # In a real impl, we'd check if code exists. 
        # For now, KB uses ID as key.
        
        proc = Procedure(
            id=uid(),
            code=code,
            title=title,
            type=type,
            steps=steps,
            required_tools=tools,
            version="1.0.0"
        )
        
        # Persist
        if hasattr(self.kb, 'add_procedure'):
             self.kb.add_procedure(proc)
             logger.info(f"✅ SOP Created: {code} - {title}")
             return proc
        else:
            logger.warning("KB does not support Procedures yet.")
            return None

    def list_procedures(self) -> List[Procedure]:
        if hasattr(self.kb, 'procedures'):
            return list(self.kb.procedures.values())
        return []

    def get_procedure(self, code_or_id: str) -> Optional[Procedure]:
        if not hasattr(self.kb, 'procedures'): return None
        
        # Check ID
        if code_or_id in self.kb.procedures:
            return self.kb.procedures[code_or_id]
            
        # Check Code (Scan)
        for p in self.kb.procedures.values():
            if p.code == code_or_id:
                return p
        return None
