"""Интерфейсы конвертера и пользовательского типа для скриптов в assets'ах.

Этот модуль будет копироваться в игровые assets'ы, поэтому он должен содержать
только импорты библиотек питона.
"""

from __future__ import annotations

import abc
import logging
from typing import Dict

logger = logging.getLogger(__name__)


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

    @staticmethod
    @abc.abstractmethod
    def createObjFromDict(dct: Dict) -> IUserType:
        """
        Конвертирует FIXED_DICT в объект, который будет использоваться
        на сервере.
        """

    @staticmethod
    @abc.abstractmethod
    def getDictFromObj(obj: IUserType) -> Dict:
        """Конвертирует объект, используемый на сервере, в FIXED_DICT."""
        logger.debug('')
        return {}

    @staticmethod
    @abc.abstractmethod
    def isSameType(obj: IUserType) -> bool:
        """Проверяет является ли объект пользовательским типом."""
