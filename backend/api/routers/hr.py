from api.server_shared import get_icgl
from fastapi import APIRouter

router = APIRouter(prefix="/api/hr", tags=["hr"])


@router.get("/records")
async def get_hr_records():
    """
    Returns HR records/institutional profiles.
    CHECKLIST alignment: /api/hr/records.
    """
    icgl = get_icgl()
    # We'll pull these from 'concepts' or a dedicated HR store if it exists
    # For now, we search for concepts tagged with 'Human' or 'Organization'
    records = []
    for concept in icgl.kb.concepts.values():
        if concept.owner == "HUMAN" or "authority" in concept.name.lower():
            records.append(
                {
                    "id": concept.id,
                    "name": concept.name,
                    "role": concept.definition[:50] + "...",
                    "status": "Verified",
                }
            )
    return {"records": records}
