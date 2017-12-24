from constants import client_statuses
from singletons.client_manager import ClientManager


class Client:
    def __init__(self, sid):
        self.sid = sid
        self.uid = ClientManager().next_uid()
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
            self._game = None

    @property
    def game(self):
        return self._game

    @property
    def is_in_game(self):
        return self._game is not None

    @property
    def is_host(self):
        if not self.is_in_game:
            return False
        host_slot = self._game.get_host()
        return host_slot.client == self

