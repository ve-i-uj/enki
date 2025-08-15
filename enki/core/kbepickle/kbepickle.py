"""Десериализатор python-объектов, закодированных KBEngine."""

import pickle
import sys
from pathlib import Path
from typing import Any


def pickle_global_data_value(data: bytes) -> Any:  # noqa: ANN401
    """Десериализовать закодированные KBEngine pickle данные.

    Для десериализации нужен модуль _upf.
    """
    try:
        value = pickle.loads(data)  # noqa: S301
    except ModuleNotFoundError as err:
        if str(err) == "No module named '_upf'":
            sys.path.append(str(Path(__file__).parent))
            value = pickle.loads(data)  # noqa: S301
            sys.path.pop()
        else:
            raise

    return value
