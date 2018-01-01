import logging
import uuid

import server.game
from singletons.sio import Sio
from utils.singleton import singleton


@singleton
class LobbyManager:
    def __init__(self):
        self._games_by_uuid = {}

    async def add_game(self, game):
        """
        Adds a game to registered games
        :param game:
        :return:
        """
        if type(game) is not server.Game:
            raise TypeError("`game` is not a Game object")

        # Generate UUID and register game
        game.uuid = self.generate_uuid()
        self._games_by_uuid[game.uuid] = game

        # Notify lobby
        await game.notify_lobby()

        logging.info("Registered game {}".format(game.uuid))

    async def remove_game(self, game):
        """
        Removes a previously registered game
        :param game:
        :return:
        """
        if type(game) is not server.game.Game:
            raise TypeError("`game` is not a Game object")
        if game.uuid is None:
            raise TypeError("This game doesn't have an uuid")
        if game.uuid not in self._games_by_uuid:
            raise KeyError("This game is not registered")

        # Notify lobby if not already in game
        if not self._games_by_uuid[game.uuid].playing:
            await self._games_by_uuid[game.uuid].notify_lobby_dispose()

        # Remove game
        del self._games_by_uuid[game.uuid]

        logging.info("Removed game {}".format(game.uuid))

    def generate_uuid(self):
        """
        Generates a valid and random UUID
        :return:
        """
        valid = False
        _uuid = None
        while not valid:
            _uuid = str(uuid.uuid4())
            if _uuid not in self._games_by_uuid:
                valid = True
        return _uuid

    def items(self):
        return self._games_by_uuid.items()

    def __getitem__(self, item):
        return self._games_by_uuid[item]

    def __contains__(self, item):
        return item in self._games_by_uuid
