import socketio

from utils.singleton import singleton


@singleton
class Sio(socketio.AsyncServer):
    pass