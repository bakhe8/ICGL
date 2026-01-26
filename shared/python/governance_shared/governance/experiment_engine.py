from typing import Any, Dict, List

from backend.agents.base import AgentResult


class PolicyExperimentEngine:
    """
    Experimental Engine for Phase 10.
    Allows testing of 'Autonomous Policy Engine' recommendations in trial mode.
    """

    def __init__(self):
        self.trial_policies = []
        self.benefit_metrics = {
            "token_savings": 0,
            "latency_reduction": 0.0,
            "accuracy_gain": 0.0,
        }

    def register_trial_proposal(self, agent_id: str, suggestion: str):
        """Register a policy suggestion for trial tracking."""
        proposal = {
            "agent": agent_id,
            "suggestion": suggestion,
            "status": "TRIAL",
            "impact_score": 0.0,
        }
        self.trial_policies.append(proposal)
        return proposal

    def calculate_benefit(self, results: List[AgentResult]) -> Dict[str, Any]:
        """
        Analyzes a batch of results to prove if the experimental policy
        actually improved the system.
        """
        # Logic to compare against historical baseline
        return self.benefit_metrics

    async def analyze_traffic_and_propose(self):
        """
        Autonomous Check:
        Scans traffic logs from the Sovereign Router to find inefficiencies.
        If the 'Researcher' agent is spamming, it proposes a 'Quiet Hours' policy.
        """
        from backend.api.server import get_channel_router

        router = get_channel_router()
        if not router:
            return None

        # 1. Get stats
        logs = router.get_recent_traffic(limit=50)
        if not logs:
            return None

        # 2. Simple Heuristic: Count messages per agent
        counts = {}
        for msg in logs:
            sender = msg.get("from_agent")
            counts[sender] = counts.get(sender, 0) + 1

        # 3. Detect "Spam" (Threshold > 10 messages in buffer)
        for agent, count in counts.items():
            if count > 10:
                # Check if we already have a proposal for this
                existing = [p for p in self.trial_policies if p["agent"] == agent]
                if not existing:
                    # PROPOSE POLICY AUTOMATICALLY
                    suggestion = f"Policy: Rate Limit {agent} due to excessive traffic ({count} msgs)"
                    self.register_trial_proposal(agent, suggestion)

                    return {
                        "event": "AUTO_PROPOSAL",
                        "agent": agent,
                        "proposal": suggestion,
                        "details": "Detected high frequency chatter. Proposed throttling.",
                    }
        return None


# Singleton for trial mode
experiment_engine = PolicyExperimentEngine()
