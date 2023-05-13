import math
import socket
import struct


def int82angle(angle: int) -> float:
    return math.pi * float(angle) / 128


def angle2int8(angle: float) -> int:
    return int(angle * 128 / math.pi + 0.5)


def ip2int(addr):
    return struct.unpack("I", socket.inet_aton(addr))[0]


def int2ip(addr):
    return socket.inet_ntoa(struct.pack("I", addr))


def int2port(uint16_port: int) -> int:
    return socket.htons(uint16_port)
