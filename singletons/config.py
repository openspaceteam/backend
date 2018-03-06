from decouple import config

from utils.singleton import singleton


@singleton
class Config:
    def __init__(self):
        self._config = {
            "DEBUG": config("DEBUG", default="0", cast=bool),
            "SINGLE_PLAYER": config("SINGLE_PLAYER", default="0", cast=bool),

            "SIO_HOST": config("SIO_HOST", default="127.0.0.1"),
            "SIO_PORT": config("SIO_PORT", default="4433", cast=int),

            "SSL_CERT": config("SSL_CERT", default="cert.crt"),
            "SSL_KEY": config("SSL_KEY", default="key.key"),
        }

        if not self._config["DEBUG"]:
            # Force debug options to off if debug mode is off
            self._config["SINGLE_PLAYER"] = False

    def __getitem__(self, item):
        return self._config[item]
