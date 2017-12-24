import server.client
from utils.singleton import singleton


@singleton
class ClientManager:
    def __init__(self):
        self._clients_by_sid = {}
        self._uid = 0

    def add_client(self, client):
        if type(client) is not server.client.Client:
            raise TypeError("`client` is not a Client object")
        if client.sid in self._clients_by_sid:
            raise ValueError("This client has already been registered")
        self._clients_by_sid[client.sid] = client

    def remove_client(self, client):
        if type(client) is not server.client.Client:
            raise TypeError("`client` is not a Client object")
        if client.sid not in self._clients_by_sid:
            raise KeyError("This client is not registered")
        del self._clients_by_sid[client.sid]

    def __getitem__(self, item):
        return self._clients_by_sid[item]

    def next_uid(self):
        self._uid += 1
        return self._uid
