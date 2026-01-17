"""Test /chat endpoint"""
import json

# Simulate POST test (would use requests library in real scenario)
test_request = {
    "message": "help",
    "context": {"human_id": "test_user"}
}

print("Test Request:")
print(json.dumps(test_request, indent=2))
print("\nExpected: Help response with suggestions")
