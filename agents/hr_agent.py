"""
HR Agent — ICGL
---------------
Agent responsible for updating and generating responsibility documents for all agents and departments.
"""

from typing import List, Dict

class HRAgent:
    def __init__(self):
        self.records = []  # List of agent/department records

    def update_record(self, record: Dict):
        self.records.append(record)
        return f"Record updated for: {record.get('name', 'Unknown')}"

    def generate_responsibility_docs(self) -> List[Dict]:
        # Simulate generating responsibility docs
        return [
            {"name": r.get("name"), "role": r.get("role"), "duties": r.get("duties"), "limits": r.get("limits")} for r in self.records
        ]
