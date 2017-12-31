import random

from singletons.words_storage import WordsStorage


class CommandNameGenerator:
    def __init__(self):
        self.used_nouns = []
        self.used_adjectives = []
        self.used_verbs = []

    def generate_compound_noun(self):
        if random.getrandbits(1) == 1:
            nouns = WordsStorage().MASCULINE["nouns"]
        else:
            nouns = WordsStorage().FEMININE["nouns"]

        prefix = random.choice(WordsStorage().PREFIXES).lower()

        while True:
            noun = random.choice(nouns).lower()
            if noun not in self.used_nouns:
                break
        self.used_nouns.append(noun)

        if prefix.endswith(noun[0]):
            prefix += "-"
        elif " " in noun:
            prefix += " "
        return "{}{}".format(prefix, noun)

    def generate_noun_adjective(self):
        if random.getrandbits(1) == 0:
            nouns = WordsStorage().MASCULINE["nouns"]
            adjectives = WordsStorage().MASCULINE["adjectives"]
        else:
            nouns = WordsStorage().FEMININE["nouns"]
            adjectives = WordsStorage().FEMININE["adjectives"]

        while True:
            noun = random.choice(nouns)
            adjective = random.choice(adjectives)
            if noun not in self.used_nouns and adjective not in self.used_adjectives:
                break
        self.used_nouns.append(noun)
        self.used_adjectives.append(adjective)

        return "{} {}".format(noun, adjective)

    def generate_command_name(self):
        if random.randint(0, 2) == 0:
            return self.generate_noun_adjective()
        else:
            return self.generate_compound_noun()

    def generate_action(self):
        while True:
            verb = random.choice(WordsStorage().VERBS)
            if verb not in self.used_verbs:
                break
        self.used_verbs.append(verb)
        return verb
