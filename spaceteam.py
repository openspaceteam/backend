import logging

from aiohttp import web

from singletons.config import Config
from singletons.sio import Sio
import server

HEADER = """
  __  ___  __   ______ _____ ___  __  __ __  
/' _/| _,\/  \ / _/ __|_   _| __|/  \|  V  | 
`._`.| v_/ /\ | \_| _|  | | | _|| /\ | \_/ | 
|___/|_| |_||_|\__/___| |_| |___|_||_|_| |_| 

"""


def main():
    logging.getLogger("aiohttp").setLevel(logging.CRITICAL)
    logging.getLogger().setLevel(logging.DEBUG if Config()["DEBUG"] else logging.INFO)
    print(HEADER)

    # Create sio and aiohttp server
    app = web.Application()
    Sio().attach(app)

    # Start server
    web.run_app(
        app,
        host=Config()["SIO_HOST"],
        port=Config()["SIO_PORT"]
    )

if __name__ == '__main__':
    main()
