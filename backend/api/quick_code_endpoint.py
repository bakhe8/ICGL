# Simple Direct Code Execution Endpoint
# =====================================
#
# This endpoint bypasses the full ICGL pipeline (Policy, Guardian, Sentinel, LanceDB)
# and directly uses BuilderAgent + EngineerAgent for immediate code changes.

import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/quick", tags=["Quick Execution"])


class QuickCodeRequest(BaseModel):
    """Minimal request for direct code changes."""

    instruction: str  # What to do
    target_file: str  # Which file to modify
    file_content: Optional[str] = None  # Current file content (optional)


class QuickCodeResponse(BaseModel):
    """Response from quick code execution."""

    success: bool
    file_path: str
    changes_applied: bool
    message: str
    generated_content: Optional[str] = None


@router.post("/code", response_model=QuickCodeResponse)
async def quick_code_execution(req: QuickCodeRequest):
    """
    Direct code execution bypass - uses only BuilderAgent + file writing.

    No LanceDB, no Policy checks, no Sentinel - just fast idea → code → disk.
    """
    try:
        from shared.python.agents_shared.agents.base import Problem
        from shared.python.agents_shared.agents.builder import BuilderAgent

        # 1. Create BuilderAgent
        builder = BuilderAgent()

        # 1.5. Read existing file content if file exists
        project_root = Path(os.getcwd())
        target_path = (
            project_root / req.target_file
            if not Path(req.target_file).is_absolute()
            else Path(req.target_file)
        )

        existing_content = req.file_content
        if not existing_content and target_path.exists():
            try:
                existing_content = target_path.read_text(encoding="utf-8")
                print(f"📖 Read existing file: {len(existing_content)} chars")
            except Exception as e:
                print(f"⚠️ Could not read existing file: {e}")

        # Build detailed context
        if existing_content:
            context = f"""{req.instruction}

**IMPORTANT INSTRUCTIONS**:
1. This is a MODIFICATION of an existing file, NOT a new file creation
2. You MUST preserve ALL existing code that is not being changed
3. Only modify the specific parts mentioned in the instruction
4. Keep all imports, functions, and logic intact

**Current file content**:
```
{existing_content[:2000]}  
{f"... ({len(existing_content)} total chars)" if len(existing_content) > 2000 else ""}
```

**Target file**: {req.target_file}
**Action**: MODIFY (not CREATE)
"""
        else:
            context = f"{req.instruction}\n\n**Target file**: {req.target_file}\n\nIMPORTANT: You MUST use exactly this path: {req.target_file}"

        # 2. Prepare problem - explicitly mention target file
        problem = Problem(
            title=f"Quick change: {req.instruction[:50]}",
            context=context,
            metadata={
                "decision": req.instruction,
                "target_files": [req.target_file],
                "file_contents": {req.target_file: existing_content}
                if existing_content
                else {},
            },
        )

        # 3. Generate code (no KB needed for simple mode)
        result = await builder._analyze(problem, kb=None)

        # 4. Write to file if changes exist
        if result.file_changes:
            # Get project root
            project_root = Path(os.getcwd())

            for fc in result.file_changes:
                # Resolve path
                raw_path = fc.path
                if not Path(raw_path).is_absolute():
                    final_path = project_root / raw_path
                else:
                    final_path = Path(raw_path)

                # Create parent directories
                final_path.parent.mkdir(parents=True, exist_ok=True)

                # Write file
                print(f"📝 Writing to: {final_path}")
                print(f"   Content length: {len(fc.content)} chars")

                try:
                    with open(final_path, "w", encoding="utf-8") as f:
                        f.write(fc.content)
                    print("   ✅ File written successfully!")
                except Exception as write_err:
                    print(f"   ❌ Write error: {write_err}")
                    raise

                # Verify file exists
                if final_path.exists():
                    actual_size = final_path.stat().st_size
                    print(f"   ✅ Verified: {actual_size} bytes on disk")
                else:
                    print("   ❌ File doesn't exist after write!")

                return QuickCodeResponse(
                    success=True,
                    file_path=str(final_path),
                    changes_applied=True,
                    message=f"✅ File written successfully: {final_path}",
                    generated_content=fc.content,
                )
        else:
            return QuickCodeResponse(
                success=False,
                file_path=req.target_file,
                changes_applied=False,
                message="⚠️ No file changes generated by BuilderAgent",
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Quick code execution failed: {str(e)}"
        )
