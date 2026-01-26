class EventType:
    USER_MESSAGE = "USER_MESSAGE"
    SYSTEM_EVENT = "SYSTEM_EVENT"

    def __init__(self, event_type: str):
        self.value = event_type

    def __repr__(self):
        return f"EventType({self.value})"

