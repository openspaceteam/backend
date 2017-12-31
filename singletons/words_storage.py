from utils.singleton import singleton


@singleton
class WordsStorage:
    def __init__(self):
        self.PREFIXES = [
            "ultra", "super", "mega", "proto", "sub", "pro", "alter", "stra", "de", "iono", "arci", "bio",
            "mono", "bi", "tri", "quadri", "penta", "esa", "otta", "deca", "multi",
            "emi", "olo", "pseudo", "termo", "turbo", "ipno", "infra", "astro", "macro", "spettro", "fanta", "tele"
        ]

        self.MASCULINE = {
            "rare_nouns": [],
            "rare_adjectives": [],
            "nouns": [],
            "adjectives": []
        }

        self.FEMININE = {
            "rare_nouns": [],
            "rare_adjectives": [],
            "nouns": [],
            "adjectives": []
        }

        self.VERBS = []

    def load_nouns(self):
        lines = []
        with open("words/nouns.txt", "r") as f:
            lines += [(x.lower().strip(), False) for x in f.readlines()]
        with open("words/rare_nouns.txt", "r") as f:
            lines += [(x.lower().strip(), True) for x in f.readlines()]

        for (line, rare) in lines:
            noun, gender = line.split(",")
            if gender == "f":
                dest_list = self.FEMININE["{}nouns".format("rare_" if rare else "")]
            else:
                dest_list = self.MASCULINE["{}nouns".format("rare_" if rare else "")]

            dest_list.append(noun)

    def load_adjectives(self):
        lines = []
        with open("words/adjectives.txt", "r") as f:
            lines += [(x.lower().strip(), False) for x in f.readlines()]
        with open("words/rare_adjectives.txt", "r") as f:
            lines += [(x.lower().strip(), True) for x in f.readlines()]

        for (line, rare) in lines:
            parts = line.split(",")
            if len(parts) == 1:
                # Same for feminine and masculine
                self.MASCULINE["{}adjectives".format("rare_" if rare else "")].append(line)
                self.FEMININE["{}adjectives".format("rare_" if rare else "")].append(line)
            else:
                # Different feminine and masculine variants
                self.MASCULINE["{}adjectives".format("rare_" if rare else "")].append(parts[0])
                self.FEMININE["{}adjectives".format("rare_" if rare else "")].append(parts[1])

    def load_verbs(self):
        with open("words/verbs.txt", "r") as f:
            self.VERBS = [x.lower().strip() for x in f.readlines()]

    def load(self):
        self.load_nouns()
        self.load_adjectives()
        self.load_verbs()