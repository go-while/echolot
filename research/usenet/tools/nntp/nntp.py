"""Minimal read-only NNTP client (raw sockets). No POST/IHAVE/AUTHINFO."""
import socket, time, sys

HOST = "archive.usenet.blueworldhosting.com"
PORT = 119
FORBIDDEN = ("POST", "IHAVE", "AUTHINFO", "XGTITLE_POST")


class NNTP:
    def __init__(self, host=HOST, port=PORT, timeout=120):
        self.host, self.port, self.timeout = host, port, timeout
        self.connect()

    def connect(self):
        self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        self.f = self.sock.makefile("rb")
        self.greeting = self._line()
        self.group_name = None

    def _line(self):
        l = self.f.readline()
        if not l:
            raise EOFError("connection closed")
        return l.rstrip(b"\r\n").decode("latin-1")

    def cmd(self, c):
        word = c.split()[0].upper()
        if word in FORBIDDEN:
            raise RuntimeError("forbidden command " + word)
        self.sock.sendall((c + "\r\n").encode("latin-1"))
        return self._line()

    def multi(self):
        out = []
        while True:
            l = self.f.readline()
            if not l:
                raise EOFError("closed during multiline")
            l = l.rstrip(b"\r\n")
            if l == b".":
                break
            if l.startswith(b".."):
                l = l[1:]
            out.append(l)
        return out

    def close(self):
        try:
            self.cmd("QUIT")
        except Exception:
            pass
        self.sock.close()
