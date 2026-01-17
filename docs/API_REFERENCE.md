# API Reference for ICGL

The ICGL system provides REST and WebSocket endpoints for interacting with the system programmatically.

## REST Endpoints

- **`/decision`**: Endpoint for initiating a decision loop.
- **`/status`**: Returns the current status of the system.

## WebSocket Endpoints

- **`/events`**: Stream of system events.

## Request/Response Examples

```json
{
  "method": "POST",
  "url": "/decision",
  "body": {
    "decisionType": "simple"
  }
}
```

This example demonstrates how to initiate a decision loop using the REST API.