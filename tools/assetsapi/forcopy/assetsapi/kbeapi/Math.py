from typing import Type

from . import _math

# Подсказываем анализатору типов (Pylance, например), какое API у этих типов
Vector2 = _math.Vector2
Vector3 = _math.Vector3
Vector4 = _math.Vector4
try:
    # Это импортируется реализация этих типов из движка, если код запускается
    # движком.
    from Math import Vector2, Vector3, Vector4  # type: ignore
except ImportError:
    # В глобальном пространстве имён нет модуля Math, значит это IDE.
    # Оставляем свою реализация с тем же интерфейсом, что и у движка.
    pass
