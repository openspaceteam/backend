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
            "nouns": [],
            "adjectives": []
        }

        self.FEMININE = {
            "nouns": [],
            "adjectives": []
        }

        self.VERBS = []

    def load_nouns(self):
        with open("words/nouns.txt", "r") as f:
            lines = [x.lower().strip() for x in f.readlines()]

        for line in lines:
            noun, gender = line.split(",")
            if gender == "f":
                dest_list = self.FEMININE["nouns"]
            else:
                dest_list = self.MASCULINE["nouns"]

            dest_list.append(noun)

    def load_adjectives(self):
        with open("words/adjectives.txt", "r") as f:
            lines = [x.lower().strip() for x in f.readlines()]

        for line in lines:
            parts = line.split(",")
            if len(parts) == 1:
                # Same for feminine and masculine
                self.MASCULINE["adjectives"].append(line)
                self.FEMININE["adjectives"].append(line)
            else:
                # Different feminine and masculine variants
                self.MASCULINE["adjectives"].append(parts[0])
                self.FEMININE["adjectives"].append(parts[1])

    def load_verbs(self):
        with open("words/verbs.txt", "r") as f:
            self.VERBS = [x.lower().strip() for x in f.readlines()]

    def load(self):
        self.load_nouns()
        self.load_adjectives()
        self.load_verbs()