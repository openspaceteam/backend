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

    def difficulty_post_processor(self, diff):
        return diff


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


class Alien(GameModifier):
    DESCRIPTION = "Errore di traduzione"

    def grid_post_processor(self, grid):
        total_alien = 0

        # At least 2 commands with wrong name
        while total_alien == 0:
            for o in grid.objects:
                if random.randrange(0, 2) == 0:
                    total_alien += 1
                    o.additional_data["alien"] = True
                if total_alien >= 2:
                    break


class AsteroidsField(GameModifier):
    DESCRIPTION = "Campo di asteroidi in arrivo"

    def difficulty_post_processor(self, diff):
        print(diff)
        diff["asteroid_chance"] *= 3
        diff["black_hole_chance"] /= 2
        diff["special_command_cooldown"] //= 2
        return diff


class BlackHolesField(GameModifier):
    DESCRIPTION = "Campo di buchi neri in arrivo"

    def difficulty_post_processor(self, diff):
        print(diff)
        diff["black_hole_chance"] *= 3
        diff["asteroid_chance"] /= 2
        diff["special_command_cooldown"] //= 2
        return diff
