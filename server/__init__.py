import logging

from server.client import Client
from server.game import Game
from singletons.client_manager import ClientManager
from singletons.lobby_manager import LobbyManager
from singletons.sio import Sio
from utils import server

sio = Sio()

# TODO: some of these raise uncaught runtime errors in akerino edge cases


@sio.on("connect")
async def connect(sid, environ):
    c = Client(sid)
    ClientManager().add_client(c)
    await sio.emit("welcome", {"uid": c.uid}, room=sid)
    logging.info("{} connected".format(c.uid))


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
@server.client_not_in_game
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
        if g.public and not g.playing:
            await sio.emit("lobby_info", g.sio_lobby_info(), room=sid)
    logging.info("{} joined lobby".format(sid))


@sio.on("leave_lobby")
@server.base
@server.link_client
async def leave_lobby(sid, data, client):
    sio.leave_room(client.sid, "lobby")
    logging.info("{} left lobby".format(sid))


@sio.on("join_game")
@server.base
@server.link_client
@server.client_not_in_game
@server.args(("game_id", str))
async def join_game(sid, data, client):
    if data["game_id"].lower() not in LobbyManager():
        logging.warning("{} tried to enter unknown game {}".format(sid, data["game_id"]))
        await sio.emit("game_join_fail", {
            "message": "Partita non trovata"
        })
    else:
        await LobbyManager()[data["game_id"]].join_client(client)


@sio.on("change_game_settings")
@server.base
@server.link_client
@server.client_in_game
@server.client_is_host
async def change_game_settings(sid, data, client):
    kwargs = {}
    if "size" in data and type(data["size"]) is int:
        kwargs["size"] = data["size"]
    if "public" in data and type(data["public"]) is bool:
        kwargs["public"] = data["public"]
    await client.game.update_settings(**kwargs)


@sio.on("ready")
@server.base
@server.link_client
@server.client_in_game
async def toggle_ready(sid, _, client):
    await client.game.ready(client)


@sio.on("leave_game")
@server.base
@server.link_client
@server.client_in_game
async def leave_game(sid, _, client):
    await client.leave_game()


@sio.on("start_game")
@server.base
@server.link_client
@server.client_in_game
@server.client_is_host
async def start_game(sid, _, client):
    try:
        await client.game.start()
    except RuntimeError:
        logging.warning("{} game wanted to start, but requirements arent met".format(client.game.uuid))