from __future__ import annotations

import socketserver
import threading
import os

from typing import Tuple

from .protocol import (
    parse_line,
    err
)
from .commands import dispatch
from .store import InMemoryStorage


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

class RequestHandler(socketserver.StreamRequestHandler):
    server_version = 'lite_cache/0.1'

    def handle(self) -> None:
        store: InMemoryStorage = self.server.store # type: ignore[attr-defined]
        while True:
            line = self.rfile.readline()
            if not line:
                break
            decoded = line.decode("utf-8", errors="replace").strip("\r\n")
            if not decoded:
                continue
            try:
                decoded = line.decode('utf-8', errors='replace')
                cmd, args = parse_line(decoded)
                if cmd == 'QUIT':
                    self.wfile.write(b"OK\r\n")
                    break
                response = dispatch(cmd, args, store)
            except Exception as e:
                response = err(str(e))
            if response is None:
                response = err("internal error")
            self.wfile.write((response + "\r\n").encode("utf-8"))

def serve(host: str = '0.0.0.0', port: int = 6380) -> Tuple[ThreadedTCPServer, threading.Thread]:
    store = InMemoryStorage()
    srv = ThreadedTCPServer((host, port), RequestHandler)
    srv.store = store # type: ignore[attr-defined]
    t = threading.Thread(target=srv.serve_forever, name='tcp-server', daemon=True)
    t.start()
    return srv, t


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6380))
    srv, _ = serve(port=port)
    print(f'Server listening on port 0.0.0.0{port}')
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print('\nShutting down...')
        srv.shutdown()
        srv.server_close()