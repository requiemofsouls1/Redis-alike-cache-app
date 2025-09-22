import socket
import sys


def send_command(host: str, port: int, command: str) -> str:
    with socket.create_connection((host, port), timeout=5) as s:
        s.sendall((command.strip() + '\r\n').encode('utf-8'))
        data = b''
        while not data.endswith(b'\r\n'):
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
        return data.decode('utf-8').rstrip('\r\n')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: client.py <host> <port> <COMMAND...>')
        sys.exit(2)
    host = sys.argv[1]
    port = int(sys.argv[2])
    command = ''.join(sys.argv[3:])
    print(send_command(host, port, command))