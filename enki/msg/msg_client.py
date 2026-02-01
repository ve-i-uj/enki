"""Классы серверов для работы с сообщениями."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Self, TypeAlias

from enki.misc import devonly
from enki.misc.startable import IStartable
from enki.msg.imsg import (
    IClientMsgSender,
    IMsgClientClosable,
    IMsgResponseAwaitable,
)
from enki.msg.msg_utils import get_serializer
from enki.net.client import (
    ResponseAwaitableTCPClient,
    ResponseAwaitableUDPClient,
)

if TYPE_CHECKING:
    from enki.kbeenum import ComponentType
    from enki.misc.result import Result
    from enki.msg.message import Message
    from enki.msg.msg_descr import (
        MsgDescr,
    )
    from enki.net.addr import Addr

logger = logging.getLogger(__name__)

OnEndReceiveMsgCallback: TypeAlias = Callable[[], None]


class TcpMsgClient(
    IStartable,
    IClientMsgSender,
    IMsgResponseAwaitable,
):
    """TCP-клиент для отправки KBEngine-сообщений."""

    def __init__(
        self,
        addr: Addr,
        resp_comp: ComponentType,
        on_end_receive_msg_cb: OnEndReceiveMsgCallback | None = None,
    ) -> None:
        """Конструктор TCP-клиента для отправки KBEngine-сообщений.

        Args:
            addr (AppAddr): адрес компонента, к которому будет подключение
            resp_comp (ComponentType): компонент, которому придут ответы
            on_end_receive_msg_cb (OnEndReceiveMsgCallback | None, optional):
                колбэк на окончание получения данных от сервера. Defaults to None.

        """
        self._client = ResponseAwaitableTCPClient(
            addr, on_end_receive_data_cb=self.on_end_receive_msg_cb
        )
        self._addr = addr
        self._resp_comp = resp_comp
        self._on_end_receive_msg_cb = on_end_receive_msg_cb

    def on_end_receive_msg_cb(self) -> None:
        """Колбэк на прекращение получения сообщений (tcp соединение закрыто)."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        if self._on_end_receive_msg_cb is not None:
            self._on_end_receive_msg_cb()

    @property
    def is_started(self) -> bool:
        """Клиент запущен.

        Returns:
            bool: флаг запущен ли клиент

        """
        return self._client.is_connected

    async def start(self) -> Result:
        """Запустить tcp-клиент для отправки сообщений.

        Returns:
            Result: результат запуска клиента

        """
        return await self._client.connect()

    def stop(self) -> None:
        """Остановить клиент сообщений."""
        self._client.disconnect()

    async def send_msg(self, msg: Message) -> bool:
        """Отправить сообщение компоненту KBEngine.

        Args:
            msg (Message): сообщение, которое нужно отправить

        Returns:
            bool: успех отправки сообщения

        """
        logger.debug("[%s] %s ", self, devonly.func_args_values())

        serializer = get_serializer(msg.component)
        data = serializer.serialize(msg)

        success = await self._client.send_data(data)
        if not success:
            logger.warning(
                "[%s] The message was not sent (msg = '%s')", self, msg
            )
            return False

        logger.debug("[%s] The message was sent (msg = '%s')", self, msg)
        return True

    async def send_msg_content(self, msg: Message) -> bool:
        """Отправить сообщения без id и длины на компонент, с которого запрос.

        Принимающая сторона сама знает, какое сообщение ждать на конкретном
        адресе.

        Args:
            msg (Message): KBEngine-сообщение, данные которого будут отправлены

        Returns:
            bool: получилось или нет отправить сообщение

        """
        serializer = get_serializer(msg.component)
        data = serializer.serialize(msg, only_data=True)
        success = await self._client.send_data(data)
        if not success:
            logger.warning(
                "[%s] The message was not sent (msg = '%s')", self, msg
            )
            return False

        logger.debug("[%s] The message was sent (msg = '%s')", self, msg)
        return True

    def wait_and_iterate_resp_msgs(self, timeout: float) -> Self:
        """Возвращает итератор с таймаутом ожидания ответа на сообщение.

        Может быть несколько сообщений в ответ или несколько чанков ответов,
        завёрнутых в сообщения (т.к. это клиент слоя сообщений, то и возвращает
        он даже чанки в виде сообщений).

        Args:
            timeout (float, optional): время ожидания ответа

        Returns:
            Self: итератор ответных сообщений

        """
        self._client.wait_and_iterate_responses(timeout)
        return self

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> Message:
        resp_data = await self._client.__anext__()
        serializer = get_serializer(self._resp_comp)
        resp_msg, data_tail = serializer.deserialize(memoryview(resp_data))
        if resp_msg is None:
            logger.warning(
                "The message cannot be deserialized. Reject data (data = %s)",
                resp_data,
            )
            # На выход через проверку остальных ответов
            return await self.__anext__()

        if data_tail:
            logger.warning(
                "[%s] There is another data after deserializing. Handle it again "
                "(data = %s)",
                self,
                data_tail.tobytes(),
            )
            self._client.on_receive_data(data_tail.tobytes())

        return resp_msg

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}({self._addr}, "
            f"resp_comp={self._resp_comp.name})"
        )


