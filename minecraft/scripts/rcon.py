#!/usr/bin/env python3
"""Tiny Source-RCON CLI helper: rcon.py <host> <port> <password> <command>"""
import socket, struct, sys
host, port, pw, cmd = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
s = socket.create_connection((host, port), timeout=30)
_id = 0
def send(t, body):
    global _id; _id += 1; rid = _id
    d = struct.pack('<ii', rid, t) + body.encode() + b'\x00\x00'
    s.sendall(struct.pack('<i', len(d)) + d)
    buf = b''
    while True:
        while len(buf) < 4:
            buf += s.recv(4096)
        ln = struct.unpack('<i', buf[:4])[0]
        while len(buf) < 4 + ln:
            buf += s.recv(4096)
        pid = struct.unpack('<i', buf[4:8])[0]
        out = buf[12:4 + ln - 2].decode('utf8', 'replace'); buf = buf[4 + ln:]
        if pid == rid:
            return out
send(3, pw)
print(send(2, cmd))
