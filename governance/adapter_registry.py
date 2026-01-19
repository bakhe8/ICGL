from typing import Dict, List, Optional
from dataclasses import dataclass, field
from ..kb.schemas import ID, Timestamp, uid, now
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class AdapterMetadata:
    """
    ADR-CANONICAL-001 §3.3: Adapter Certification Metadata.
    
    All adapters SHALL:
    - Be registered and versioned
    - Undergo integrity validation
    - Declare dependency boundaries
    - Support emergency disablement
    """
    id: ID
    name: str
    version: str
    adapter_type: str  # e.g., "slack", "email", "webhook"
    scope: str  # e.g., "outbound-only", "bidirectional"
    permissions: List[str]  # e.g., ["send_message", "read_channels"]
    data_boundaries: str  # Description of what data can be accessed
    kill_switch_enabled: bool = True
    certified: bool = False
    certification_date: Optional[Timestamp] = None
    dependency_boundaries: List[str] = field(default_factory=list)
    created_at: Timestamp = field(default_factory=now)


class AdapterRegistry:
    """
    Central registry for all external adapters.
    Enforces ADR-CANONICAL-001 §3.3 compliance.
    """
    
    def __init__(self):
        self.adapters: Dict[str, AdapterMetadata] = {}
        logger.info("🔌 AdapterRegistry initialized")
    
    def register(self, metadata: AdapterMetadata) -> None:
        """Register a new adapter."""
        if metadata.name in self.adapters:
            logger.warning(f"⚠️ Adapter {metadata.name} already registered. Updating...")
        
        self.adapters[metadata.name] = metadata
        logger.info(f"✅ Adapter registered: {metadata.name} v{metadata.version}")
    
    def get(self, name: str) -> Optional[AdapterMetadata]:
        """Retrieve adapter metadata."""
        return self.adapters.get(name)
    
    def list_all(self) -> List[AdapterMetadata]:
        """List all registered adapters."""
        return list(self.adapters.values())
    
    def list_certified(self) -> List[AdapterMetadata]:
        """List only certified adapters."""
        return [a for a in self.adapters.values() if a.certified]
    
    def list_uncertified(self) -> List[AdapterMetadata]:
        """List uncertified adapters (compliance gap)."""
        return [a for a in self.adapters.values() if not a.certified]


class AdapterCertificationEngine:
    """
    ADR-CANONICAL-001 §3.3: Adapter Certification Engine.
    
    Validates adapter integrity and enforces compliance requirements.
    """
    
    def __init__(self, registry: AdapterRegistry):
        self.registry = registry
        logger.info("🛡️ AdapterCertificationEngine initialized")
    
    def certify(self, adapter_name: str) -> bool:
        """
        Certify an adapter after validation.
        
        Validation checks:
        1. Kill switch is enabled
        2. Scope is explicitly declared
        3. Permissions are non-empty
        4. Data boundaries are documented
        """
        adapter = self.registry.get(adapter_name)
        if not adapter:
            logger.error(f"❌ Adapter {adapter_name} not found in registry")
            return False
        
        # Validation checks
        if not adapter.kill_switch_enabled:
            logger.error(f"❌ Certification failed: {adapter_name} has no kill switch")
            return False
        
        if not adapter.scope:
            logger.error(f"❌ Certification failed: {adapter_name} has no declared scope")
            return False
        
        if not adapter.permissions:
            logger.error(f"❌ Certification failed: {adapter_name} has no declared permissions")
            return False
        
        if not adapter.data_boundaries:
            logger.error(f"❌ Certification failed: {adapter_name} has no data boundaries")
            return False
        
        # All checks passed
        adapter.certified = True
        adapter.certification_date = now()
        logger.info(f"✅ Adapter certified: {adapter_name}")
        return True
    
    def revoke_certification(self, adapter_name: str, reason: str) -> None:
        """Revoke adapter certification (e.g., after security incident)."""
        adapter = self.registry.get(adapter_name)
        if adapter:
            adapter.certified = False
            logger.warning(f"⚠️ Certification revoked for {adapter_name}: {reason}")
    
    def emergency_disable_all(self) -> None:
        """
        Global kill switch: Disable all adapters immediately.
        ADR-CANONICAL-001 §3.3 compliance requirement.
        """
        for adapter in self.registry.list_all():
            adapter.kill_switch_enabled = False
        logger.critical("🚨 EMERGENCY: All adapters disabled via global kill switch")
    
    def validate_adapter_boundaries(self, adapter_name: str) -> bool:
        """
        Validate that adapter does not couple with core systems.
        ADR-CANONICAL-001 §2.2 requirement.
        """
        adapter = self.registry.get(adapter_name)
        if not adapter:
            return False
        
        forbidden_dependencies = ["Sentinel", "Governance", "Orchestrator", "KnowledgeBase"]
        for dep in adapter.dependency_boundaries:
            if any(forbidden in dep for forbidden in forbidden_dependencies):
                logger.error(f"❌ Boundary violation: {adapter_name} couples with core system: {dep}")
                return False
        
        return True


# Global registry instance
_adapter_registry = None
_certification_engine = None

def get_adapter_registry() -> AdapterRegistry:
    """Get the global adapter registry."""
    global _adapter_registry
    if _adapter_registry is None:
        _adapter_registry = AdapterRegistry()
    return _adapter_registry

def get_certification_engine() -> AdapterCertificationEngine:
    """Get the global certification engine."""
    global _certification_engine
    if _certification_engine is None:
        _certification_engine = AdapterCertificationEngine(get_adapter_registry())
    return _certification_engine