class UdpMsgClient(IClientMsgSender, IMsgResponseAwaitable, IMsgClientClosable):
    """UDP-клиент для отправки KBEngine-сообщений."""

    def __init__(
        self,
        addr: Addr,
        resp_comp: ComponentType,
    ) -> None:
        """Конструктор UDP-клиента для отправки KBEngine-сообщений.

        Args:
            addr (AppAddr): адрес компонента, которому будет отправклено
                сообщение
            resp_comp (ComponentType): компонент, которому придут ответы

        """
        self._client = ResponseAwaitableUDPClient(
            addr, broadcast=addr.is_broadcast_ip
        )
        self._addr = addr
        self._resp_comp = resp_comp

    async def send_msg(self, msg: Message) -> bool:
        """Отправить сообщение компоненту KBEngine.

        Args:
            msg (Message): сообщение, которое нужно отправить

        Returns:
            bool: успех отправки сообщения

        """
        logger.debug("[%s] %s ", self, devonly.func_args_values())

        serializer = get_serializer(msg.component)
        data = serializer.serialize(msg)

        success = await self._client.send_data(data)
        if not success:
            logger.warning(
                "[%s] The message was not sent (msg = '%s')", self, msg
            )
            return False

        logger.debug("[%s] The message was sent (msg = '%s')", self, msg)
        return True

    async def send_msg_content(self, msg: Message) -> bool:
        """Отправить сообщения без id и длины на компонент, с которого запрос.

        Принимающая сторона сама знает, какое сообщение ждать на конкретном
        адресе.

        Args:
            msg (Message): KBEngine-сообщение, данные которого будут отправлены

        Returns:
            bool: получилось или нет отправить сообщение

        """
        serializer = get_serializer(msg.component)
        data = serializer.serialize(msg, only_data=True)
        success = await self._client.send_data(data)
        if not success:
            logger.warning(
                "[%s] The message was not sent (msg = '%s')", self, msg
            )
            return False

        logger.debug("[%s] The message was sent (msg = '%s')", self, msg)
        return True

    def wait_and_iterate_resp_msgs(self, timeout: float) -> Self:
        """Возвращает итератор с таймаутом ожидания ответа на сообщение.

        Может быть несколько сообщений в ответ или несколько чанков ответов,
        завёрнутых в сообщения (т.к. это клиент слоя сообщений, то и возвращает
        он даже чанки в виде сообщений).

        Args:
            timeout (float, optional): время ожидания ответа

        Returns:
            Self: итератор ответных сообщений

        """
        self._client.wait_and_iterate_responses(timeout)
        return self

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> Message:
        resp_data = await self._client.__anext__()
        serializer = get_serializer(self._resp_comp)
        resp_msg, data_tail = serializer.deserialize(memoryview(resp_data))
        if resp_msg is None:
            logger.warning(
                "The message cannot be deserialized. Reject data (data = %s)",
                resp_data,
            )
            # На выход через проверку остальных ответов
            return await self.__anext__()

        if data_tail:
            logger.warning(
                "[%s] There is another data after deserializing. Handle it again "
                "(data = %s)",
                self,
                data_tail,
            )
            self._client.on_receive_data(data_tail.tobytes())

        return resp_msg

    def close(self) -> None:
        """Закрыть."""
        self._client.close()


