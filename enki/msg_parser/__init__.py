"""Парсеры KBEngine-сообщений в данные для использования в логике."""

from types import ModuleType

from enki.kbeenum import ComponentType
from enki.msg.msg_descr import MsgDescr

from . import (
    baseapp_msg_parser,
    baseappmgr_msg_parser,
    cellapp_msg_parser,
    cellappmgr_msg_parser,
    client_msg_parser,
    dbmgr_msg_parser,
    interfaces_msg_parser,
    logger_msg_parser,
    loginapp_msg_parser,
    machine_msg_parser,
    supervisor_msg_parser,
)
from .imsg_parser import IMsgParser

_MSG_PARSER_MODULE: dict[ComponentType, ModuleType] = {
    ComponentType.BASEAPP: baseapp_msg_parser,
    ComponentType.BASEAPPMGR: baseappmgr_msg_parser,
    ComponentType.CELLAPP: cellapp_msg_parser,
    ComponentType.CELLAPPMGR: cellappmgr_msg_parser,
    ComponentType.DBMGR: dbmgr_msg_parser,
    ComponentType.INTERFACES: interfaces_msg_parser,
    ComponentType.LOGGER: logger_msg_parser,
    ComponentType.LOGINAPP: loginapp_msg_parser,
    ComponentType.MACHINE: machine_msg_parser,
    ComponentType.SUPERVISOR: supervisor_msg_parser,
    ComponentType.CLIENT: client_msg_parser,
}


def get_msg_parser(
    comp_type: ComponentType, msg_descr: MsgDescr
) -> type[IMsgParser]:
    """Получить парсер сообщения для указанного типа компонента.

    Args:
        comp_type: Тип компонента KBEngine.
        msg_descr: Описание сообщения.

    Returns:
        Реализация интерфейса IMsgParser для конкретного типа сообщения.

    Raises:
        AttributeError: Если парсер для указанного сообщения не найден в модуле.

    """
    parsers_module = _MSG_PARSER_MODULE[comp_type]
    parser_name = (
        msg_descr.short_name[0].upper() + msg_descr.short_name[1:] + "MsgParser"
    )
    parser: type[IMsgParser] = getattr(parsers_module, parser_name)

    return parser
