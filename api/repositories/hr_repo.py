from pathlib import Path
from api.repositories.base_repo import BaseFileRepository
from api.dependencies import root_dir

HR_RECORDS_FILE = root_dir / "data" / "hr_records.json"

class HrRepository(BaseFileRepository):
    def __init__(self):
        super().__init__(HR_RECORDS_FILE)
    
    def find_by_name(self, name: str):
        data = self.get_all()
        for item in data:
            if item.get("name") == name:
                return item
        return None
