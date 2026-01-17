"""
Trace Graph Builder
-------------------

Transforms flat observability events into a directed graph for visualization.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .events import ObservabilityEvent

class TraceGraphBuilder:
    """Builds a graph structure from a trace's event log."""
    
    def build(self, trace_id: str, events: List[ObservabilityEvent]) -> Dict[str, Any]:
        """
        Convert events to React Flow compatible graph structure.
        """
        if not events:
            return None
            
        # Sort by time
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        start_time = sorted_events[0].timestamp
        end_time = sorted_events[-1].timestamp
        
        nodes = []
        edges = []
        
        # 1. diverse set of actors
        actors = set()
        event_types = set()
        failures = 0
        
        # Map span_id -> event for parent linking
        span_map = {e.span_id: e for e in events}
        
        for idx, event in enumerate(sorted_events):
            actors.add(event.actor_id)
            event_types.add(event.event_type.value)
            if event.status == "error":
                failures += 1
                
            # Create Node
            node = {
                "id": event.event_id,
                "index": idx,
                "type": event.event_type.value,
                "actor": event.actor_id,
                "actor_type": event.actor_type,
                "timestamp": event.timestamp.isoformat(),
                "status": event.status,
                "data": {
                    "action": event.action,
                    "target": event.target,
                    "duration_ms": event.duration_ms,
                    "error": event.error_message,
                    "input_size": len(str(event.input_payload or "")),
                    "output_size": len(str(event.output_payload or ""))
                },
                "tags": event.tags
            }
            nodes.append(node)
            
            # Create Edge (Parent -> Child)
            if event.parent_span_id and event.parent_span_id in span_map:
                parent_event = span_map[event.parent_span_id]
                
                # Find parent event's node ID (which is the event_id)
                # In a real distributed system, span_id might map to multiple events (start/end)
                # Here we assume 1:1 for simplicity or map to the 'latest' event of that span
                
                edge = {
                    "from": parent_event.event_id,
                    "to": event.event_id,
                    "label": event.action or "calls",
                    "duration_ms": (event.timestamp - parent_event.timestamp).total_seconds() * 1000
                }
                edges.append(edge)

        # Metadata
        metadata = {
            "total_events": len(events),
            "duration_ms": (end_time - start_time).total_seconds() * 1000,
            "success_count": len(events) - failures,
            "failure_count": failures,
            "success_rate": (len(events) - failures) / len(events) if events else 0,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "actors": list(actors),
            "event_types": list(event_types)
        }
        
        return {
            "trace_id": trace_id,
            "nodes": nodes,
            "edges": edges,
            "metadata": metadata
        }
