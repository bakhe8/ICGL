from typing import Optional
from agents.base import Agent, AgentRole, Problem, AgentResult
from git.adapter import GitAdapter
from kb.schemas import ADR, HumanDecision

class EngineerAgent(Agent):
    """
    The Engineer: Operates the machinery of the codebase (Git, Scalability, CI).
    """
    
    def __init__(self, repo_path: str = "."):
        super().__init__("agent-engineer", AgentRole.ENGINEER)
        # Note: Ideally we add ENGINEER to AgentRole enum.
        self.git = GitAdapter(repo_path)

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Standard analysis (not primary use case for Engineer yet).
        """
        analysis_parts = []
        recommendations = []
        concerns = []
        git_snapshot = {}
        try:
            branch = self.git.get_current_branch()
            status = self.git.get_status()
            git_snapshot = {
                "branch": branch,
                "staged": status.staged_files,
                "modified": status.modified_files,
                "clean": status.is_clean,
            }
            analysis_parts.append(f"Git branch: {branch}")
            if status.is_clean:
                analysis_parts.append("Working tree is clean.")
            else:
                analysis_parts.append(f"Staged: {status.staged_files}")
                analysis_parts.append(f"Modified: {status.modified_files}")
                concerns.append("Working tree not clean")
                recommendations.append("راجع التعديلات قبل الدمج")
        except Exception as e:
            concerns.append(f"Git check failed: {e}")
            analysis_parts.append("Git status unavailable.")
        
        if not recommendations:
            recommendations.append("استمر في فحص CI/CD قبل أي دمج")

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis="\n".join(analysis_parts) or "Engineer ready for ops.",
            recommendations=recommendations,
            concerns=concerns,
            references=[str(git_snapshot)] if git_snapshot else [],
            confidence=0.8 if concerns else 1.0
        )

    def commit_decision(self, adr: ADR, decision: HumanDecision) -> str:
        """
        Executes the auto-commit for an approved decision.
        """
        if decision.action != "APPROVE":
            return "Skipped (Not Approved)"
            
        print(f"🏗️ [Engineer] Committing Decision {adr.id}...")
        
        # 1. Stage Data Files
        # We assume the DB and Logs are what we want to persist representing the state.
        # In a real repo, we might commit the code changes if the agent wrote them.
        # For now, we commit the Kernel (kb.db).
        try:
            self.git.stage_file("data/kb.db")
            
            # Construct Commit Message
            msg = f"governance(adr): {adr.id} {adr.title}\n\nDecision: {decision.action} by {decision.signed_by}\nRationale: {decision.rationale}"
            
            # Commit
            commit_hash = self.git.commit(msg)
            print(f"   ✅ Committed: {commit_hash[:7]}")
            return commit_hash
        except Exception as e:
            print(f"   ⚠️ Commit Failed: {e}")
            return f"Failed: {e}"

    def write_file(self, path: str, content: str, mode: str = "w") -> str:
        """
        Writes content to the physical filesystem.
        Constrained to the current workspace (repo_path) for safety.
        """
        import os
        from pathlib import Path
        
        # 1. Resolve Paths
        base_dir = Path(self.git.repo_path).resolve()
        target_path = (base_dir / path).resolve()
        
        # 2. Safety Check: path traversal
        if not str(target_path).startswith(str(base_dir)):
            error = f"🛑 Security Violation: Attempt to write outside workspace ({target_path})"
            print(error)
            return error
            
        print(f"👷 [Engineer] Writing file: {path}...")
        try:
            # 3. Create Parent Dirs
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 4. Write
            with open(target_path, mode, encoding="utf-8") as f:
                f.write(content)
                
            print(f"   ✅ Success: {len(content)} bytes written.")
            return "Success"
            
        except Exception as e:
            msg = f"   ❌ Write Failed: {e}"
            print(msg)
            return msg
