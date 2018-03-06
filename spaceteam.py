import logging
import ssl

import os
from aiohttp import web

from singletons.config import Config
from singletons.sio import Sio
import server
from singletons.words_storage import WordsStorage

HEADER = """
  __  ___  __   ______ _____ ___  __  __ __  
/' _/| _,\/  \ / _/ __|_   _| __|/  \|  V  | 
`._`.| v_/ /\ | \_| _|  | | | _|| /\ | \_/ | 
|___/|_| |_||_|\__/___| |_| |___|_||_|_| |_| 

"""


def main():
    logging.getLogger("aiohttp").setLevel(logging.CRITICAL)
    logging.getLogger().setLevel(logging.DEBUG if Config()["DEBUG"] else logging.INFO)

    # Debug alert
    if Config()["DEBUG"]:
        logging.debug("Running in debug mode")
    if Config()["SINGLE_PLAYER"]:
        logging.debug("Running in single player mode")

    # ASCII art
    print(HEADER)

    # Load words storage
    WordsStorage().load()

    # Create sio and aiohttp server
    app = web.Application()
    Sio().attach(app)

    # Load SSL context
    cert_path = Config()["SSL_CERT"]
    key_path = Config()["SSL_KEY"]
    if cert_path and key_path and os.path.isfile(cert_path) and os.path.isfile(key_path):
        logging.info("Using SSL")
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_context.load_cert_chain(Config()["SSL_CERT"], Config()["SSL_KEY"])
    else:
        logging.warning("SSL is disabled!")
        ssl_context = None

    # Start server
    web.run_app(
        app,
        host=Config()["SIO_HOST"],
        port=Config()["SIO_PORT"],
        ssl_context=ssl_context
    )


if __name__ == '__main__':
    main()
