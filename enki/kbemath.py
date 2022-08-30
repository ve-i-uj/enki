import math


def int82angle(angle: int) -> float:
    return math.pi * float(angle) / 128


def angle2int8(angle: float) -> int:
    return int(angle * 128 / math.pi + 0.5)
