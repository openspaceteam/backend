import logging

import exceptions
from singletons.client_manager import ClientManager
from singletons.sio import Sio
from utils.general import str_to_bool, str_is_bool


def args(*required_args):
    """
    Decorator that makes checking for required GET/POST
    argument easier.
    The decorator will look for arguments in the right
    dictionary according to the request's method.
    If at least one argument is missing, a
    `exceptions.ApiMissingArgumentsError` is raised.
    You must required arguments to the decorator, like so:
    ```
    @api.errors
    @api.args("arg1", "arg2")
    def handle(request):
        ...
    ```
    -   It's highly recommended to put the `errors` decorator
        **before** the `args` one, because this decorator will
        raise an exceptions if at least one argument is missing,
        and by using the `errors` decorator, the server will
        return a 400 response with a valid JSON body
        rather than returning an Exception.

    :param required_args: required arguments
    :return:
    """
    def decorator(f):
        async def wrapper(sid, data=None, *args, **kwargs):
            missing = []
            for arg in required_args:
                if type(arg) is tuple:
                    if len(arg) == 2:
                        arg_name, arg_type, *checker_args = arg + (None,)
                    else:
                        arg_name, arg_type, *checker_args = arg
                else:
                    arg_name, arg_type, *checker_args = arg, None, None

                checkers = {
                    int: lambda x, *_: type(x) is int or (type(x) is str and x.isnumeric()),
                    str: lambda x, accept_empty: type(x) is str and (len(x.strip()) > 0 or accept_empty),
                    bool: lambda x, *_: type(x) in [str, int, bool] and str_is_bool(str(x)),
                    list: lambda x, *_: type(x) is list,
                    None: lambda x, *_: True
                }

                pre_processors = {
                    int: lambda x: int(x),
                    bool: lambda x: str_to_bool(x)
                }

                if arg_name not in data or not checkers[arg_type](data[arg_name], *checker_args):
                    missing.append(arg_name)

                if arg_type in pre_processors and arg_name in data:
                    data[arg_name] = pre_processors[arg_type](data[arg_name])

            if missing:
                raise exceptions.SocketMissingArgumentsError("Missing argument(s): {}".format(missing))
            return await f(sid, data, *args, **kwargs)
        return wrapper
    return decorator


def errors(f):
    async def wrapper(sid, data=None, *args, **kwargs):
        try:
            await f(sid, data, *args, **kwargs)
        except exceptions.SocketMissingArgumentsError:
            logging.error("{} raised missing arguments".format(sid))
            await Sio().emit('error_missing_arguments', room=sid)
        except exceptions.SocketInvalidArgumentsError:
            logging.error("{} raised invalid arguments".format(sid))
            await Sio().emit('error_invalid_arguments', room=sid)
        except exceptions.SocketUnlinkableClientError:
            logging.error("{} raised unlinkable client".format(sid))
            await Sio().emit('error_unlinkable_client', room=sid)
        except exceptions.SocketNotInGameError:
            logging.error("{} raised not in game".format(sid))
            await Sio().emit('error_not_in_game', room=sid)
        except exceptions.SocketInGameError:
            logging.error("{} raised in game".format(sid))
            await Sio().emit('error_in_game', room=sid)
        except exceptions.SocketIsNotHostError:
            logging.error("{} raised is not host".format(sid))
            await Sio().emit('error_is_not_host', room=sid)
    return wrapper


def link_client(f):
    async def wrapper(sid, data=None, *args, **kwargs):
        try:
            client = ClientManager()[sid]
        except ValueError:
            raise exceptions.SocketUnlinkableClientError()
        return await f(sid, data, client, *args, **kwargs)
    return wrapper


def client_in_game(f):
    async def wrapper(sid, data=None, client=None, *args, **kwargs):
        if client is None or not client.is_in_game:
            raise exceptions.SocketNotInGameError()
        return await f(sid, data, client, *args, **kwargs)
    return wrapper


def client_not_in_game(f):
    async def wrapper(sid, data=None, client=None, *args, **kwargs):
        if client is None or client.is_in_game:
            raise exceptions.SocketInGameError()
        return await f(sid, data, client, *args, **kwargs)
    return wrapper


def client_is_host(f):
    async def wrapper(sid, data=None, client=None, *args, **kwargs):
        if client is None or not client.is_host:
            raise exceptions.SocketIsNotHostError()
        return await f(sid, data, client, *args, **kwargs)
    return wrapper


def client_in_game_in_progress(f):
    async def wrapper(sid, data=None, client=None, *args, **kwargs):
        if client is None or not client.is_in_game or not client.game.playing:
            raise exceptions.SocketNotInGameError()
        return await f(sid, data, client, *args, **kwargs)
    return wrapper


def base(f):
    return errors(f)
