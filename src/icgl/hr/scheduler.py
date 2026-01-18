import asyncio
from typing import Dict, Callable, Awaitable, Optional
from datetime import datetime, timedelta
from croniter import croniter
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class AgentScheduler:
    """
    Task Scheduler for Agents
    
    Manages periodic execution of agent tasks based on cron-like schedules.
    Coordinates with WorkforceManager to ensure proper execution.
    """
    
    def __init__(self, workforce_manager=None):
        self.workforce_manager = workforce_manager
        self.scheduled_tasks: Dict[str, dict] = {}
        self.running = False
        logger.info("📅 AgentScheduler initialized")
    
    def schedule_task(
        self,
        task_id: str,
        cron_expression: str,
        task_func: Callable[[], Awaitable[None]],
        agent_id: Optional[str] = None
    ) -> None:
        """
        Schedule a periodic task.
        
        Args:
            task_id: Unique identifier for the task
            cron_expression: Cron-like schedule (e.g., "*/5 * * * *")
            task_func: Async function to execute
            agent_id: Optional agent ID for tracking
        """
        try:
            # Validate cron expression
            croniter(cron_expression)
            
            self.scheduled_tasks[task_id] = {
                "cron": cron_expression,
                "func": task_func,
                "agent_id": agent_id,
                "last_run": None,
                "next_run": self._calculate_next_run(cron_expression),
                "run_count": 0
            }
            
            logger.info(f"✅ Task scheduled: {task_id} ({cron_expression})")
            
        except Exception as e:
            logger.error(f"❌ Failed to schedule task {task_id}: {e}")
    
    def unschedule_task(self, task_id: str) -> None:
        """Remove a scheduled task."""
        if task_id in self.scheduled_tasks:
            del self.scheduled_tasks[task_id]
            logger.info(f"❌ Task unscheduled: {task_id}")
    
    def _calculate_next_run(self, cron_expression: str) -> datetime:
        """Calculate the next run time based on cron expression."""
        cron = croniter(cron_expression, datetime.now())
        return cron.get_next(datetime)
    
    async def _execute_task(self, task_id: str, task_info: dict) -> None:
        """Execute a single task."""
        try:
            logger.info(f"🔄 Executing task: {task_id}")
            
            # Execute the task
            await task_info["func"]()
            
            # Update task info
            task_info["last_run"] = datetime.now()
            task_info["next_run"] = self._calculate_next_run(task_info["cron"])
            task_info["run_count"] += 1
            
            # Record in workforce manager if agent_id is provided
            if self.workforce_manager and task_info.get("agent_id"):
                self.workforce_manager.record_run(task_info["agent_id"], success=True)
            
            logger.info(f"✅ Task completed: {task_id}")
            
        except Exception as e:
            logger.error(f"❌ Task failed: {task_id} - {e}")
            
            # Record failure
            if self.workforce_manager and task_info.get("agent_id"):
                self.workforce_manager.record_run(task_info["agent_id"], success=False)
    
    async def run(self) -> None:
        """
        Main scheduler loop.
        Checks every minute for tasks that need to run.
        """
        self.running = True
        logger.info("🚀 AgentScheduler started")
        
        while self.running:
            now = datetime.now()
            
            # Check each scheduled task
            for task_id, task_info in list(self.scheduled_tasks.items()):
                if now >= task_info["next_run"]:
                    # Run task in background
                    asyncio.create_task(self._execute_task(task_id, task_info))
            
            # Sleep for 1 minute
            await asyncio.sleep(60)
        
        logger.info("🛑 AgentScheduler stopped")
    
    def stop(self) -> None:
        """Stop the scheduler."""
        self.running = False
    
    def get_status(self) -> Dict:
        """Get scheduler status."""
        return {
            "running": self.running,
            "total_tasks": len(self.scheduled_tasks),
            "tasks": [
                {
                    "task_id": task_id,
                    "cron": info["cron"],
                    "agent_id": info.get("agent_id"),
                    "last_run": info["last_run"].isoformat() if info["last_run"] else None,
                    "next_run": info["next_run"].isoformat(),
                    "run_count": info["run_count"]
                }
                for task_id, info in self.scheduled_tasks.items()
            ]
        }
