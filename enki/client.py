"""Client of a KBEngine server."""

from __future__ import annotations
import abc
import asyncio
import logging
from typing import Union, List, Dict, Awaitable

from enki import settings, serializer, connection, message
from enki.misc import devonly

logger = logging.getLogger(__name__)


class IClient(abc.ABC):

    @abc.abstractmethod
    def on_receive_data(self, data):
        pass

    @abc.abstractmethod
    def send(self, msg: message.IMessage):
        pass

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def fire(self, msg_name, values):
        pass


async def _waiting_for_future(future: Awaitable, timeout: int,
                              msg_ids: List[int]) -> Awaitable:
    """Wrap a coroutine with timeout."""
    try:
        res = await asyncio.wait_for(future, timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f'No response for messages {", ".join(str(i) for i in msg_ids)}')
        return None
    return res


class ICommunicationProtocol(abc.ABC):

    @abc.abstractmethod
    def login(self, account_name: str, password: str):
        pass

    @abc.abstractmethod
    def on_receive_msg(self, msg: message.IMessage):
        pass

    @abc.abstractmethod
    async def _waiting_for(self, msg_id_or_ids: Union[int, List[int]],
                           timeout: int):
        pass


class CommunicationProtocol(ICommunicationProtocol):

    def __init__(self, client: Client):
        self._client = client
        self._waiting_futures = {}  # type: Dict[id, asyncio.Future]

    def on_receive_msg(self, msg):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
        future = self._waiting_futures.pop(msg.id, None)
        if future is not None:
            future.set_result(msg)

    def _waiting_for(self, msg_id_or_ids: Union[int, List[int]],
                     timeout: int) -> asyncio.Future:
        msg_id = msg_id_or_ids
        future = asyncio.get_event_loop().create_future()
        self._waiting_futures[msg_id] = future
        return _waiting_for_future(future, timeout, [msg_id])

    async def login(self, account_name, password) -> bool:
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
        hello_msg = message.Message(
            spec=message.spec.app.loginapp.hello,
            fields=('2.5.10', '0.1.0', b'')
        )
        await self._client.send(hello_msg)
        resp_msg = await self._waiting_for(
            msg_id_or_ids=message.spec.app.client.onHelloCB.id,
            timeout=2
        )
        if resp_msg is None:
            return
        # TODO: [07.12.2020 1:08 a.burov@mednote.life]
        # Обработка случая, когда пришло другое сообщение
        login_msg = message.Message(
            spec=message.spec.app.loginapp.login,
            fields=(0, b'', account_name, password, '96C93073CCCBB4F8362D769C8629CCCC')
        )
        await self._client.send(login_msg)
        resp_msg = await self._waiting_for(
            message.spec.app.client.onLoginSuccessfully.id, 5
        )
        # TODO: [06.12.2020 22:32 a.burov@mednote.life]
        # Достаём адрес BaseApp и подключаемся к нему (это тоже считается частью
        # логина)
        print()


class Client(IClient):

    def __init__(self, loginapp_addr: settings.AppAddr):
        # TODO: [06.12.2020 21:40 a.burov@mednote.life]
        # Возможно подключение к LoginApp нужно закрывать после получения адреса
        # BaseApp (нужно посмотреть, возможно оно само закрывается)
        self._login_app_conn = connection.AppConnection(
            host=loginapp_addr.host,
            port=loginapp_addr.port,
            client_app=self
        )
        self._serializer = serializer.Serializer()
        self._protocol = CommunicationProtocol(client=self)

    def on_receive_data(self, data):
        """Handle incoming data from a server."""
        msg = self._serializer.deserialize(data)
        logger.debug('[%s] Received a message (%s)', self, devonly.func_args_values())
        logger.debug('[%s] Message "%s" fields: %s', self, msg.name, msg.get_values())
        self._protocol.on_receive_msg(msg)

    async def send(self, msg: message.Message):
        data = self._serializer.serialize(msg)
        await self._login_app_conn.send(data)

    async def start(self):
        await self._login_app_conn.connect()

    def stop(self):
        self._login_app_conn.close()

    async def fire(self, msg_name, *values):
        method = getattr(self._protocol, msg_name)
        await method(*values)
