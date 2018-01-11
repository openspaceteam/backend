import asyncio
import logging
import random

from server import Client
from server.instruction import Instruction
from singletons.config import Config
from singletons.lobby_manager import LobbyManager
from singletons.sio import Sio
from utils.command_name_generator import CommandNameGenerator
from utils.grid import Grid, Button, SliderLikeElement, Actions, Switch, GridElement
from utils.special_commands import DummyAsteroidCommand, DummyBlackHoleCommand, SpecialCommand


class Slot:
    def __init__(self, client, ready=False, host=False):
        self.client = client
        self.ready = ready
        self.intro_done = False
        self.host = host

        self.grid = None
        self.instruction = None
        self.next_generation_task = None

        self.defeating_asteroid = False
        self.defeating_black_hole = False

    def sio_slot_info(self):
        return {
            "uid": self.client.uid,
            "ready": self.ready,
            "host": self.host
        }

    async def reset_asteroid(self, after=2):
        await asyncio.sleep(after)
        self.defeating_asteroid = False
        logging.debug("as def")

    async def reset_black_hole(self, after=2):
        await asyncio.sleep(after)
        self.defeating_black_hole = False
        logging.debug("bh def")


class Game:
    STARTING_HEALTH = 50
    HEALTH_LOOP_RATE = 2
    MAX_PLAYERS = 4

    def __init__(self, name, public):
        self._uuid = None   # implemented as a property

        self.name = name

        self.public = public
        self.max_players = 2

        self.slots = []
        self.playing = False
        self.disposing = False
        self.instructions = []

        self.level = -1
        self.health = self.STARTING_HEALTH
        self.death_limit = 0

        self.health_drain_task = None

        self.difficulty = {
            "instructions_time": 25,
            "health_drain_rate": 0.5,
            "death_limit_increase_rate": 0.05,
            "completed_instruction_health_increase": 10,
            "useless_command_health_decrease": 0,
            "expired_command_health_decrease": 5,
            "asteroid_chance": 0.5,
            "black_hole_chance": 0.5
        }

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
        """
        Adds a client to the match and notifies match and lobby
        :param client: `Client` object
        :return:
        """
        if self.playing:
            raise RuntimeError("The game is in progress!")
        if type(client) is not Client:
            raise TypeError("`client` must be a Client object")
        # if client in self.clients:
        #     raise ValueError("This client is already in that lobby")

        # Make sure the room is not completely full
        if len(self.slots) >= self.max_players:
            await Sio().emit("game_join_fail", {
                "message": "La partita è piena"
            }, room=client.sid)
            return

        # Add the client to this match's clients
        self.slots.append(Slot(client, host=len(self.slots) == 0))

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
        if len(self.slots) > 0:
            await self.notify_game()

        # Notify lobby if public
        await self.notify_lobby()

        logging.info("{} joined game {}".format(client.sid, self.uuid))

        if Config()["SINGLE_PLAYER"]:
            await self.start()

    async def remove_client(self, client):
        """
        Removes a client from the match and notifies game and lobby.
        If the host leaves, a new random host is chosen.
        If all players leave, the match is disposed.
        :param client: `Client` object to remove
        :return:
        """
        if type(client) is not Client:
            raise TypeError("`client` must be a Client object")
        # if client not in self.clients:
        #     raise ValueError("This client is not in that lobby")

        # Get client to remove
        slot_to_remove = None
        for c in self.slots:
            if c.client == client:
                slot_to_remove = c

        if slot_to_remove is None:
            raise ValueError("This client is not in that lobby")

        # Remove the client
        self.slots.remove(slot_to_remove)

        # Leave sio room
        Sio().leave_room(client.sid, self.sio_room)

        if self.playing and not self.disposing:
            # If we are in game, disconnect everyone
            try:
                await Sio().emit('player_disconnected', room=self.sio_room)
                await self.dispose()
            except RuntimeError:
                # Already disposing
                pass
        elif not self.playing:
            # Choose another host if host left
            if slot_to_remove.host and len(self.slots) > 0:
                new_host = random.choice(self.slots)
                new_host.host = True
                logging.info("{} chosen as new host in game {}".format(client.sid, self.uuid))

            # Notify other clients
            await self.notify_game()

            # Notify lobby
            await self.notify_lobby()

            # Dispose room if everyone left
            if self.is_empty:
                await self.dispose()

        logging.info("{} left game {}".format(client.sid, self.uuid))

    @property
    def sio_room(self):
        return "game/{}".format(self.uuid)

    @property
    def is_empty(self):
        return len(self.slots) == 0

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
            "players": len(self.slots),
            "max_players": self.max_players,
            "public": self.public
        }

    def sio_game_info(self):
        return {**self.sio_lobby_info(), **{
            "slots": [x.sio_slot_info() for x in self.slots] + [None] * (self.max_players - len(self.slots))
        }}

    def get_host(self):
        """
        Returns the `Slot` object of this match's host
        :return: `Slot` object or `None` if there's no host set
        """
        for x in self.slots:
            if x.host:
                return x
        return None

    def get_slot(self, client):
        """
        Get the `Slot` object corresponding to `Client`
        :param client:
        :return: `Slot` object or `None` if the client is not in this match
        """
        for x in self.slots:
            if x.client == client:
                return x
        return None

    async def update_settings(self, size=None, public=None):
        """
        Updates game settings and broadcasts events to game and lobby
        :param size: new size. min 2 max 4. Use `None` to leave untouched.
        :param public: new public status (True/False). Use `None` to leave untouched.
        :return:
        """
        if self.playing:
            raise RuntimeError("Game in progress!")
        visibility_changed = False
        if size is not None and 2 <= size <= self.MAX_PLAYERS:
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
        """
        Toggles `client`'s ready status
        :param client: `Client` object
        :return:
        """
        if self.playing:
            raise RuntimeError("Game in progress!")
        slot = self.get_slot(client)
        if slot is None:
            raise ValueError("Client not in match")
        slot.ready = not slot.ready
        await self.notify_game()

    async def start(self):
        """
        Starts the game
        :return:
        """
        if len(self.slots) > 1 and all([x.ready for x in self.slots]) or Config()["SINGLE_PLAYER"]:
            # Game starts
            self.playing = True

            # Remove game from lobby
            await self.notify_lobby_dispose()

            # First level
            await self.next_level()

            # Notify all clients
            await Sio().emit("game_started", room=self.sio_room)
        else:
            raise RuntimeError("Conditions not met for game to start")

    async def next_level(self):
        """
        Changes level, difficulty, resets intro done,
        sets game modifiera and generates new grids
        :return:
        """
        # Stop drain loop task
        if self.health_drain_task is not None:
            self.health_drain_task.cancel()

        # Stop all command generation loop tasks
        for slot in self.slots:
            if slot.next_generation_task is not None:
                slot.next_generation_task.cancel()

        # Go to next level
        self.level += 1

        # Reset health and death limit
        self.health = self.STARTING_HEALTH
        self.death_limit = 0

        # Change difficulty settings if this is not the first level
        if self.level > 0:
            self.difficulty["instructions_time"] = max(7.0, self.difficulty["instructions_time"] - 2.75)
            self.difficulty["health_drain_rate"] = max(1.75, self.difficulty["health_drain_rate"] - 0.35)
            self.difficulty["death_limit_increase_rate"] = max(1.8, self.difficulty["death_limit_increase_rate"] + 0.35)
            self.difficulty["completed_instruction_health_increase"] = max(
                3.0,
                self.difficulty["completed_instruction_health_increase"] - 0.5
            )
            self.difficulty["expired_command_health_decrease"] = min(
                20.0,
                self.difficulty["expired_command_health_decrease"] + 0.25
            )

            self.difficulty["asteroid_chance"] = 0.25
            self.difficulty["black_hole_chance"] = 0.25

            if self.level > 5:
                self.difficulty["useless_command_health_decrease"] = min(
                    2.25,
                    self.difficulty["useless_command_health_decrease"] + 0.1
                )
            logging.debug("Current difficulty: {}".format(self.difficulty))

        # TODO: Game modifiers

        # Set all `intro done` to false
        for i in self.slots:
            i.intro_done = False

        # Generate grids
        await self.generate_grids()

        # TODO: Broadcast game modifiers (if not first level?)

    async def generate_grids(self):
        """
        Generates new `Grid`s for all clients
        :return:
        """
        if not self.playing:
            raise RuntimeError("Game not in progress!")
        name_generator = CommandNameGenerator()

        for slot in self.slots:
            slot.grid = Grid(name_generator)

    async def intro_done(self, client):
        """
        Sets that a client has played the intro.
        When everyone has played the intro, `self.intro_done_all()` is called
        :param client: `Client` object
        :return:
        """
        if not self.playing:
            raise RuntimeError("Game not in progress!")
        slot = self.get_slot(client)
        if slot is None:
            raise ValueError("Client not in match")

        # This client has played the intro
        slot.intro_done = True

        # Check if everyone has played the intro
        for i in self.slots:
            if not i.intro_done:
                return
        await self.intro_done_all()

    async def intro_done_all(self):
        """
        Called when all clients have played the intro.
        This emits to all clients their `grid` event and the first `command` event
        :return:
        """
        # Notify each client about their grid if eveyone has completed intro
        for slot in self.slots:
            await Sio().emit("grid", slot.grid.__dict__(), room=slot.client.sid)

        # Warmup dummy instruction
        warmup_time = max(int(self.difficulty["instructions_time"] / 5), 3)
        await Sio().emit("command", {
            "text": "Prepararsi a ricevere istruzioni",
            "time": warmup_time
        }, room=self.sio_room)

        # Wait until the dummy instruction expires
        await asyncio.sleep(warmup_time)

        # Generate first command for each slot, starting the regeneration loop as well
        for slot in self.slots:
            await self.generate_instruction(slot)

        # Star the health drain task too
        self.health_drain_task = asyncio.Task(self.health_drain_loop())

    async def generate_instruction(self, slot, expired=None, stop_old_task=True):
        """
        Generates and sets a valid and unique Instruction for `Slot` and schedules
        an asyncio Task to run
        :param slot: `Slot` object that will be the target of that instruction
        :param stop_old_task: if `True`, stop the old generation task.
                              Set to `False` if running in the generation loop, `True` if calling from outside the loop.
        :param expired: Send this to the client with the new instruction.
                        If `True`, the old instruction expired.
                        If `False`, the old instruction was successful.
                        If `None` (or not present), not specified.
                        The client will play sounds and visual fx accordingly.
        :return:
        """
        # Stop the old next generation task if needed
        if slot.next_generation_task is not None and stop_old_task:
            slot.next_generation_task.cancel()
        old_instruction = slot.instruction

        # Choose between an asteroid/black hole or normal command
        command = None
        if random.random() < self.difficulty["asteroid_chance"]:
            # Asteroid, force target and command
            target = None
            command = DummyAsteroidCommand()
        elif random.random() < self.difficulty["black_hole_chance"]:
            # Black hole, force target and command
            target = None
            command = DummyBlackHoleCommand()
        elif Config()["SINGLE_PLAYER"]:
            # Single player debug mode, force target only
            target = slot
        else:
            # Normal, choose a target
            # Choose a random slot and a random command.
            # We don't do this in `Instruction` because we need to access
            # match's properties and passing match and next_levelinstruction to `Instruction` is not elegant imo
            if random.randint(0, 5) == 0:
                # 1/5 chance of getting a command in our grid
                target = slot
            else:
                # Filter out our slot and chose another one randomly
                target = random.choice(list(filter(lambda z: z != slot, self.slots)))

        # Generate a command if needed
        if command is None:
            # Find a random command that is not used in any other instructions at the moment and is not the same as the
            # previous one
            valid_command = False
            while not valid_command:
                valid_command = True
                command = random.choice(target.grid.objects)
                print(self.instructions + [slot.instruction])
                print(slot.instruction)
                for x in self.instructions + [slot.instruction]:
                    # x is `None` if slot.instructions is None (first generation)
                    if x is not None and x.target_command == command:
                        valid_command = False
                        break

        # Set this slot's instruction and notify the client
        slot.instruction = Instruction(slot, target, command)

        # Add new one
        self.instructions.append(slot.instruction)

        # Notify the client about the new command and the status of the old command
        await Sio().emit("command", {
            "text": slot.instruction.text,
            "time": self.difficulty["instructions_time"],
            "expired": expired,
            "special_defeated": issubclass(type(old_instruction.target_command), SpecialCommand) if old_instruction is not None else False
        }, room=slot.client.sid)

        # Schedule a new generation
        slot.next_generation_task = asyncio.Task(self.schedule_generation(slot, self.difficulty["instructions_time"]))

    async def schedule_generation(self, slot, seconds):
        """
        Executes a new instruction generation for `slot` after `seconds` have passed
        :param slot: `Slot` object that will receive the `Instruction`
        :param seconds: number of seconds to wait
        :return:
        """
        await asyncio.sleep(seconds)

        # Remove expired instruction
        if slot.instruction in self.instructions:
            self.instructions.remove(slot.instruction)

        # Drain health
        self.health -= self.difficulty["expired_command_health_decrease"]

        # Generate a new instruction
        await self.generate_instruction(slot, expired=True, stop_old_task=False)  # if True, it would stop itself :|

    async def health_drain_loop(self):
        while True:
            # Drain health every two seconds second
            await asyncio.sleep(self.HEALTH_LOOP_RATE)
            self.health -= self.difficulty["health_drain_rate"] * self.HEALTH_LOOP_RATE
            self.death_limit = min(
                90,
                self.death_limit + self.difficulty["death_limit_increase_rate"] * self.HEALTH_LOOP_RATE
            )
            logging.debug("Draining health, new value {} and death limit is {}".format(self.health, self.death_limit))

            if self.health <= self.death_limit:
                # Game over
                await self.game_over()
                break
            else:
                # Game still in progress, broadcast new health
                await self.notify_health()

    async def game_over(self):
        await Sio().emit("game_over", room=self.sio_room)
        logging.info("{} game over".format(self.uuid))

    async def notify_health(self):
        await Sio().emit("health_info", {
            "health": self.health,
            "death_limit": self.death_limit
        }, room=self.sio_room)

    async def do_command(self, client, command_name, value=None):
        """
        Called when someone does something on a command on their grid
        :param client: `Client` object, must be in game
        :param command_name: changed command name, case insensitive
        :param value: command value, required only for slider-like, actions and switches commands
        :return:
        """
        # Playing/player checks
        if not self.playing:
            raise RuntimeError("Game not in progress!")
        slot = self.get_slot(client)
        if slot is None:
            raise ValueError("Client not in match")

        # Make sure the command is valid
        command = None
        for c in slot.grid.objects:
            if c.name.lower() == command_name:
                command = c
        if command is None:
            raise ValueError("Command not found")

        # Make sure value is valid
        if type(command) is Button and value is not None:
            raise ValueError("Invalid value, must be None")
        elif issubclass(type(command), SliderLikeElement) and type(value) is not int and (value < command.min or value > command.max):
            raise ValueError("Invalid value, must be an int between min and max")
        elif type(command) is Actions and type(value) is not str and value.lower() not in command.actions:
            raise ValueError("Invalid value, must be a valid action")
        elif type(command) is Switch and type(value) is not bool:
            raise ValueError("Invalid value, must be a bool")

        # Update status if it's a slider or switch
        if issubclass(type(command), SliderLikeElement):
            command.value = value
        elif type(command) is Switch:
            command.toggled = value

        # Check if this command completes an instruction
        instruction_completed = None
        for instruction in self.instructions:
            if issubclass(type(instruction.target_command), GridElement) \
                    and instruction.target_command.name.lower() == command_name.lower() and instruction.value == value:
                instruction_completed = instruction

        if instruction_completed is None:
            # Useless command, apply penality
            self.health -= self.difficulty["useless_command_health_decrease"]
            return

        # Complete this instruction and generate a new one
        await self.complete_instruction(instruction_completed)

    async def complete_instruction(self, instruction_completed):
        # Remove old instruction
        self.instructions.remove(instruction_completed)

        # Increase health
        self.health += self.difficulty["completed_instruction_health_increase"]

        # Broadcast new health or next level
        if self.health >= 100:
            # TODO: Game modifiers
            await self.next_level()
            await Sio().emit("next_level", {
                "level": self.level,
                "modifier": None,
                "text": "Nessuna anomalia rilevata"
            }, room=self.sio_room)
        else:
            # This was an useful command! Force new generation outside the loop
            await self.generate_instruction(instruction_completed.source, expired=False, stop_old_task=True)
            await self.notify_health()

    async def dispose(self):
        """
        Disposes the current room
        :return:
        """
        # Make sure the match is not already disposing
        if self.disposing:
            raise RuntimeError("The match is already disposing")
        self.disposing = True

        # Cancel all pending next generation tasks
        for slot in self.slots:
            if slot.next_generation_task is not None:
                logging.debug("slot {} generation task cancelled".format(slot))
                slot.next_generation_task.cancel()

        # Cancel health drain task too
        if self.health_drain_task is not None:
            logging.debug("Health drain task cancelled")
            self.health_drain_task.cancel()

        # Make everyone leave the game
        for slot in self.slots:
            await slot.client.leave_game()

        # Remove from lobby
        await LobbyManager().remove_game(self)

        logging.info("{} match disposed".format(self.uuid))

    async def defeat_special(self, client, black_hole=False):
        # Playing/player checks
        if not self.playing:
            raise RuntimeError("Game not in progress!")
        slot = self.get_slot(client)
        if slot is None:
            raise ValueError("Client not in match")

        # Defeat thing
        if black_hole:
            slot.defeating_black_hole = True
        else:
            slot.defeating_asteroid = True

        # Check if everyone is defeating
        all_defeated = True
        for s in self.slots:
            if (not s.defeating_black_hole and black_hole) or (not s.defeating_asteroid and not black_hole):
                all_defeated = False
                break

        # Everyone has defeated asteroid/black hole!
        if all_defeated:
            logging.debug("All defeated!")

            # Check if there's a special command (we may have more than once)
            instructions_completed = []
            for instruction in self.instructions:
                if (type(instruction.target_command) is DummyBlackHoleCommand and black_hole) \
                        or (type(instruction.target_command) is DummyAsteroidCommand and not black_hole):
                    instructions_completed.append(instruction)

            # Complete all instructions (two loops because we're removing items from self.instructions)
            for instruction in instructions_completed:
                logging.debug("SPECIAL DONE!")
                await self.complete_instruction(instruction)

        # Reset defeating back to False after two seconds
        asyncio.Task(slot.reset_black_hole() if black_hole else slot.reset_asteroid())



