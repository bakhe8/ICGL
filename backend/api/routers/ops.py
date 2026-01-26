from fastapi import APIRouter

from backend.ops.transaction import tx_manager

router = APIRouter()


@router.get("/metrics")
def get_metrics():
    """Returns real-time system metrics."""
    # Placeholder: In Phase 4 connect to Promethues/Real monitors
    return {"chaosLevel": 0.12, "efficiency": 98.2, "databaseIntegrity": 100.0}


@router.get("/transactions")
def get_transactions():
    """Returns the history of atomic deployment transactions."""
    return tx_manager.get_history()


@router.get("/committee")
def get_committee():
    """Returns the status of the Sovereign Committee."""
    return [
        {"name": "Architect", "role": "System Design", "status": "Active"},
        {"name": "Sovereign", "role": "Policy Guard", "status": "Watching"},
        {"name": "DevOps", "role": "Transaction Ops", "status": "Idle"},
    ]
