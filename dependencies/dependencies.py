from utils.websocket_manager import WebSocketManager

# Singleton instance of WebSocketManager
socketManager = WebSocketManager()


def get_socket_manager():
    return socketManager
