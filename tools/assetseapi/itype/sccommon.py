"""Интерфейсы ключевых сервеных типов для скриптов в assets'ах."""

from __future__ import annotations

import abc
import logging
from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Optional

from enki.misc import devonly
from enki.core.kbetype import FixedDict, Array, Vector3

logger = logging.getLogger(__name__)


@dataclass
class GDInfoDC:
    """Parent class for the GD info."""
    pass


class IGDAccessor(abc.ABC):
    """Интерфейс класса имеющего доступ к KBEngine.globalData ."""

    GD_KEY: ClassVar[str]

    @abc.abstractmethod
    def get(self, uid: str) -> Optional[GDInfoDC]:
        pass

    @abc.abstractmethod
    def add(self, info_dc: GDInfoDC) -> str:
        """Returns unique identifier."""
        pass

    @abc.abstractmethod
    def remove(self, uid: str) -> bool:
        pass


class IUserType(abc.ABC):
    """Абстрактный класс для пользовательского типа."""


class IConverter(abc.ABC):
    """Интерфейс конвертера для пользовательского типа.

    Конвертер используется для проброса пользовательских объектов
    между процессами *app'ов в виде FIXED_DICT и конвертирования
    этого FIXED_DICT обратно в пользовательский объект.

    Путь до конвертера задаётся в <implementedBy> у FIXED_DICT в types.xml

    Пример (types.xml):

    <root>
        ...
        <MY_TYPE_NAME> FIXED_DICT
            <implementedBy> name_of_module_contained_converter.ConverterClassName </implementedBy>
            <Properties>
                <property_name>
                    <Type> INT8 </Type>
                </property_name>
            </Properties>
        </MY_TYPE_NAME>
        ...
    </root>

    Более подробно см. server_programming_guide.pdf для BW. Глава 5.5
    (Implementing Custom Property Data Types)
    """

    @abc.abstractmethod
    @staticmethod
    def createObjFromDict(fixed_dict: FixedDict) -> IUserType:
        """
        Конвертирует FIXED_DICT в объект, который будет использоваться
        на сервере.
        """

    @abc.abstractmethod
    @staticmethod
    def getDictFromObj(obj: IUserType) -> FixedDict:
        """Конвертирует объект, используемый на сервере, в FIXED_DICT."""
        logger.debug('')
        return {}

    @abc.abstractmethod
    @staticmethod
    def isSameType(obj: IUserType) -> bool:
        """Проверяет является ли объект пользовательским типом."""
