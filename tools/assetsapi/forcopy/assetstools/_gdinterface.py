"""Интерфейс доступа к KBEngine.globalData."""

import abc
import logging
from typing import Any, Optional, Union, Hashable

from . import devonly
from assetsapi.kbeapi.baseapp import KBEngine

logger = logging.getLogger(__name__)


class IGlobalData(abc.ABC):
    """Interface for accessing global data.

    A separate child class for each key. The interface is needed so that you
    can catch places where global data is accessed.

    The engine has callbacks for accessing global data: onGlobalData / onGlobalDataDel.
    But these callbacks are already called by the engine and it is not
    possible to track the access point to global data by means of python by
    their call. To find an access point to global data, you will need to use
    text search by code - this is inconvenient.

    In the case of one access point, it will be enough to put only in one place,
    for example, "import traceback; traceback.print_stack()"; or use other ways
    from Python (tests, inspect.stack(), etc.). In the case of a simple call
    through `KBEngine.globalData`, you will need to perform the same actions
    for all access points to global data using this key.
    """

    @abc.abstractmethod
    def get_key(self) -> Hashable:
        pass

    def get_value(self) -> Optional[Any]:
        logger.debug('[%s]', self)
        return KBEngine.globalData.get(self.get_key())

    def set_value(self, value: Any):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        KBEngine.globalData[self.get_key()] = value

    def del_value(self):
        logger.debug('[%s]', self)
        del KBEngine.globalData[self.get_key()]

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(key="{self.get_key()}")'

    __repr__ = __str__
