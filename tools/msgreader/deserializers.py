"""Десериализаторы KBEngine-сообщений."""

from __future__ import annotations

import logging
import struct
from dataclasses import dataclass
from typing import TYPE_CHECKING

from enki import msgspec
from enki.kbeenum import ComponentType
from enki.kbetype.decoders.custom_decoders import MESSAGE_ID
from enki.misc.result import Result
from enki.msg.msg_serializer import MessageSerializer

if TYPE_CHECKING:
    from enki.msg.message import Message
    from enki.msg.msg_descr import MsgId

logger = logging.getLogger(__name__)


def deserialize_msg_without_id_and_len(
    data,
    no_envelop_msg_name: str,
) -> DeserializeMsgResult:
    """Обработать чанк байтов, где сообщение без MsgId и MsgLen.

    Args:
        data (memoryview): байты с сериализованным сообщением
        no_envelop_msg_name (str | None): имя сообщения, если данные
            не содержат MsgId и MsgLen

    """
    msg_split_name = no_envelop_msg_name.split("::", 1)
    if len(msg_split_name) != 2:
        text = (f'Invalid message name (msg_name = "{no_envelop_msg_name}")')
        logger.debug(text)
        return DeserializeMsgResult(success=False,
                                    result=DeserializeMsgResultData(None, data), text=text)

    component_name, _msg_name = msg_split_name

    component_name = component_name.lower()
    try:
        comp_type = ComponentType.__members__[component_name.upper()]
    except KeyError:
        text = f"Invalid component name (component_name = {component_name})"
        logger.debug(text)
        return DeserializeMsgResult(success=False, result=DeserializeMsgResultData(None, data), text=text)

    comp_msg_spec = msgspec.MSG_COMP_SPEC_BY_COMPONENT[comp_type]

    serializer = MessageSerializer(comp_msg_spec)

    msg_spec_by_name = {
        sp.name: sp for sp in comp_msg_spec.msg_spec_by_id.values()
    }
    msg_spec = msg_spec_by_name.get(no_envelop_msg_name)
    if msg_spec is None:
        text = f'The message specification is not found (msg_name = "{no_envelop_msg_name}")'
        logger.debug(text)
        return DeserializeMsgResult(success=False, result=DeserializeMsgResultData(None, data), text=text)

    msg, data_tail = serializer.deserialize_only_data(data, msg_spec.id)
    if msg is None:
        text = f'Cannot parse data of the "{no_envelop_msg_name}" message'
        logger.debug(text)
        return DeserializeMsgResult(success=False, result=DeserializeMsgResultData(None, data), text=text)

    return DeserializeMsgResult(success=True, result=DeserializeMsgResultData(msg, data_tail.tobytes()))


@dataclass(frozen=True)
class DeserializeMsgIdResultData:
    """Данные результата получений id сериализованного сообщения."""

    msg_id: MsgId | None
    data_tail: bytes



@dataclass(frozen=True)
class DeserializeMsgIdResult(Result):
    """Результат получить id сериализованного сообщения."""

    success: bool
    result: DeserializeMsgIdResultData
    text: str = ""


def deserialize_msg_id(data: bytes) -> DeserializeMsgIdResult:
    """Получить из данных id сообщения."""
    try:
        decoded_msg_id, offset = MESSAGE_ID.decode(memoryview(data))
    except ValueError as err:
        text = f"The message id cannot be read. Reason: {err}"
        logger.debug(text)
        return DeserializeMsgIdResult(success=False, result=DeserializeMsgIdResultData(None, data), text=text)

    data_tail = data[offset:]

    logger.debug('The message id is "%s"', decoded_msg_id)
    return DeserializeMsgIdResult(success=True, result=DeserializeMsgIdResultData(decoded_msg_id, data_tail))


@dataclass(frozen=True)
class DeserializeMsgResultData:
    """Данные после обработки сериализованного сообщения."""

    # объект сообщения при удачно
    # десериализации или None и хвост с необработанными данными
    msg: Message | None
    data_tail: bytes


@dataclass(frozen=True)
class DeserializeMsgResult(Result):
    """Результат обработки сериализованного сообщения."""

    success: bool
    result: DeserializeMsgResultData
    text: str = ""


def deserialize_msg(
    data: bytes,
    comp_type: ComponentType,
) -> DeserializeMsgResult:
    """Обработать чанк байтов, содержащий сериалзиванное KBEngine-сообщение.

    Args:
        data (bytes): байты с сериализованным сообщением
        comp_type (ComponentType): тип компонента владельца сообщения

    Returns:
        DeserializeMsgResult:

    """
    decoded_msg_id, _offset = MESSAGE_ID.decode(memoryview(data))
    logger.debug('The message id is "%s"', decoded_msg_id)

    comp_msg_spec = msgspec.MSG_COMP_SPEC_BY_COMPONENT[comp_type]
    message_descr = comp_msg_spec.msg_spec_by_id.get(decoded_msg_id)
    if message_descr is None:
        text = (
            f"There is no info about the message id '{decoded_msg_id}' for the component '{comp_type.name}'"
        )
        logger.debug(text)
        return DeserializeMsgResult(success=False, result=DeserializeMsgResultData(None, data), text=text)

    logger.debug('The message name is "%s"', message_descr.name)

    serializer = MessageSerializer(comp_msg_spec)

    try:
        msg, data_tail = serializer.deserialize(memoryview(data))
    except (KeyError, struct.error) as err:
        text = (
            f'The data cannot be decoded (msg_id = "{message_descr.id}", err = "{err}")'
        )
        return DeserializeMsgResult(success=False, result=DeserializeMsgResultData(None, data), text=text)

    if msg is None:
        text = ("The data cannot be parsed to the message")
        return DeserializeMsgResult(success=False, result=DeserializeMsgResultData(None, data), text=text)

    logger.debug("The message has been deserialied (msg = %s)", msg)
    return DeserializeMsgResult(success=True, result=DeserializeMsgResultData(msg, data_tail.tobytes()))
