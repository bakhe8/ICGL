"""
Observability Instrumentation
------------------------------

Decorators and helpers for automatic event logging.
"""

import asyncio
import time
from datetime import datetime
from functools import wraps
from typing import Callable, Optional

from ..kb.schemas import uid
from ..utils.logging_config import get_logger
from .events import EventType, ObservabilityEvent
from .ledger import ObservabilityLedger

logger = get_logger(__name__)

# Global ledger instance
_ledger: Optional[ObservabilityLedger] = None


def init_observability(db_path: str) -> None:
    """Initialize global observability ledger"""
    global _ledger
    from pathlib import Path

    _ledger = ObservabilityLedger(Path(db_path))
    logger.info(f"✅ Observability initialized: {db_path}")


def get_ledger() -> Optional[ObservabilityLedger]:
    """Get global ledger instance"""
    return _ledger


def observe(event_type: EventType, action: str, actor_type: str = "agent"):
    """
    Decorator to automatically log async function calls.

    Usage:
        @observe(EventType.AGENT_INVOKED, "analyze")
        async def analyze(self, problem, kb, **context):
            ...

    The decorator will log:
    - Function invocation (with input)
    - Function completion (with output and duration)
    - Function failure (with error)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not _ledger:
                # Observability not initialized, just run normally
                return await func(*args, **kwargs)

            # Extract context
            trace_id = kwargs.get("trace_id", uid())
            span_id = uid()
            parent_span_id = kwargs.get("parent_span_id")
            session_id = kwargs.get("session_id", "unknown")
            adr_id = kwargs.get("adr_id")

            # Inject trace context for nested calls
            kwargs["trace_id"] = trace_id
            kwargs["parent_span_id"] = span_id

            # Determine actor_id
            actor_id = "unknown"
            if args and hasattr(args[0], "__class__"):
                actor_id = args[0].__class__.__name__

            start_time = time.time()

            # Log invocation
            try:
                _ledger.log(
                    ObservabilityEvent(
                        event_id=uid(),
                        event_type=event_type,
                        timestamp=datetime.utcnow(),
                        trace_id=trace_id,
                        span_id=span_id,
                        parent_span_id=parent_span_id,
                        session_id=session_id,
                        adr_id=adr_id,
                        actor_type=actor_type,
                        actor_id=actor_id,
                        action=action,
                        target=None,
                        input_payload={"function": func.__name__, "args_count": len(args)},
                        output_payload=None,
                        status="pending",
                        error_message=None,
                        duration_ms=None,
                        tags={"function": func.__name__},
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to log invocation: {e}")

            try:
                # Execute function
                result = await func(*args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)

                # Log success
                try:
                    _ledger.log(
                        ObservabilityEvent(
                            event_id=uid(),
                            event_type=EventType.AGENT_RESPONDED,
                            timestamp=datetime.utcnow(),
                            trace_id=trace_id,
                            span_id=span_id,
                            parent_span_id=parent_span_id,
                            session_id=session_id,
                            adr_id=adr_id,
                            actor_type=actor_type,
                            actor_id=actor_id,
                            action=action,
                            target=None,
                            input_payload=None,
                            output_payload={"success": True},
                            status="success",
                            error_message=None,
                            duration_ms=duration_ms,
                            tags={"function": func.__name__},
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to log success: {e}")

                return result

            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)

                # Log failure
                try:
                    _ledger.log(
                        ObservabilityEvent(
                            event_id=uid(),
                            event_type=EventType.AGENT_FAILED,
                            timestamp=datetime.utcnow(),
                            trace_id=trace_id,
                            span_id=span_id,
                            parent_span_id=parent_span_id,
                            session_id=session_id,
                            adr_id=adr_id,
                            actor_type=actor_type,
                            actor_id=actor_id,
                            action=action,
                            target=None,
                            input_payload=None,
                            output_payload=None,
                            status="failure",
                            error_message=str(e),
                            duration_ms=duration_ms,
                            tags={"function": func.__name__, "error_type": type(e).__name__},
                        )
                    )
                except Exception as log_error:
                    logger.warning(f"Failed to log error: {log_error}")

                raise  # Re-raise original exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            """Sync version (for non-async functions)"""
            if not _ledger:
                return func(*args, **kwargs)

            # Similar logic but without async/await
            trace_id = kwargs.get("trace_id", uid())
            span_id = uid()
            parent_span_id = kwargs.get("parent_span_id")
            session_id = kwargs.get("session_id", "unknown")
            adr_id = kwargs.get("adr_id")

            kwargs["trace_id"] = trace_id
            kwargs["parent_span_id"] = span_id

            actor_id = "unknown"
            if args and hasattr(args[0], "__class__"):
                actor_id = args[0].__class__.__name__

            start_time = time.time()

            try:
                _ledger.log(
                    ObservabilityEvent(
                        event_id=uid(),
                        event_type=event_type,
                        timestamp=datetime.utcnow(),
                        trace_id=trace_id,
                        span_id=span_id,
                        parent_span_id=parent_span_id,
                        session_id=session_id,
                        adr_id=adr_id,
                        actor_type=actor_type,
                        actor_id=actor_id,
                        action=action,
                        target=None,
                        input_payload={"function": func.__name__},
                        status="pending",
                        tags={"function": func.__name__},
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to log invocation: {e}")

            try:
                result = func(*args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)

                try:
                    _ledger.log(
                        ObservabilityEvent(
                            event_id=uid(),
                            event_type=EventType.AGENT_RESPONDED,
                            timestamp=datetime.utcnow(),
                            trace_id=trace_id,
                            span_id=span_id,
                            parent_span_id=parent_span_id,
                            session_id=session_id,
                            adr_id=adr_id,
                            actor_type=actor_type,
                            actor_id=actor_id,
                            action=action,
                            status="success",
                            duration_ms=duration_ms,
                            tags={"function": func.__name__},
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to log success: {e}")

                return result

            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)

                try:
                    _ledger.log(
                        ObservabilityEvent(
                            event_id=uid(),
                            event_type=EventType.AGENT_FAILED,
                            timestamp=datetime.utcnow(),
                            trace_id=trace_id,
                            span_id=span_id,
                            parent_span_id=parent_span_id,
                            session_id=session_id,
                            adr_id=adr_id,
                            actor_type=actor_type,
                            actor_id=actor_id,
                            action=action,
                            status="failure",
                            error_message=str(e),
                            duration_ms=duration_ms,
                            tags={"function": func.__name__},
                        )
                    )
                except Exception as log_error:
                    logger.warning(f"Failed to log error: {log_error}")

                raise

        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
