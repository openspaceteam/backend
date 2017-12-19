from constants import client_statuses


class Client:
    def __init__(self, sid):
        self.sid = sid
        self.status = client_statuses.NONE
        self._game = None

    async def dispose(self):
        # Leave joined game
        await self.leave_game()
        # TODO: Check if joined rooms are automatically left

    async def join_game(self, game):
        await self.leave_game()
        self._game = game

    async def leave_game(self):
        if self._game is not None:
            await self._game.remove_client(self)

