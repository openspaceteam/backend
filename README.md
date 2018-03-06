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
- nginx (not required but highly recommended)  

## Installing
```
$ git clone https://github.com/openspaceteam/backend.git
$ cd backend
$ virtualenv -p $(which python3.6) .pyenv
$ source .pyenv/bin/activate
(.pyenv)$ pip install -r requirements.txt
(.pyenv)$ cp settings.sample.ini settings.ini
(.pyenv)$ nano settings.ini
...
(.pyenv)$ python3 server.py

  __  ___  __   ______ _____ ___  __  __ __
/' _/| _,\/  \ / _/ __|_   _| __|/  \|  V  |
`._`.| v_/ /\ | \_| _|  | | | _|| /\ | \_/ |
|___/|_| |_||_|\__/___| |_| |___|_||_|_| |_|


======== Running on http://127.0.0.1:4433 ========
(Press CTRL+C to quit)
```

## Configuring nginx
We highly recommend using nginx as a reverse proxy with the backend. We 
also recommend using Web Socket Secure (wss) rather than a normal Web 
Socket (ws), so you'll need an SSL certificate. You can get one quite easilly with [Let's Encrypt](https://letsencrypt.org/). [Cloudflare should work as well.](https://support.cloudflare.com/hc/en-us/articles/200169466-Can-I-use-Cloudflare-with-WebSockets-)  
[There's a sample nginx config in nginx.conf.](https://github.com/openspaceteam/backend/blob/master/nginx.conf)

## License
This project is licensed under the GNU AGPL 3 License.  
See the "LICENSE" file for more information.

