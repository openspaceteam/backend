from decouple import config

from utils.singleton import singleton


@singleton
class Config:
    def __init__(self):
        self._config = {
            "DEBUG": config("DEBUG", default="0", cast=bool),

            "SIO_HOST": config("SIO_HOST", default="127.0.0.1"),
            "SIO_PORT": config("SIO_PORT", default="4433", cast=int)
        }

    def __getitem__(self, item):
        return self._config[item]
