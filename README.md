# OpenSpaceTeam Backend
OpenSpaceTeam is an open source implementation of a 
[Spaceteam](http://spaceteam.ca/)-like game, playable through the 
browser. This is the backend's code, written in Python using asyncio and socket.io.  
Frontend's code is available [here](https://github.com/openspaceteam/frontend).

## Current status
This project was made for ISIS Di Maggio's educational guidance (the 
italian high school I'm attending at the time of writing this, in 2018), 
so it's aimed at Italian middle school students. That's why the interface is entirely in Italian. If you are Italian and you wish to translate this project, you're welcome to make a fork and a submit pull request.  
The game is mostly working. It may be a bit unbalanced and there are a 
few unimplemented features, but what's been implemented works quite 
well.  
There are few comments and some files need a bit of refactoring.  

## Requirements
- Python 3.6 (doesn't work in <= 3.5 nor 2)
- An SSL certificate (not required but highly recommended)

## Installing
```bash
$ git clone https://github.com/openspaceteam/backend.git
$ cd backend
$ virtualenv -p $(which python3.6) .pyenv
$ source .pyenv/bin/activate
(.pyenv)$ pip install -r requirements.txt

# SSL is optional, but recommended
(.pyenv)$ mv certs/spaceteam.crt cert.crt
(.pyenv)$ mv certs/spaceteam.key key.key


(.pyenv)$ cp settings.sample.ini settings.ini
(.pyenv)$ nano settings.ini
...
(.pyenv)$ python3 spaceteam.py

  __  ___  __   ______ _____ ___  __  __ __
/' _/| _,\/  \ / _/ __|_   _| __|/  \|  V  |
`._`.| v_/ /\ | \_| _|  | | | _|| /\ | \_/ |
|___/|_| |_||_|\__/___| |_| |___|_||_|_| |_|


INFO:root:Using SSL
======== Running on http://0.0.0.0:4433 ========
(Press CTRL+C to quit)
```

## Configuring
The easiest configuration is letting the backend listen on all interfaces (0.0.0.0) and using a SSL certificate by
[Let's Encrypt](https://letsencrypt.org/).
Put the certificate (rename it to `cert.crt`) and the key file (rename it to `key.key`) in backend's folder. You can
specify a different path as well in `settings.ini`.

## License
This project is licensed under the GNU AGPL 3 License.  
See the "LICENSE" file for more information.

