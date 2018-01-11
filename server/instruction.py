import random

from utils.grid import Button, SliderLikeElement, Switch, Actions, GridElement
from utils.special_commands import DummyBlackHoleCommand, DummyAsteroidCommand, SpecialCommand


class Instruction:
    def __init__(self, source, target, target_command):
        self.source = source
        self.target = target
        self.target_command = target_command
        self.value = self.generate_value()  # new value to set the target command to. Only for sliders/switches
        self.text = self.generate_text()    # instruction text, visible to the client

    def generate_value(self):
        if type(self.target_command) is Button:
            # No extra actions required for buttons
            return None
        elif issubclass(type(self.target_command), SpecialCommand):
            # Same for asteroids and black holes
            return None
        elif issubclass(type(self.target_command), SliderLikeElement):
            # For slider-like elements, pick a new random value between min and max, excluding the current one
            return random.choice([x for x in range(self.target_command.min, self.target_command.max + 1) if x != self.target_command.value])
        elif type(self.target_command) is Switch:
            # If it's a switch, flip it
            return not self.target_command.toggled
        elif type(self.target_command) is Actions:
            return random.choice(self.target_command.actions)

    def generate_text(self):
        if type(self.target_command) is Button:
            sentences = [
                "Azionare {name}",
                "Innestare {name}",
                "Premere {name}"
            ]
        elif issubclass(type(self.target_command), SliderLikeElement):
            sentences = [
                "Impostare {name} a {value}",
                "Cambiare {name} a {value}",
                "Posizionare {name} su {value}",
            ]
            if self.value > self.target_command.value:
                sentences.append("Aumentare {name} a {value}")
            else:
                sentences += ["Diminuire {name} a {value}", "Ridurre {name} a {value}"]

            if self.value == self.target_command.max:
                sentences += ["Aumentare {name} al massimo", "Impostare {name} al massimo"]
            elif self.value == self.target_command.min:
                sentences += ["Diminuire {name} al minimo", "Impostare {name} al minimo"]
        elif type(self.target_command) is Actions:
            sentences = ["{value} {name}"]
        elif type(self.target_command) is Switch:
            # Switch
            if self.value:
                sentences = [
                    "Attivare {name}",
                    "Innestare {name}",
                    "Accendere {name}",
                ]
            else:
                sentences = [
                    "Disattivare {name}",
                    "Disinnestare {name}",
                    "Spegnere {name}",
                ]
        elif type(self.target_command) is DummyAsteroidCommand:
            sentences = ["Asteroide! (scuotere tutti il mouse)"]
        elif type(self.target_command) is DummyBlackHoleCommand:
            sentences = ["Buco nero! (premere tutti la barra spazio più volte)"]
        else:
            raise ValueError("Invalid command type")

        # Choose a random sentence form the possible ones and format it
        sentence = random.choice(sentences)
        name = self.target_command.name if issubclass(type(self.target_command), GridElement) else ""
        return sentence.format(name=name, value=self.value).capitalize()
