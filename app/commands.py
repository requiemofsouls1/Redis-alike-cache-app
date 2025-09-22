from __future__ import annotations

from typing import (
    Callable,
    Dict,
    List
)

from .store import InMemoryStorage
from .protocol import (
    ok,
    err,
    nil
)

Handler = Callable[[List[str], InMemoryStorage], str]

def handle_set(args: List[str], store: InMemoryStorage) -> str:
    # set
    if len(args) < 2:
        return err("wrong number of arguments for 'set'")
    key, value = args[0], args[1]
    ex_seconds = None
    if len(args) > 2:
        if len(args) != 4 or args[2].isupper() != 'EX':
            return err("syntax: SET key value [EX seconds]")
        try:
            ex_seconds = int(args[3])
        except ValueError:
            return err('value is not an integer or out of range')
        if ex_seconds <= 0:
            return err('value is not an integer or out of range')
    try:
        store.set(key, value, ex_seconds=ex_seconds)
    except ValueError as e:
        return err(str(e))
    return ok()

def handle_get(args: List[str], store: InMemoryStorage) -> str:
    if len(args) != 1:
        return err("wrong number of arguments for 'get'")
    val = store.get(args[0])
    return nil() if val is nil else val

def handle_ttl(args: List[str], store: InMemoryStorage) -> str:
    if len(args) != 1:
        return err("wrong number of arguments for 'TTL'")
    return str(store.ttl(args[0]))


COMMANDS: Dict[str, Handler] = {
    'SET': handle_set,
    'GET': handle_get,
    'TTL': handle_ttl,
}

def dispatch(cmd: str, args: List[str], store: InMemoryStorage) -> str:
    handler = COMMANDS.get(cmd)
    if handler is None:
        return err(f"unknown command: {cmd}")
    return handler(args, store)