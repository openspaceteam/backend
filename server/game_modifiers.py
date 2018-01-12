import asyncio
import logging
import random
import string

from singletons.sio import Sio


class GameModifier:
    DESCRIPTION = ""

    def __init__(self, match):
        self.match = match

    async def task(self):
        raise asyncio.CancelledError()

    def grid_post_processor(self, grid):
        return


class FlipGrid(GameModifier):
    DESCRIPTION = "Matrice di riflessione attivata"

    async def task(self):
        while True:
            logging.debug("Screen filp")
            if random.getrandbits(1):
                await Sio().emit("flip_grid", room=self.match.sio_room)
            await asyncio.sleep(8)


class Symbols(GameModifier):
    DESCRIPTION = "$" + "$".join("moxacunis")

    def grid_post_processor(self, grid):
        available_symbols = list(string.ascii_letters + "!#\"$%&'()*+,-./?>=<;:@[]^_`{}~")
        total_symbols = 0

        # At least 2 commands with symbols
        while total_symbols < 2:
            for o in grid.objects:
                if random.randrange(0, 2) == 0:
                    total_symbols += 1
                    o.additional_data["symbol"] = True
                    o.name = random.choice(available_symbols)
                    available_symbols.remove(o.name)
