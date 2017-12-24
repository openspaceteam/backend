import logging
import random

from server import Client
from singletons.lobby_manager import LobbyManager
from singletons.sio import Sio


class Slot:
    def __init__(self, client, ready=False, host=False):
        self.client = client
        self.ready = ready
        self.host = host

    def sio_slot_info(self):
        return {
            "uid": self.client.uid,
            "ready": self.ready,
            "host": self.host
        }


class Game:
    def __init__(self, name, public):
        self._uuid = None   # implemented as a property
        self.name = name
        self.public = public
        self.clients = []
        self.max_players = 2
        self.playing = False

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
        if self.playing:
            raise RuntimeError("The game is in progress!")
        if type(client) is not Client:
            raise TypeError("`client` must be a Client object")
        # if client in self.clients:
        #     raise ValueError("This client is already in that lobby")

        # Make sure the room is not completely full
        if len(self.clients) >= self.max_players:
            await Sio().emit("game_join_fail", {
                "message": "La partita è piena"
            }, room=client.sid)
            return

        # Add the client to this match's clients
        self.clients.append(Slot(client, host=len(self.clients) == 0))

        # Enter sio room
        Sio().enter_room(client.sid, self.sio_room)

        # Bind client to this game
        await client.join_game(self)

        # Notify joined client
        await Sio().emit("game_join_success", {
            "game_id": self.uuid
        }, room=client.sid)

        # Notify other clients (if this is not the first one joining aka the one creating the room)
        # await Sio().emit("client_joined", room=self.sio_room, skip_sid=client.sid)
        if len(self.clients) > 0:
            await self.notify_game()

        # Notify lobby if public
        await self.notify_lobby()

        logging.info("{} joined game {}".format(client.sid, self.uuid))

    async def remove_client(self, client):
        if type(client) is not Client:
            raise TypeError("`client` must be a Client object")
        # if client not in self.clients:
        #     raise ValueError("This client is not in that lobby")

        # Get client to remove
        slot_to_remove = None
        for c in self.clients:
            if c.client == client:
                slot_to_remove = c

        if slot_to_remove is None:
            raise ValueError("This client is not in that lobby")

        # Remove the client
        self.clients.remove(slot_to_remove)

        # Leave sio room
        Sio().leave_room(client.sid, self.sio_room)

        # Notify leaving client
        # await Sio().emit("game_leave_success", room=client.sid)

        # Choose another host if host left
        if slot_to_remove.host and len(self.clients) > 0:
            new_host = random.choice(self.clients)
            new_host.host = True
            logging.info("{} chosen as new host in game {}".format(client.sid, self.uuid))

        # Do lobby stuff if the game is not in progress
        if not self.playing:
            # Notify other clients
            await self.notify_game()

            # Notify lobby
            await self.notify_lobby()

            # Dispose room if everyone left
            if self.is_empty:
                await LobbyManager().remove_game(self)
        logging.info("{} left game {}".format(client.sid, self.uuid))

    @property
    def sio_room(self):
        return "game/{}".format(self.uuid)

    @property
    def is_empty(self):
        return len(self.clients) == 0

    async def notify_lobby(self):
        if self.public:
            await Sio().emit("lobby_info", self.sio_lobby_info(), room="lobby")

    async def notify_game(self):
        await Sio().emit("game_info", self.sio_game_info(), room=self.sio_room)

    async def notify_lobby_dispose(self):
        await Sio().emit("lobby_disposed", {
            "game_id": self.uuid
        }, room="lobby")

    def sio_lobby_info(self):
        return {
            "name": self.name,
            "game_id": self.uuid,
            "players": len(self.clients),
            "max_players": self.max_players,
            "public": self.public
        }

    def sio_game_info(self):
        return {**self.sio_lobby_info(), **{
            "slots": [x.sio_slot_info() for x in self.clients] + [None] * (self.max_players - len(self.clients))
        }}

    def get_host(self):
        for x in self.clients:
            if x.host:
                return x
        return None

    def get_slot(self, client):
        for x in self.clients:
            if x.client == client:
                return x
        return None

    async def update_settings(self, size=None, public=None):
        if self.playing:
            raise RuntimeError("Game in progress!")
        visibility_changed = False
        if size is not None and 2 <= size <= 4:
            self.max_players = size
        if public is not None:
            self.public = public
            visibility_changed = True
        await self.notify_game()

        if self.public:
            # If the game is public, always send updated info to lobby
            await self.notify_lobby()
        elif visibility_changed:
            # Otherwise, if it has just changed to private,
            # make it disappear in lobbies list
            await self.notify_lobby_dispose()

    async def ready(self, client):
        if self.playing:
            raise RuntimeError("Game in progress!")
        slot = self.get_slot(client)
        if slot is None:
            raise ValueError("Client not in match")
        slot.ready = not slot.ready
        await self.notify_game()

    async def start(self):
        if len(self.clients) > 1 and all([x.ready for x in self.clients]):
            # Game starts
            self.playing = True

            # Remove game from lobby
            await self.notify_lobby_dispose()

            # Notify all clients
            await Sio().emit("game_started", room=self.sio_room)
        else:
            raise RuntimeError("Conditions not met for game to start")
