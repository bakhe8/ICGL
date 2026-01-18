"""
ICGL Dashboard — Centralized committee/report/task view
------------------------------------------------------
Provides a central interface for committees, reports, requests, and decision logs.
"""

from typing import List, Dict, Any

class Dashboard:
    def __init__(self):
        self.committees = []
        self.reports = []
        self.requests = []
        self.decision_log = []

    def add_committee(self, committee: Dict[str, Any]):
        self.committees.append(committee)

    def add_report(self, report: Dict[str, Any]):
        self.reports.append(report)

    def add_request(self, request: Dict[str, Any]):
        self.requests.append(request)

    def log_decision(self, decision: Dict[str, Any]):
        self.decision_log.append(decision)

    def get_overview(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "committees": self.committees,
            "reports": self.reports,
            "requests": self.requests,
            "decision_log": self.decision_log
        }
