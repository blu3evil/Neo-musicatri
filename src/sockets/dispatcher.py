from __future__ import annotations

from typing import Optional
# from core import socketio

class AdminSocketDispatcher:
    def emit(self, event, data):
        # socketio.emit(event, data, namespace='/socket/admin')
        pass

admin_socket_dispatcher: Optional[AdminSocketDispatcher] = None

def init_dispatcher():
    global admin_socket_dispatcher
    admin_socket_dispatcher = AdminSocketDispatcher()





