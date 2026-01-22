# Stub for broadcaster
class Broadcaster:
    def broadcast(self, message):
        pass

    def subscribe(self, websocket):
        # noop for stub
        return True

    def unsubscribe(self, websocket):
        return True

def get_broadcaster():
    return Broadcaster()
