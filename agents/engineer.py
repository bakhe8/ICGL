from typing import Optional, Any, List
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
        Analysis of the machinery and state of the codebase.
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
            analysis_parts.append(f"Staged: {len(status.staged_files)}, Modified: {len(status.modified_files)}")
            
            if not status.is_clean:
                if status.staged_files:
                    analysis_parts.append(f"Staged files: {', '.join(status.staged_files)}")
                if status.modified_files:
                    analysis_parts.append(f"Modified files: {', '.join(status.modified_files)}")
                concerns.append("Working tree not clean")
                recommendations.append("Review modifications before merging.")
            else:
                analysis_parts.append("Working tree is clean.")
        except Exception as e:
            concerns.append(f"Git check failed: {e}")
            analysis_parts.append("Git status unavailable.")
        
        if not recommendations:
            recommendations.append("Continue monitoring CI/CD and system stability.")

        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis="\n".join(analysis_parts) or "Engineer ready for operations.",
            recommendations=recommendations,
            concerns=concerns,
            references=[
                f"branch={git_snapshot.get('branch')}",
            ] if git_snapshot else [],
            confidence=0.9 if not concerns else 0.7
        )

    def commit_decision(self, adr: ADR, decision: Any) -> str:
        """
        Executes the auto-commit for an approved decision.
        """
        try:
            commit_hash = self.git.commit(f"ADR-{adr.id}: {decision.action}\n\nRationale: {decision.rationale}")
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

    def read_file(self, path: str) -> str:
        """Reads a file from the workspace."""
        from pathlib import Path
        base_dir = Path(self.git.repo_path).resolve()
        target_path = (base_dir / path).resolve()
        if not str(target_path).startswith(str(base_dir)):
            return "🛑 Security Violation"
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"❌ Read Failed: {e}"

    def list_files(self, path: str = ".") -> List[str]:
        """Lists files in a directory."""
        import os
        from pathlib import Path
        base_dir = Path(self.git.repo_path).resolve()
        target_path = (base_dir / path).resolve()
        if not str(target_path).startswith(str(base_dir)):
            return ["🛑 Security Violation"]
        try:
            return os.listdir(target_path)
        except Exception as e:
            return [f"❌ List Failed: {e}"]

    def run_command(self, cmd: str) -> str:
        """Runs a shell command in the workspace."""
        import subprocess
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=self.git.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout or result.stderr or "Executed."
        except Exception as e:
            return f"❌ Command Failed: {e}"
