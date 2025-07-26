"""Классы серверов для работы с сообщениями."""

from __future__ import annotations

import asyncio
import logging
from asyncio import CancelledError, Future

from enki.kbeenum import ComponentType
from enki.misc import devonly
from enki.misc.result import Result
from enki.misc.startable import IStartable
from enki.msg.imsg import (
    IClientMsgSender,
    NoSerializerForComponentError,
)
from enki.msg.message import Message
from enki.msg.msg_descr import CompenentMsgSpecs, ComponentMsgSpecById, MsgDescr
from enki.msg.msg_serializer import MessageSerializer
from enki.net.addr import Addr
from enki.net.client import TCPClient, UDPClient
from enki.settings import WAITING_FOR_SERVER_TIMEOUT

logger = logging.getLogger(__name__)


class TcpMsgClient(IClientMsgSender, IStartable):
    """TCP-клиент для отправки KBEngine-сообщений."""

    def __init__(
        self,
        addr: Addr,
        req_msg_spec_by_id: ComponentMsgSpecById,
        resp_msg_spec_by_id: ComponentMsgSpecById,
    ) -> None:
        """Конструктор TCP-клиента для отправки KBEngine-сообщений.

        Args:
            addr (AppAddr): адрес компонента, к которому будет подключение
            req_msg_spec_by_id (ComponentMsgSpecById): спецификации отправляемых
                сообщений (описание сообщений компонента-получателя)
            resp_msg_spec_by_id (ComponentMsgSpecById): спецификации ответных сообщений

        """
        self._addr = addr
        # Ответные данные и закрытие соединения будут приходить в колбэки
        self._client = TCPClient(
            addr, self._on_receive_data_cb, self._on_end_receive_data_cb
        )
        self._req_msg_spec_by_id = req_msg_spec_by_id
        self._resp_msg_spec_by_id = resp_msg_spec_by_id

        self._responses: list[Message] = []
        self._waiting_for_resp_future: Future[Message] | None = None

        self._connected = False

    def _get_serializer(self, component: ComponentType) -> MessageSerializer:
        """Возвращает сериализатор сообщения в зависимовсти от типа компонента.

        Args:
            component (ComponentType): тип компонента

        Raises:
            NoSerializerForComponentError: если для нужного компонента нет
                сериализатора

        Returns:
            MessageSerializer: сериализатор сообщений

        """
        if component == self._req_msg_spec_by_id.component:
            return MessageSerializer(self._req_msg_spec_by_id)

        if component == self._resp_msg_spec_by_id.component:
            return MessageSerializer(self._resp_msg_spec_by_id)

        err_msg = f"There is no serializator for the component '{component.name}'"
        logger.error("%s (Logic error)", err_msg)
        raise NoSerializerForComponentError(err_msg)

    @property
    def is_alive(self) -> bool:
        """Клиент запущен.

        Returns:
            bool: флаг запущен ли клиент

        """
        return self._connected

    async def start(self) -> Result:
        """Запустить tcp-клиент для отправки сообщений.

        Returns:
            Result: результат запуска клиента

        """
        res = await self._client.start()
        if res.success:
            self._connected = True

        return res

    def stop(self) -> None:
        """Остановить клиент сообщений."""
        self._client.stop()
        self._connected = False

        self._responses.clear()
        if self._waiting_for_resp_future is not None:
            self._waiting_for_resp_future.cancel()
            self._waiting_for_resp_future = None

    async def send_msg(self, msg: Message) -> bool:
        """Отправить сообщение компоненту KBEngine.

        Args:
            msg (Message): сообщение, которое нужно отправить

        Returns:
            bool: успех отправки сообщения

        """
        logger.debug("[%s] %s ", self, devonly.func_args_values())

        if not self._connected:
            logger.warning("[%s] The client is not started", self)
            return False

        serializer = self._get_serializer(msg.component)
        data = serializer.serialize(msg)
        success = await self._client.send_data(data)
        if not success:
            logger.warning("[%s] The message was not sent (msg = '%s')", self, msg)
            return False

        logger.debug("[%s] The message was sent (msg = '%s')", self, msg)
        return True

    def _on_receive_data_cb(self, data: bytes) -> None:
        """Колбэк на получение данных от серверного подключения.

        Args:
            data (bytes): данные от сервера

        """
        serializer = MessageSerializer(self._resp_msg_spec_by_id)
        while data:
            msg, data = serializer.deserialize(memoryview(data))
            if msg is None:
                logger.warning(
                    "[%s] The message cannot be deserialize (data = '%s')",
                    self,
                    data,
                )
                break

            if (
                self._waiting_for_resp_future is not None
                and not self._waiting_for_resp_future.done()
            ):
                self._waiting_for_resp_future.set_result(msg)
            else:
                self._responses.append(msg)

    def _on_end_receive_data_cb(self) -> None:
        self.stop()

    async def waiting_for_response(
        self, timeout: float = WAITING_FOR_SERVER_TIMEOUT
    ) -> Message | None:
        """Ожидать ответа на отправленное сообщение.

        Args:
            timeout (float, optional): время ожидания ответа. Defaults to
                WAITING_FOR_SERVER_TIMEOUT.

        Returns:
            Message | None: или ответное сообщение, если ответ получен и
            получилось сообщение десериализовать; или None, если
            истёк таймаут или ошибка

        """
        logger.debug("[%s] %s ", self, devonly.func_args_values())

        if self._responses:
            # Уже пришёл ответ на этот момент
            return self._responses.pop(0)

        self._waiting_for_resp_future = Future()

        try:
            resp_msg = await asyncio.shield(
                asyncio.wait_for(self._waiting_for_resp_future, timeout)
            )
        except TimeoutError:
            logger.info(
                "[%s] No response. Stop waiting by timeout (timeout = %s)",
                self,
                timeout,
            )
            return None

        except CancelledError:
            logger.info(
                "[%s] No response. Waiting was canceled",
                self,
            )
            return None

        logger.debug("[%s] The response message got", self)
        return resp_msg


