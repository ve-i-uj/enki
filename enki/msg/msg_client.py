"""Классы серверов для работы с сообщениями."""

import asyncio
import logging
from asyncio import CancelledError, Future
from enum import Enum

from enki.kbeenum import ComponentType
from enki.misc import devonly
from enki.misc.result import Result
from enki.misc.startable import IStartable
from enki.msg.imsg import (
    IClientMsgSender,
    NoSerializerForComponentError,
)
from enki.msg.message import Message, OptionalMessage
from enki.msg.msg_descr import CompenentMsgSpecs, ComponentMsgSpecById
from enki.msg.msg_serializer import MessageSerializer
from enki.net.addr import Addr
from enki.net.client import TCPClient, UDPClient
from enki.settings import WAITING_FOR_SERVER_TIMEOUT

logger = logging.getLogger(__name__)


# TODO: [burov_alexey@mail.ru 11.07.2025 10:18]
# Они во многом нужны для отладки. Можно и удалить
class AwaitableClientState(Enum):
    """Состояния клиента сообщений."""

    INITIALIZED = "INITIALIZED"
    STARTED = "STARTED"
    ERROR_ON_START = "ERROR_ON_START"
    MSG_SENT = "MSG_SENT"
    WAITING_RESPONSE = "WAITING_RESPONSE"
    RESPONSE_TIMEOUT_ERROR = "RESPONSE_TIMEOUT_ERROR"
    RESPONSE_CANCELED = "CANCELED"
    RESPONSE_RECEIVED = "RESPONSE_RECEIVED"
    RESPONSE_RETURNED = "RESPONSE_RETURNED"
    STOPPED = "STOPPED"
    CLOSED_BY_SERVER = "CLOSED_BY_SERVER"

    @property
    def is_alive(self) -> bool:
        return self in {
            self.STARTED,
            self.MSG_SENT,
            self.WAITING_RESPONSE,
            self.RESPONSE_RECEIVED,
            self.RESPONSE_RETURNED,
        }


class TcpMsgClient(IClientMsgSender, IStartable):
    """TCP-клиент для отправки KBEngine-сообщений."""

    def __init__(
        self,
        addr: Addr,
        resp_msg_spec_by_id: ComponentMsgSpecById,
        comp_msg_specs: CompenentMsgSpecs,
    ) -> None:
        """Конструктор TCP-клиента для отправки KBEngine-сообщений.

        Args:
            addr (AppAddr): адрес компонента, к которому будет подключение
            resp_msg_spec_by_id (ComponentMsgSpecById): спецификации ответных сообщений
            comp_msg_specs (CompenentMsgSpecs): спецификации сообщений
                компонентов-получателей

        """
        self._addr = addr
        # Ответные данные и закрытие соединения будут приходить в колбэки
        self._client = TCPClient(
            addr, self._on_receive_data_cb, self._on_end_receive_data_cb
        )
        self._resp_msg_spec_by_id = resp_msg_spec_by_id
        self._comp_msg_specs = comp_msg_specs

        self._responses: list[Message] = []
        self._waiting_for_resp_future: Future[Message] | None = None
        self._state = AwaitableClientState.INITIALIZED

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

    @property
    def is_alive(self) -> bool:
        """Клиент запущен.

        Returns:
            bool: флаг запущен ли клиент

        """
        return self._state.is_alive

    async def start(self) -> Result:
        """Запустить tcp-клиент для отправки сообщений.

        Returns:
            Result: результат запуска клиента

        """
        res = await self._client.start()
        if res.success:
            self._state = AwaitableClientState.STARTED
        else:
            self._state = AwaitableClientState.ERROR_ON_START

        return res

    def stop(self) -> None:
        """Остановить клиент сообщений."""
        self._client.stop()
        self._state = AwaitableClientState.STOPPED

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

        if self._state != AwaitableClientState.STARTED:
            logger.warning("[%s] The client is not started", self)
            return False

        serializer = self._get_serializer(msg.component)
        data = serializer.serialize(msg)
        success = await self._client.send_data(data)
        if not success:
            logger.warning("[%s] The message was not sent (msg = '%s')", self, msg)
            return False

        logger.debug("[%s] The message was sent (msg = '%s')", self, msg)
        self._state = AwaitableClientState.MSG_SENT
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

        self._state = AwaitableClientState.RESPONSE_RECEIVED

    def _on_end_receive_data_cb(self) -> None:
        self._state = AwaitableClientState.CLOSED_BY_SERVER

    async def waiting_for_response(
        self, timeout: float = WAITING_FOR_SERVER_TIMEOUT
    ) -> OptionalMessage:
        """Ожидать ответа на отправленное сообщение.

        Args:
            timeout (float, optional): время ожидания ответа. Defaults to
                WAITING_FOR_SERVER_TIMEOUT.

        Returns:
            OptionalMessage: или ответное сообщение, если ответ получен и
            получилось сообщение десериализовать, или None, если
            истёк таймаут или ошибка

        """
        logger.debug("[%s] %s ", self, devonly.func_args_values())

        self._state = AwaitableClientState.WAITING_RESPONSE

        if self._responses:
            # Уже пришёл ответ на этот момент
            self._state = AwaitableClientState.RESPONSE_RETURNED
            return self._responses.pop(0)

        self._waiting_for_resp_future = Future()

        try:
            resp_msg = await asyncio.shield(
                asyncio.wait_for(self._waiting_for_resp_future, timeout)
            )
        except TimeoutError:
            self._state = AwaitableClientState.RESPONSE_TIMEOUT_ERROR
            return None

        except CancelledError:
            self._state = AwaitableClientState.RESPONSE_CANCELED
            return None

        self._state = AwaitableClientState.RESPONSE_RETURNED
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
