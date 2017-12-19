import logging

from server.client import Client
from server.game import Game
from singletons.client_manager import ClientManager
from singletons.lobby_manager import LobbyManager
from singletons.sio import Sio
from utils import server

sio = Sio()


@sio.on("connect")
async def connect(sid, environ):
    ClientManager().add_client(Client(sid))
    logging.info("{} connected".format(sid))


@sio.on("disconnect")
@server.link_client
async def disconnect(sid, data, client):
    try:
        ClientManager().remove_client(client)
        await client.dispose()
        logging.info("{} disconnected".format(sid))
    except KeyError:
        # TODO: Log
        return


@sio.on("create_game")
@server.base
@server.link_client
@server.args(("name", str), ("public", bool))
async def create_game(sid, data, client):
    match = Game(name=data["name"], public=data["public"])
    await LobbyManager().add_game(match)
    try:
        await match.join_client(client)
    except ValueError:
        # Already joined
        return


@sio.on("join_lobby")
@server.base
@server.link_client
async def join_lobby(sid, data, client):
    sio.enter_room(client.sid, "lobby")
    for _, g in LobbyManager().items():
        if g.public:
            await sio.emit("lobby_info", g.sio_lobby_info(), room=sid)
    logging.info("{} joined lobby".format(sid))


@sio.on("leave_lobby")
@server.base
@server.link_client
async def join_lobby(sid, data, client):
    sio.leave_room(client.sid, "lobby")
    logging.info("{} left lobby".format(sid))