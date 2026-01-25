import json
import logging
import os
from datetime import datetime
from typing import Dict

STATE_FILE = "data/agent_states.json"


class AgentLifecycleController:
    """
    Enforces Human Supremacy Policy (DRA-P01).
    Manages the ACTIVE/SUSPENDED state of agents.
    Persists state to disk to survive restarts.
    """

    def __init__(self):
        self.states = self._load_states()
        self.logger = logging.getLogger("Lifecycle")

    def _load_states(self) -> Dict[str, Dict]:
        if not os.path.exists(STATE_FILE):
            return {}
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load agent states: {e}")
            return {}

    def _save_states(self):
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(self.states, f, indent=2)
        except Exception as e:
            print(f"Failed to save agent states: {e}")

    def kill_agent(self, agent_id: str, reason: str, operator_id: str) -> Dict:
        """
        Executes the 'Kill Switch'.
        According to DRA-P01, this logically suspends the agent.
        """
        if agent_id not in self.states:
            self.states[agent_id] = {}

        self.states[agent_id] = {
            "status": "suspended",
            "suspended_at": datetime.now().isoformat(),
            "reason": reason,
            "operator": operator_id,
        }
        self._save_states()
        self.logger.warning(f"KILL SWITCH ACTIVATED for {agent_id} by {operator_id}")
        return {"status": "success", "agent": agent_id, "state": "suspended"}

    def revive_agent(self, agent_id: str, reason: str, operator_id: str) -> Dict:
        """
        Revives a suspended agent.
        """
        self.states[agent_id] = {
            "status": "active",
            "revived_at": datetime.now().isoformat(),
            "reason": reason,
            "operator": operator_id,
        }
        self._save_states()
        self.logger.info(f"Agent {agent_id} REVIVED by {operator_id}")
        return {"status": "success", "agent": agent_id, "state": "active"}

    def is_agent_active(self, agent_id: str) -> bool:
        """
        Check if an agent is allowed to run.
        Default is active if no record exists.
        """
        state = self.states.get(agent_id, {})
        return state.get("status", "active") == "active"

    def get_agent_status(self, agent_id: str) -> Dict:
        return self.states.get(agent_id, {"status": "active"})


# Global Instance
lifecycle_controller = AgentLifecycleController()