class RawRespTcpMsgClient(
    TcpMsgClient,
    IStartable,
    IClientMsgSender,
    IMsgResponseAwaitable,
):
    """TCP-клиент для отправки KBEngine-сообщений с сырым ответом.

    В ответ на сообщение приходят закодированные значения, а не сериализованное
    сообщение. Клиент декодирует данные и возвращает уже сообщение в ответе.
    """

    def __init__(
        self,
        addr: Addr,
        resp_msg_descr: MsgDescr,
    ) -> None:
        """Конструктор TCP-клиента для отправки KBEngine-сообщений.

        Args:
            addr (AppAddr): адрес компонента, к которому будет подключение
            resp_msg_descr (MsgDescr): сообщение, данные, которого будут в ответе

        """
        super().__init__(addr, resp_msg_descr.component_type)

        self._resp_msg_descr = resp_msg_descr

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> Message:
        resp_data = await self._client.__anext__()
        serializer = get_serializer(self._resp_msg_descr.component_type)
        resp_msg, data_tail = serializer.deserialize_only_data(
            resp_data, self._resp_msg_descr.id
        )
        if resp_msg is None:
            logger.warning(
                "The message '%s' cannot be deserialized. Reject data (data = %s)",
                self._resp_msg_descr.name,
                resp_data,
            )
            # На выход через проверку остальных ответов
            return await self.__anext__()

        if data_tail:
            logger.warning(
                "[%s] There is another data after deserializing. Put data in "
                "the client like new one (data = %s)",
                self,
                data_tail.tobytes(),
            )
            # В TCP пакете может быть несколько KBEngine-сообщений. Если что-то
            # осталось необработанным просто скиним данные, как сново пришедшеи.
            # Надеюсь порядок сообщений не имеет значения ...
            self._client.on_receive_data(data_tail.tobytes())

        return resp_msg

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(addr={self._addr}, "
            f"resp_msg={self._resp_msg_descr.name})"
        )

    __repr__ = __str__


class RawRespUdpMsgClient(
    UdpMsgClient, IClientMsgSender, IMsgResponseAwaitable
):
    """UDP-клиент для отправки KBEngine-сообщений с сырым ответом.

    В ответ на сообщение приходят закодированные значения, а не сериализованное
    сообщение. Клиент декодирует данные и возвращает уже сообщение в ответе.
    """

    def __init__(
        self,
        addr: Addr,
        resp_msg_descr: MsgDescr,
    ) -> None:
        """Конструктор UDP-клиента для отправки KBEngine-сообщений.

        Args:
            addr (AppAddr): адрес компонента, которому будет отправлено сообщение
            resp_msg_descr (MsgDescr): описание сообщения, данные, которого
                будут в ответе

        """
        super().__init__(addr, resp_msg_descr.component_type)
        self._resp_msg_descr = resp_msg_descr

    async def __anext__(self) -> Message:
        resp_data = await self._client.__anext__()

        serializer = get_serializer(self._resp_msg_descr.component_type)
        resp_msg, data_tail = serializer.deserialize_only_data(
            resp_data, self._resp_msg_descr.id
        )
        if resp_msg is None:
            logger.warning(
                "The message %s' cannot be deserialized (data = %s). Reject data",
                self._resp_msg_descr.name,
                resp_data,
            )
            # На выход через проверку остальных ответов
            return await self.__anext__()

        if data_tail:
            # В UDP сырых ответах должно быть одно сообщение в одной датаграмме.
            # Иначе, если сообщение без фиксированной длины, то его не прочитать.
            logger.warning(
                "[%s] There is another data after deserializing. Reject it "
                "(data = %s)",
                self,
                data_tail,
            )

        return resp_msg

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(addr={self._addr}, "
            f"resp_msg={self._resp_msg_descr.name})"
        )

    __repr__ = __str__
