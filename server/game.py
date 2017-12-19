import logging

from server import Client
from singletons.lobby_manager import LobbyManager
from singletons.sio import Sio


class Game:
    def __init__(self, name, public):
        self._uuid = None   # implemented as a property
        self.name = name
        self.public = public
        self.clients = []
        self.max_players = 2

    @property
    def uuid(self):
        """
        uuid property getter
        :return:
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid):
        """
        uuid setter. uuid can be set only one
        :param uuid:
        :return:
        """
        if self._uuid is not None:
            raise RuntimeError("Game's uuid cannot be changed!")
        self._uuid = uuid

    async def join_client(self, client):
        if type(client) is not Client:
            raise TypeError("`client` must be a Client object")
        if client in self.clients:
            raise ValueError("This client is already in that lobby")

        # Add the client to this match's clients
        self.clients.append(client)

        # Enter sio room
        Sio().enter_room(client.sid, self.sio_room)

        # Bind client to this game
        await client.join_game(self)

        # Notify joined client
        await Sio().emit("lobby_joined", {
            "game_id": self.uuid
        }, room=client.sid)

        # Notify other clients
        await Sio().emit("client_joined", room=self.sio_room, skip_sid=client.sid)

        # Notify lobby if public
        await self.notify_lobby()

        logging.info("{} joined game {}".format(client.sid, self.uuid))

    async def remove_client(self, client):
        if type(client) is not Client:
            raise TypeError("`client` must be a Client object")
        if client not in self.clients:
            raise ValueError("This client is not in that lobby")

        # Remove the client
        self.clients.remove(client)

        # Leave sio room
        Sio().leave_room(client.sid, self.sio_room)

        # Notify leaving client
        await Sio().emit("lobby_left", room=client.sid)

        # Notify other clients
        await Sio().emit("client_left", room=self.sio_room)

        # Notify lobby
        await self.notify_lobby()

        logging.info("{} left game {}".format(client.sid, self.uuid))

        # Dispose room if everyone left
        if self.is_empty:
            await LobbyManager().remove_game(self)

    @property
    def sio_room(self):
        return "game/{}".format(self.uuid)

    @property
    def is_empty(self):
        return len(self.clients) == 0

    async def notify_lobby(self):
        if self.public:
            await Sio().emit("lobby_info", self.sio_lobby_info(), room="lobby")

    def sio_lobby_info(self):
        return {
            "name": self.name,
            "game_id": self.uuid,
            "players": len(self.clients),
            "max_players": self.max_players
        }
