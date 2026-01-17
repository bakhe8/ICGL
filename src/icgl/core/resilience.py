"""
ICGL Resilience Layer
=====================

"The Shield of the System."
Provides validation boundaries and failure containment.
"""

import functools
import logging
from typing import Any, Callable, Optional, Coroutine
from .observability import SystemObserver

class FailureContainer:
    """
    Wraps execution boundaries to prevent system-wide crashes.
    Catches exceptions, logs them to the Observability layer, 
    and returns safe fallback values.
    """
    def __init__(self, observer: Optional[SystemObserver] = None):
        self.observer = observer or SystemObserver()

    def safe_async(self, fallback_factory: Callable[[], Any]):
        """
        Decorator for Async methods.
        fallback_factory: A function that returns the fallback value.
        """
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    # 1. Log to Console
                    print(f"🛡️ [Shield] Caught Exception in {func.__name__}: {str(e)}")
                    
                    # 2. Extract Context (Best Effort)
                    agent_id = "unknown"
                    if args and hasattr(args[0], "agent_id"):
                        agent_id = args[0].agent_id
                        
                    # 3. Log to Observability
                    self.observer.record_metric(
                        agent_id=agent_id,
                        role="error",
                        latency=0.0,
                        confidence=0.0,
                        success=False,
                        error_code=str(e)
                    )
                    
                    # 4. Return Fallback
                    return fallback_factory()
            return wrapper
        return decorator
