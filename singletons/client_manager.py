from server.client import Client
from utils.singleton import singleton


@singleton
class ClientManager:
    def __init__(self):
        self._clients_by_sid = {}

    def add_client(self, client):
        if type(client) is not Client:
            raise TypeError("`client` is not a Client object")
        if client.sid in self._clients_by_sid:
            raise ValueError("This client has already been registered")
        self._clients_by_sid[client.sid] = client

    def remove_client(self, client):
        if type(client) is not Client:
            raise TypeError("`client` is not a Client object")
        if client.sid not in self._clients_by_sid:
            raise KeyError("This client is not registered")
        del self._clients_by_sid[client.sid]

    def __getitem__(self, item):
        return self._clients_by_sid[item]
