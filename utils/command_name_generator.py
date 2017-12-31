import random

from singletons.words_storage import WordsStorage


class CommandNameGenerator:
    def __init__(self):
        self.used_nouns = []
        self.used_adjectives = []
        self.used_verbs = []

    def random_noun(self, masculine=None):
        if masculine is None:
            masculine = random.getrandbits(1) == 1
        if masculine:
            nouns = random.choice([WordsStorage().MASCULINE["rare_nouns"] * 4, WordsStorage().MASCULINE["nouns"]])
        else:
            nouns = random.choice([WordsStorage().FEMININE["rare_nouns"] * 4, WordsStorage().FEMININE["nouns"]])
        return random.choice(nouns).lower()

    def random_adjective(self, masculine=None):
        if masculine is None:
            masculine = random.getrandbits(1) == 1
        if masculine:
            adjectives = random.choice([WordsStorage().MASCULINE["rare_adjectives"] * 4, WordsStorage().MASCULINE["adjectives"]])
        else:
            adjectives = random.choice([WordsStorage().FEMININE["rare_adjectives"] * 4, WordsStorage().FEMININE["adjectives"]])
        return random.choice(adjectives).lower()

    def generate_compound_noun(self):
        prefix = random.choice(WordsStorage().PREFIXES).lower()

        while True:
            noun = self.random_noun()
            if noun not in self.used_nouns:
                break
        self.used_nouns.append(noun)

        if prefix.endswith(noun[0]):
            prefix += "-"
        elif " " in noun:
            prefix += " "
        return "{}{}".format(prefix, noun)

    def generate_noun_adjective(self):
        while True:
            masculine = random.getrandbits(1) == 1
            noun = self.random_noun(masculine)
            adjective = self.random_adjective(masculine)
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
