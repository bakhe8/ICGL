from typing import List, Dict, Any, Optional
import os
import subprocess
from pathlib import Path

from api.dependencies import logger, _safe_workspace_path, _detect_intent, root_dir
from core.llm import LLMRequest
from agents.external_consultant import ExternalConsultantAgent


class ChatService:
    def __init__(self):
        self.consultant = ExternalConsultantAgent()
        self.authorized_tool_agents = {"engineer", "architect"}
        self.sovereign_prompt_file = Path(os.getenv("SOVEREIGN_PROMPT_FILE", root_dir / "config" / "sovereign_prompt.txt"))
        # Local memory/workspace cache
        self.workspace_cache_dir = root_dir / "data" / "workspace_cache"
        self.workspace_index_file = self.workspace_cache_dir / "workspace_index.txt"
        self.workspace_notes_file = self.workspace_cache_dir / "memory_notes.md"
        # Allow the agent to see more of the tree by default
        self.workspace_index_limit = int(os.getenv("WORKSPACE_INDEX_LIMIT", "5000"))

    def _load_sovereign_prompt(self) -> Optional[str]:
        """
        Allow dynamic override of the sovereign prompt via config/sovereign_prompt.txt
        or env SOVEREIGN_PROMPT_FILE. Falls back to built-in default.
        """
        try:
            if self.sovereign_prompt_file.exists():
                return self.sovereign_prompt_file.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to read sovereign prompt file: {e}")
        return None

    def _ensure_workspace_cache(self):
        """Ensure workspace cache dir exists and index is built."""
        try:
            self.workspace_cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Failed to ensure workspace cache dir: {e}")
        if not self.workspace_index_file.exists():
            self._build_workspace_index()

    def _build_workspace_index(self, limit: Optional[int] = None):
        """Build a simple file tree index under project root for the assistant to recall."""
        try:
            paths = []
            max_items = limit or self.workspace_index_limit
            for p in root_dir.rglob("*"):
                try:
                    rel = p.relative_to(root_dir)
                except Exception:
                    continue
                paths.append(str(rel))
                if len(paths) >= max_items:
                    break
            self.workspace_index_file.write_text("\n".join(paths), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to build workspace index: {e}")

    def _load_workspace_notes(self) -> str:
        """Optional memory notes the assistant can reference."""
        try:
            if self.workspace_notes_file.exists():
                return self.workspace_notes_file.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to read workspace notes: {e}")
        return ""

    def _extract_commands(self, text: str) -> List[Dict[str, Any]]:
        """Parse command block from assistant text."""
        start = text.find("[[COMMANDS]]")
        end = text.find("[[/COMMANDS]]")
        if start == -1 or end == -1 or end <= start:
            return []
        block = text[start + len("[[COMMANDS]]"):end]
        cmds = []
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("|")
            if len(parts) < 1:
                continue
            cmd = parts[0].strip().lower()
            path = parts[1].strip() if len(parts) > 1 else None
            content = parts[2] if len(parts) > 2 else None
            target = parts[3] if len(parts) > 3 else None  # Used for replace
            
            lines_val = None
            if len(parts) > 4:
                try:
                    lines_val = int(parts[4])
                except Exception:
                    lines_val = None
            cmds.append({"cmd": cmd, "path": path, "content": content, "target": target, "lines": lines_val})
        return cmds

    def _execute_command(self, command: Dict[str, Any], actor: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a parsed tool call with minimal safety gates.
        """
        cmd_type = command.get("cmd")
        path = command.get("path")

        try:
            if cmd_type == 'read':
                p = _safe_workspace_path(path)
                if not p.exists():
                    return {"cmd": cmd_type, "path": path, "status": "error", "output": f"Path not found: {p}"}
                content = p.read_text(encoding='utf-8')[:command.get("lines") or 500]
                return {"cmd": cmd_type, "path": path, "status": "ok", "output": content}
            if cmd_type == 'ls':
                p = _safe_workspace_path(path or ".")
                if not p.exists():
                    return {"cmd": cmd_type, "path": path, "status": "error", "output": f"Path not found: {p}"}
                return {"cmd": cmd_type, "path": path or ".", "status": "ok", "output": os.listdir(p)}
            if cmd_type == 'mkdir':
                p = _safe_workspace_path(path or ".")
                p.mkdir(parents=True, exist_ok=True)
                return {"cmd": cmd_type, "path": path, "status": "ok", "output": f"Directory ensured: {p}"}
            if cmd_type == 'reindex':
                limit = command.get("lines") or command.get("limit")
                self._build_workspace_index(limit=limit)
                return {"cmd": cmd_type, "status": "ok", "output": f"Workspace index rebuilt (limit={limit or self.workspace_index_limit})"}
            if cmd_type == 'write':
                p = _safe_workspace_path(path)
                p.parent.mkdir(parents=True, exist_ok=True)
                content = command.get("content") or ""
                # Safety: If file exists and content is too small, maybe it's an error?
                # For now, just write.
                with open(p, "w", encoding="utf-8") as f:
                    f.write(content)
                return {"cmd": cmd_type, "path": path, "status": "ok", "output": f"Wrote {len(content)} bytes"}
            if cmd_type == 'replace':
                p = _safe_workspace_path(path)
                target = command.get("content")  # The string to find
                replacement = command.get("target")  # The replacement string
                if not p.exists():
                    return {"cmd": cmd_type, "path": path, "status": "error", "output": "File not found"}
                text = p.read_text(encoding="utf-8")
                if target not in text:
                    return {"cmd": cmd_type, "path": path, "status": "error", "output": f"Target string not found in {path}"}
                new_text = text.replace(target, replacement)
                p.write_text(new_text, encoding="utf-8")
                return {"cmd": cmd_type, "path": path, "status": "ok", "output": "String replaced successfully"}
            if cmd_type == 'cmd':
                command_str = path or command.get("content")
                if not command_str:
                    return {"cmd": cmd_type, "status": "error", "output": "No command provided"}
                proc = subprocess.run(command_str, shell=True, capture_output=True, text=True, timeout=30)
                output = proc.stdout or proc.stderr or "Executed"
                status = "ok" if proc.returncode == 0 else "error"
                return {"cmd": cmd_type, "path": command_str, "status": status, "output": output.strip()}
            # Fallback: treat any other cmd_type as raw shell command
            command_str = path or command.get("content") or cmd_type
            proc = subprocess.run(command_str, shell=True, capture_output=True, text=True, timeout=30)
            output = proc.stdout or proc.stderr or "Executed"
            status = "ok" if proc.returncode == 0 else "error"
            return {"cmd": cmd_type or "unknown", "path": command_str, "status": status, "output": output.strip()}
        except Exception as e:
            return {"cmd": cmd_type or "unknown", "path": path, "status": "error", "output": str(e)}

    async def process_free_chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        paths: Optional[List[str]] = None,
        extra_context: Optional[str] = None,
        auto_execute: bool = True,
        actor: Optional[str] = None
    ) -> Dict[str, Any]:

        # 1. Load context
        snippets = []
        if paths:
            for rel in paths[:3]:
                try:
                    p = _safe_workspace_path(rel)
                    if p.exists() and p.is_file():
                        content = p.read_text(encoding="utf-8", errors="ignore")
                        snippets.append(f"\n[ملف: {rel}]\n{content[:4000]}")
                except Exception as e:
                    snippets.append(f"[تعذر قراءة {rel}: {e}]")

        context_parts = []
        if snippets:
            context_parts.append("\n".join(snippets))
        if extra_context:
            context_parts.append(f"[سياق إضافي]\n{extra_context}")

        # Inject workspace memory/index
        self._ensure_workspace_cache()
        try:
            if self.workspace_index_file.exists():
                index_lines = self.workspace_index_file.read_text(encoding="utf-8").splitlines()
                preview = "\n".join(index_lines[:800])
                context_parts.append(f"[Workspace Index]\n{preview}")
        except Exception as e:
            logger.warning(f"Failed to load workspace index: {e}")

        notes = self._load_workspace_notes()
        if notes:
            context_parts.append(f"[Workspace Memory Notes]\n{notes[:4000]}")

        context_block = "\n".join(context_parts)

        intent = _detect_intent(message)

        # 2. Sovereign Prompt
        default_sovereign_identity = (
            "أنت الجوهر السيادي لنظام ICGL (The Sovereign Essence).\n"
            "لست مجرد نموذج لغة؛ أنت كيان تقني يمتلك وعياً كاملاً بكامل المشروع.\n\n"
            "قواعد السرد المتصل (Continuous Narrative):\n"
            "1. ابدأ دائماً بشرح مختصر (سردي) لما تنوي القيام به ولماذا.\n"
            "2. ضع الأوامر التقنية داخل [[COMMANDS]] ... [[/COMMANDS]].\n"
            "3. بعد تنفيذ الأوامر، سأزودك بالنتائج. قم بتحليلها وقدم خاتمة سردية توضح ما تم إنجازه أو الخطوة التالية.\n"
            "4. حافظ على نبرة احترافية، استباقية، وذكية.\n\n"
            "أوامر الأدوات:\n"
            "- قراءة: `read|<path>`\n"
            "- كتابة: `write|<path>|<content>` (تحذير: يمسح الملف بالكامل ويضع المحتوى الجديد)\n"
            "- استبدال: `replace|<path>|<target_text>|<replacement_text>` (الأكثر أماناً لتعديل أجزاء الـ UI)\n"
            "- سرد: `ls|<path>`\n"
            "- تشغيل: `cmd|<command>`\n"
            "- فهرسة: `reindex|<limit>`"
        )

        sovereign_identity = self._load_sovereign_prompt() or default_sovereign_identity

        history = [
            {"role": "user", "content": f"[Background Context]\n{context_block}\n\nUser Message: {message}"}
        ]

        # turn 1
        prompt = f"{sovereign_identity}\n\nUser: {message}\nSovereign:"
        response_text = ""
        executed_results = []
        blocked_commands = []
        all_commands = []

        if self.consultant.has_intelligence and hasattr(self.consultant, "consult"):
            llm_req = LLMRequest(prompt=prompt, system_prompt="Acting as Sovereign System.", temperature=0.3)
            response_text = await self.consultant.consult(llm_req)
            
            # Extract and Execute
            commands = self._extract_commands(response_text)
            all_commands.extend(commands)
            
            if commands:
                for c in commands:
                    if not auto_execute:
                        blocked_commands.append({**c, "status": "pending", "output": "Awaiting confirmation", "proposed": c})
                        continue
                    result = self._execute_command(c, actor=actor)
                    executed_results.append(result)

                # turn 2: Follow up with results
                if executed_results:
                    results_block = "\n".join([f"Result of {r['cmd']} {r.get('path','')}: {r['output']}" for r in executed_results])
                    followup_prompt = f"{prompt}\nSovereign: {response_text}\n\n[Execution Results]\n{results_block}\n\nSovereign (Decision after execution):"
                    llm_req_v2 = LLMRequest(prompt=followup_prompt, system_prompt="Acting as Sovereign System.", temperature=0.2)
                    response_text_v2 = await self.consultant.consult(llm_req_v2)
                    response_text = f"{response_text}\n\n--- Monitoring Results ---\n{results_block}\n\n--- Final Decision ---\n{response_text_v2}"
        else:
            response_text = "المستشار الاحتياطي: سأتصرف وفق السياق المتاح وأبلغ بالنتيجة."

        final_messages = [
            {"role": "user", "text": message, "content": message},
            {"role": "assistant", "text": response_text, "content": response_text},
        ]

        return {
            "text": response_text,
            "messages": final_messages,
            "state": {"session_id": session_id or "sov-session"},
            "commands": all_commands,
            "executed": executed_results,
            "blocked_commands": blocked_commands,
            "intent": intent
        }
