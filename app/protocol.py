from __future__ import annotations

from typing import List, Tuple

class ProtocolError(Exception):
    pass

def parse_line(line: str) -> Tuple[str, List[str]]:
    line = line.strip()
    if not line:
        raise ProtocolError("Empty line")
    parts = line.split()
    cmd = parts[0].upper()
    args = parts[1:]
    return cmd, args

def ok() -> str:
    return 'OK'

def err(msg: str) -> str:
    return  f'-ERR {msg}'

def nil() -> str:
    return '(nil)'