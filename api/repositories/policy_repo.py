from pathlib import Path
from typing import Optional, List
from api.repositories.base_repo import BaseFileRepository
from api.dependencies import root_dir

POLICY_FILE = root_dir / "data" / "kb_policies.json"

class PolicyRepository(BaseFileRepository):
    def __init__(self):
        super().__init__(POLICY_FILE)
        self.drafts_file = root_dir / "data" / "kb_policies_drafts.json"
        
    def get_drafts(self) -> List[dict]:
        import json
        if self.drafts_file.exists():
            try:
                content = self.drafts_file.read_text(encoding='utf-8')
                return json.loads(content) if content else []
            except:
                return []
        return []

    def save_draft(self, draft: dict) -> dict:
        import json
        drafts = self.get_drafts()
        # Update if exists
        for i, d in enumerate(drafts):
            if d.get("code") == draft.get("code"):
                drafts[i] = draft
                self.drafts_file.write_text(json.dumps(drafts, indent=2, ensure_ascii=False))
                return draft
        # Create
        drafts.append(draft)
        self.drafts_file.write_text(json.dumps(drafts, indent=2, ensure_ascii=False))
        return draft

    def find_by_code(self, code: str) -> Optional[dict]:
        for p in self.get_all():
            if p.get("code") == code:
                return p
        return None
    
    def save_policy(self, policy: dict) -> dict:
        data = self.get_all()
        # Check if exists (update)
        for i, p in enumerate(data):
            if p.get("id") == policy.get("id"):
                data[i] = policy
                self._save_data(data)
                return policy
        # Create
        self.add(policy)
        return policy
