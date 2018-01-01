import random

from utils.grid import Button, SliderLikeElement, Switch, Actions


class Instruction:
    def __init__(self, target, target_command):
        self.target_command = target_command
        self.target = target
        self.value = self.generate_value()  # new value to set the target command to. Only for sliders/switches
        self.text = self.generate_text()    # instruction text, visible to the client

    def generate_value(self):
        if type(self.target_command) is Button:
            # No extra actions required for buttons
            return None
        elif issubclass(type(self.target_command), SliderLikeElement):
            # For slider-like elements, pick a new random value between min and max, excluding the current one
            return random.choice([x for x in range(self.target_command.min, self.target_command.max + 1) if x != self.target_command.value])
        elif type(self.target_command) is Switch:
            # If it's a switch, flip it
            return not self.target_command.toggled

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
                sentences.append("Diminuire {name} a {value}")
        elif type(self.target_command) is Actions:
            sentences = ["{value} {name}"]
        else:
            # Switch
            if self.value:
                sentences = [
                    "Attivare {name}",
                    "Innestare {name}",
                    "Acendere {name}",
                ]
            else:
                sentences = [
                    "Disattivare {name}",
                    "Disinnestare {name}",
                    "Spegnere {name}",
                ]

        # Choose a random sentence form the possible ones and format it
        sentence = random.choice(sentences)
        return sentence.format(name=self.target_command.name, value=self.value)
