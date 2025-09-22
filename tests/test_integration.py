import socket
import threading
import time


from app.server import serve

def _send_and_recv(host, port, cmd: str) -> str:
    with socket.create_connection((host, port), timeout=3) as s:
        s.sendall((cmd + "\n").encode("utf-8"))
        data = b""
        while not data.endswith(b"\n"):
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
            return data.decode("utf-8").rstrip("\r\n")


def test_e2e_set_get_ttl():
    srv, thread = serve(host="127.0.0.1", port=0)
    port = srv.server_address[1]
    try:
        assert _send_and_recv("127.0.0.1", port, "SET a 1") == "OK"
        assert _send_and_recv("127.0.0.1", port, "GET a") == "1"
        assert _send_and_recv("127.0.0.1", port, "TTL a") == "-1"
        assert _send_and_recv("127.0.0.1", port, "SET t 42 EX 1") == "OK"
        ttl = int(_send_and_recv("127.0.0.1", port, "TTL t"))
        assert ttl in (0, 1)
        time.sleep(1.1)
        assert _send_and_recv("127.0.0.1", port, "GET t") == "(nil)"
    finally:
        srv.shutdown(); srv.server_close()

def test_unknown_command_and_errors():
    srv, thread = serve(host="127.0.0.1", port=0)
    port = srv.server_address[1]
    try:
        assert _send_and_recv("127.0.0.1", port, "FOO") == "-ERR unknown command"
        assert _send_and_recv("127.0.0.1", port, "GET") == "-ERR wrong number of arguments for 'GET'"
        assert _send_and_recv("127.0.0.1", port, "TTL a b") == "-ERR wrong number of arguments for 'TTL'"
        resp = _send_and_recv("127.0.0.1", port, "SET k v with spaces")
        assert resp.startswith("-ERR syntax: SET key value")
    finally:
        srv.shutdown(); srv.server_close()

def test_ex_option_case_insensitive_and_unicode_values():
    srv, thread = serve(host="127.0.0.1", port=0)
    port = srv.server_address[1]
    try:
        assert _send_and_recv("127.0.0.1", port, "SET t 1 ex 1") == "OK"
        r = _send_and_recv("127.0.0.1", port, "SET привет мир")
        assert r == "OK"
        assert _send_and_recv("127.0.0.1", port, "GET привет") == "мир"
    finally:
        srv.shutdown(); srv.server_close()


def test_quit_closes_connection():
    srv, thread = serve(host="127.0.0.1", port=0)
    port = srv.server_address[1]
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=3)
        try:
            s.sendall(b"QUIT\n")
            data = s.recv(1024)
            assert data.startswith(b"OK")
            try:
                s.sendall(b"GET a\n")
                more = s.recv(1024)
                assert not more
            except (ConnectionResetError, BrokenPipeError, socket.timeout):
                pass
        finally:
            s.close()
    finally:
        srv.shutdown()
        srv.server_close()

def test_concurrent_clients():
    srv, thread = serve(host="127.0.0.1", port=0)
    port = srv.server_address[1]
    try:
        def writer():
            for i in range(50):
                _send_and_recv("127.0.0.1", port, f"SET k {i}")

        def reader(results):
            for _ in range(50):
                results.append(_send_and_recv("127.0.0.1", port, "GET k"))

        res = []
        t1 = threading.Thread(target=writer)
        t2 = threading.Thread(target=reader, args=(res,))
        t1.start(); t2.start(); t1.join(); t2.join()
        assert isinstance(res[-1], str)
    finally:
        srv.shutdown(); srv.server_close()