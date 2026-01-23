"""Обработчик сообщений компонента Supervisor (расширение Machine)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import ClassVar

from enki import msgspec
from enki.kbeenum import (
    COMPONENT_STATE_BY_SHUTDOWN_STATE,
    ComponentState,
    ComponentType,
    ShutdownState,
)
from enki.kbetype.decoders.custom_decoders import (
    KBEComponentId,
    KBEComponentType,
    KBEShutdownState,
)
from enki.kbetype.pytypes.basic_data_types import KBEUInt64
from enki.misc import devonly
from enki.msg.message import Message  # noqa: TC001
from enki.msg_parser.imsg_parser import (
    IMsgParser,
    MsgParserResult,
    ParsedMsgData,
)

# Supervisor - это расширение компонента Machine. В этом модуле только новые
# сообщения относительно Machine
from .machine_msg_parser import *  # type: ignore


logger = logging.getLogger(__name__)


@dataclass
class OnStopComponentParsedMsgData(ParsedMsgData):
    """Распарсенные данные соощения Supervisor::OnStopComponent."""

    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name


@dataclass(frozen=True)
class OnStopComponentMsgParserResult(MsgParserResult):
    """Результат парсинга сообщения Supervisor::OnStopComponent."""

    success: bool
    result: OnStopComponentParsedMsgData
    msg_id: int = msgspec.supervisor.onStopComponent.id
    text: str = ""


class OnStopComponentMsgParser(IMsgParser):
    """Парсер для Supervisor::OnStopComponent."""

    def parse(self, msg: Message) -> OnStopComponentMsgParserResult:
        """Распарсить сообщение Supervisor::OnStopComponent.

        Args:
            msg (Message): KBEngine-сообщение

        Raises:
            TypeError: the message has an invalid value

        Returns:
            OnStopComponentMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        component_id = msg.get_values()[0]
        # ComponentId — это алиас для KBEUInt64
        if not isinstance(component_id, KBEUInt64):
            err_text = (
                f"The message has an invalid value. Expected "
                f"ComponentId (KBEUInt64), got {type(component_id)}"
            )
            raise TypeError(err_text)

        pd = OnStopComponentParsedMsgData(component_id)
        return OnStopComponentMsgParserResult(success=True, result=pd)


@dataclass
class OnLookAppParsedMsgData(ParsedMsgData):
    """Распарсенные данные сообщения Supervisor::onLookApp."""

    componentType: (
        KBEComponentType  # noqa: N815  # pylint: disable=invalid-name
    )
    componentID: KBEComponentId  # noqa: N815  # pylint: disable=invalid-name
    shutdownState: (
        KBEShutdownState  # noqa: N815  # pylint: disable=invalid-name
    )

    @property
    def component_id(self) -> KBEComponentId:
        """Id компонента ("--cid" в строке запуска компонента).

        Returns:
            KBEComponentId: id компонента

        """
        return self.componentID

    @property
    def component_type(self) -> ComponentType:
        """Энам типа компонента.

        Returns:
            ComponentType: энам типа компонента

        """
        return ComponentType(self.componentType)

    @property
    def component_state(self) -> ComponentState:
        """Энам состояния компонента.

        Returns:
            ComponentState: энам состояния компонента

        """
        shutdown_state = ShutdownState(self.shutdownState)
        return ComponentState(COMPONENT_STATE_BY_SHUTDOWN_STATE[shutdown_state])

    __add_to_dict__: ClassVar = ("component_type", "component_state")


@dataclass(frozen=True)
class OnLookAppMsgParserResult(MsgParserResult):
    """Результат парсинга сообщения ::onLookApp."""

    success: bool
    result: OnLookAppParsedMsgData
    msg_id: int = msgspec.machine.onLookApp.id
    text: str = ""


class OnLookAppMsgParser(IMsgParser):
    """Парсер для ::onLookApp."""

    def parse(self, msg: Message) -> OnLookAppMsgParserResult:
        """Распарсить сообщение =::onLookApp.

        Args:
            msg (Message): KBEngine-сообщение

        Raises:
            TypeError: the message has an invalid value

        Returns:
            OnStopComponentMsgParserResult: объект результата обработки

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        assert msg.id == msgspec.machine.onLookApp.id

        component_type, component_id, shutdown_state = msg.get_values()

        if not isinstance(component_type, KBEComponentType):
            err_text = (
                f"The message has an invalid value. Expected "
                f"ComponentId (KBEComponentType), got {type(component_id)}"
            )
            raise TypeError(err_text)

        if not isinstance(component_id, KBEComponentId):
            err_text = (
                f"The message has an invalid value. Expected "
                f"ComponentId (KBEComponentId), got {type(component_id)}"
            )
            raise TypeError(err_text)

        if not isinstance(shutdown_state, KBEShutdownState):
            err_text = (
                f"The message has an invalid value. Expected "
                f"ComponentId (KBEShutdownState), got {type(component_id)}"
            )
            raise TypeError(err_text)

        pd = OnLookAppParsedMsgData(
            component_type, component_id, shutdown_state
        )
        logger.debug(
            "[%s] The message '%s' parsed. Result = %s",
            self,
            msgspec.machine.onLookApp.name,
            pd,
        )

        return OnLookAppMsgParserResult(success=True, result=pd)