class UdpMsgClient(IClientMsgSender):
    """UDP-клиент для отправки KBEngine-сообщений."""

    def __init__(
        self,
        addr: Addr,
        comp_msg_specs: CompenentMsgSpecs,
        *,
        broadcast: bool = False,
    ) -> None:
        """Конструктор UDP-клиента для отправки KBEngine-сообщений.

        Args:
            addr (AppAddr): адрес компонента, которому будет отправклено
                сообщение
            comp_msg_specs (CompenentMsgSpecs): спецификации сообщений
                компонентов-получателей
            broadcast (bool, optional): udp на бродкаст. Defaults to False.

        """
        self._addr = addr
        # Ответные данные и закрытие соединения будут приходить в колбэки
        self._client = UDPClient(addr, broadcast=broadcast)
        self._comp_msg_specs = comp_msg_specs

    def _get_serializer(self, component: ComponentType) -> MessageSerializer:
        """Возвращает сериализатор сообщения в зависимовсти от типа компонента.

        Args:
            component (ComponentType): тип компонента

        Raises:
            NoSerializerForComponentError: если для нужного компонента нет
                сериализатора

        Returns:
            MessageSerializer: сериализатор сообщений

        """
        if component not in self._comp_msg_specs:
            err_msg = f"There is no serializator for the component '{component.name}'"
            logger.error("%s (Logic error)", err_msg)
            raise NoSerializerForComponentError(err_msg)

        comp_msg_spec = self._comp_msg_specs[component]
        return MessageSerializer(comp_msg_spec)

    async def send_msg(self, msg: Message) -> bool:
        """Отправить сообщение компоненту KBEngine.

        Args:
            msg (Message): сообщение, которое нужно отправить

        Returns:
            bool: успех отправки сообщения

        """
        logger.debug("[%s] %s ", self, devonly.func_args_values())

        serializer = self._get_serializer(msg.component)
        data = serializer.serialize(msg)

        success = await self._client.send_data(data)
        if not success:
            logger.warning("[%s] The message was not sent (msg = '%s')", self, msg)
            return False

        logger.debug("[%s] The message was sent (msg = '%s')", self, msg)
        return True


