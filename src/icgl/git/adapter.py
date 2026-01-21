import subprocess
import os
from typing import List
from .interface import GitInterface, GitStatus

class GitAdapter(GitInterface):
    """
    Concrete implementation of GitInterface using subprocess.
    """
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        
    def _run(self, args: List[str]) -> str:
        """Runs a git command and returns stdout."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git command failed: {' '.join(args)}\nError: {e.stderr}")

    def stage_file(self, path: str) -> None:
        self._run(["add", path])

    def commit(self, message: str) -> str:
        self._run(["commit", "-m", message])
        # Return hash
        return self._run(["rev-parse", "HEAD"])

    def get_status(self) -> GitStatus:
        # Simple status check using porcelain
        output = self._run(["status", "--porcelain"])
        
        modified = []
        staged = []
        
        for line in output.splitlines():
            if not line: continue
            code = line[:2]
            path = line[3:]
            
            if code[0] in ('M', 'A', 'D'):
                staged.append(path)
            if code[1] in ('M', 'D', '?'):
                modified.append(path)
                
        return GitStatus(
            is_clean=len(modified) == 0 and len(staged) == 0,
            modified_files=modified,
            staged_files=staged
        )

    def get_current_branch(self) -> str:
        return self._run(["rev-parse", "--abbrev-ref", "HEAD"])
