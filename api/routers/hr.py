import json
from pathlib import Path
from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel

from api.dependencies import _require_api_key, root_dir, logger

router = APIRouter(prefix="/api/hr", tags=["HR"])

HR_RECORDS_FILE = root_dir / "data" / "hr_records.json"
HR_RECORDS_FILE.parent.mkdir(parents=True, exist_ok=True)

class HRRecord(BaseModel):
    name: str
    role: str
    duties: List[str] = []
    limits: List[str] = []

def _load_hr_records() -> list:
    if HR_RECORDS_FILE.exists():
        try:
            return json.loads(HR_RECORDS_FILE.read_text(encoding="utf-8"))
        except:
            return []
    return []

def _save_hr_records(records: list):
    HR_RECORDS_FILE.write_text(json.dumps(records, indent=2), encoding="utf-8")

@router.get("/records")
async def get_hr_records():
    return _load_hr_records()

@router.post("/records/add")
async def add_hr_record(record: HRRecord):
    records = _load_hr_records()
    records.append(record.dict())
    _save_hr_records(records)
    return {"status": "success"}

@router.post("/generate-docs")
async def generate_hr_docs(_: bool = Depends(_require_api_key)):
    # Logic for HR doc generation...
    return {"status": "generated"}