class StreamRespTcpMsgClient(IClientMsgSender, IStartable):
    """TCP-клиент для отправки KBEngine-сообщений с сырым ответом.

    В ответ на сообщение приходят закодированные значения, а не сериализованное
    сообщение.
    """

    def __init__(
        self,
        addr: Addr,
        resp_msg: MsgDescr,
        req_msg_spec_by_id: ComponentMsgSpecById,
        resp_msg_spec_by_id: ComponentMsgSpecById,
    ) -> None:
        """Конструктор TCP-клиента для отправки KBEngine-сообщений.

        Args:
            addr (AppAddr): адрес компонента, к которому будет подключение
            resp_msg (MsgDescr): сообщение, данные, которого будут в ответе
            req_msg_spec_by_id (ComponentMsgSpecById): спецификации отправляемых
                сообщений (описание сообщений компонента-получателя)
            resp_msg_spec_by_id (ComponentMsgSpecById): спецификации ответных сообщений

        """
        self._addr = addr
        self._resp_msg_descr = resp_msg
        self._req_msg_spec_by_id = req_msg_spec_by_id
        self._resp_msg_spec_by_id = resp_msg_spec_by_id

        self._future: Future[bytes | None] | None = None

        self._client = TCPClient(
            addr, self._on_receive_data_cb, self._on_end_receive_data_cb
        )
        self._connected = False

    def _on_receive_data_cb(self, data: bytes) -> None:
        """Колбэк на получение данных от серверного подключения.

        Args:
            data (bytes): данные от сервера

        """
        if self._future is not None and not self._future.done():
            self._future.set_result(data)
        else:
            logger.warning("Unexpected data received (data = %s)", data.decode())

    def _on_end_receive_data_cb(self) -> None:
        """Колбэк окончания передачи данных от транспортной библиотеки."""
        if self._future is not None and not self._future.done():
            self._future.set_result(None)

        self.stop()

    def _get_serializer(self, component: ComponentType) -> MessageSerializer:
        """Возвращает сериализатор сообщения в зависимовсти от типа компонента.

        Args:
            component (ComponentType): тип компонента

        Raises:
            NoSerializerForComponentError: если для нужного компонента нет
                сериализатора

        Returns:
            MessageSerializer: сериализатор сообщений

        """
        if component == self._req_msg_spec_by_id.component:
            return MessageSerializer(self._req_msg_spec_by_id)

        if component == self._resp_msg_spec_by_id.component:
            return MessageSerializer(self._resp_msg_spec_by_id)

        err_msg = f"There is no serializator for the component '{component.name}'"
        logger.error("%s (Logic error)", err_msg)
        raise NoSerializerForComponentError(err_msg)

    async def send_msg(self, msg: Message) -> bool:
        """Отправить сообщение компоненту KBEngine.

        Args:
            msg (Message): отправляемое сообщение

        Returns:
            bool: флаг получилось отправить или нет сообщение

        """
        logger.debug("[%s] %s ", self, devonly.func_args_values())

        if not self._connected:
            logger.warning("[%s] The client is not started", self)
            return False

        serializer = self._get_serializer(msg.component)
        data = serializer.serialize(msg)

        success = await self._client.send_data(data)
        if not success:
            logger.warning("[%s] The message was not sent (msg = '%s')", self, msg)
            return False

        logger.debug("[%s] The message was sent (msg = '%s')", self, msg)
        return True

    @property
    def is_alive(self) -> bool:
        """Флаг запущен ли экземпляр класса.

        Returns:
            bool: флаг запущен ли экземпляр класса

        """
        return self._connected

    async def start(self) -> Result:
        """Запустить объект.

        Returns:
            Result: результат запуска объекта

        """
        res = await self._client.start()
        if res.success:
            self._connected = True
        return res

    def stop(self) -> None:
        """Остановить объект."""
        if not self._connected:
            logger.debug("[%s] The client has already stopped", self)
            return

        logger.debug("[%s] Stopping the client...", self)
        self._client.stop()
        self._connected = False

        if self._future is not None and not self._future.done():
            self._future.set_result(None)
        self._future = None
        logger.debug("[%s] The client stopped", self)

    async def waiting_for_response(
        self, timeout: float = WAITING_FOR_SERVER_TIMEOUT
    ) -> Message | None:
        """Ожидать ответа на отправленное сообщение.

        Args:
            timeout (float, optional): время ожидания ответа. Defaults to
                WAITING_FOR_SERVER_TIMEOUT.

        Returns:
            bytes | None: или сырые данные ответа, если ответ получен;
            или None, если истёк таймаут или ошибка

        """
        logger.debug("[%s] %s ", self, devonly.func_args_values())

        self._future = Future()

        try:
            resp_data = await asyncio.shield(asyncio.wait_for(self._future, timeout))
        except TimeoutError:
            logger.info(
                "[%s] No response. Stop waiting by timeout (timeout = %s)",
                self,
                timeout,
            )
            return None
        except CancelledError:
            logger.info(
                "[%s] No response. Waiting was canceled",
                self,
            )
            return None

        if resp_data is None:
            logger.info("Connection unexpectedly closed")
            return None

        serializer = self._get_serializer(self._resp_msg_spec_by_id.component)
        resp_msg, data_tail = serializer.deserialize_only_data(
            resp_data, self._resp_msg_descr.id
        )
        if resp_msg is None:
            logger.warning(
                "The message %s' cannot be deserialized (data = %s)",
                self._resp_msg_descr.name,
                resp_data,
            )
            return None

        if data_tail:
            logger.warning(
                "Too many data for deserializing the message '%s' (data_tail = %s)",
                self._resp_msg_descr.name,
                data_tail,
            )
            return None

        logger.debug("[%s] The response data got (msg = '%s')", self, resp_msg)
        return resp_msg

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(addr={self._addr}, "
            f"resp_msg={self._resp_msg_descr.name})"
        )

    __repr__ = __str__
