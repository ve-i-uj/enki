"""Client of a KBEngine server."""

from __future__ import annotations
import abc
import asyncio
import logging
from typing import Union, List, Dict, Awaitable, Any

from enki import settings, serializer, connection
from enki.spec import message
from enki.misc import devonly

logger = logging.getLogger(__name__)


class IClient(abc.ABC):

    @abc.abstractmethod
    def on_receive_data(self, data):
        pass

    @abc.abstractmethod
    def send(self, msg: message.IMessage):
        """Send a message."""
        pass

    @abc.abstractmethod
    def start(self):
        """Start this client."""
        pass

    @abc.abstractmethod
    def connect(self, addr: settings.AppAddr, component: settings.ComponentEnum):
        """Connect to a server component."""
        pass

    @abc.abstractmethod
    def stop(self):
        """Stop this client."""
        pass

    @abc.abstractmethod
    def fire(self, event, values):
        """Call the method of a communication protocol."""
        pass


class ICommunicationProtocol(abc.ABC):

    @abc.abstractmethod
    def on_receive_msg(self, msg: message.IMessage):
        pass

    @abc.abstractmethod
    def on_connected(self):
        """Fire after success connecting."""
        pass

    @abc.abstractmethod
    def fini(self):
        pass

    @abc.abstractmethod
    async def _waiting_for(self, msg_id_or_ids: Union[int, List[int]],
                           timeout: int):
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


class CommunicationProtocol(ICommunicationProtocol):
    """Parent class of app protocols."""

    def __init__(self, client: Client):
        self._client = client
        self._waiting_futures = {}  # type: Dict[id, asyncio.Future]

    def on_receive_msg(self, msg):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
        future = self._waiting_futures.pop(msg.id, None)
        if future is not None:
            future.set_result(msg)

    def fini(self):
        logger.debug('[%s] Fini', self)
        for coro in self._waiting_futures.values():
            coro.cancel()
        self._waiting_futures.clear()
        self._waiting_futures = None
        self._client = None

    async def on_connected(self):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())

    def _waiting_for(self, msg_id_or_ids: Union[int, List[int]],
                     timeout: int = settings.WAITING_FOR_SERVER_TIMEOUT
                     ) -> asyncio.Future:
        msg_id = msg_id_or_ids
        future = asyncio.get_event_loop().create_future()
        self._waiting_futures[msg_id] = future
        return _waiting_for_future(future, timeout, [msg_id])

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(client={self._client})'


class LoginAppProtocol(CommunicationProtocol):
    """Communication protocol with LoginApp."""

    async def login(self, account_name, password) -> bool:
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
        hello_msg = message.Message(
            spec=enki.spec.app.loginapp.hello,
            fields=('2.5.10', '0.1.0', b'')
        )
        await self._client.send(hello_msg)
        resp_msg = await self._waiting_for(
            msg_id_or_ids=enki.spec.app.client.onHelloCB.id,
            timeout=2
        )
        if resp_msg is None:
            return
        # TODO: [07.12.2020 1:08 a.burov@mednote.life]
        # Обработка случая, когда пришло другое сообщение
        login_msg = message.Message(
            spec=enki.spec.app.loginapp.login,
            fields=(0, b'', account_name, password, '96C93073CCCBB4F8362D769C8629CCCC')
        )
        await self._client.send(login_msg)
        resp_msg = await self._waiting_for(
            enki.spec.app.client.onLoginSuccessfully.id, 5
        )
        # TODO: [06.12.2020 22:32 a.burov@mednote.life]
        # Достаём адрес BaseApp и подключаемся к нему (это тоже считается частью
        # логина)
        fields = resp_msg.get_values()
        baseapp_addr = settings.AppAddr(fields[1], fields[2])
        await self._client.connect(baseapp_addr, settings.ComponentEnum.BASEAPP)


class BaseAppProtocol(CommunicationProtocol):
    """Communication protocol of BaseApp."""

    async def on_connected(self):
        logger.debug('[%s]', self)
        hello_msg = message.Message(
            spec=enki.spec.app.baseapp.hello,
            fields=('2.5.10', '0.1.0', b'')
        )
        await self._client.send(hello_msg)
        resp_msg = await self._waiting_for(
            msg_id_or_ids=enki.spec.app.client.onHelloCB.id,
            timeout=2
        )
        if resp_msg is None:
            return


class Client(IClient):

    _PROTOCOLS = {
        settings.ComponentEnum.LOGINAPP: LoginAppProtocol,
        settings.ComponentEnum.BASEAPP: BaseAppProtocol,
    }

    def __init__(self, loginapp_addr: settings.AppAddr):
        # TODO: [06.12.2020 21:40 a.burov@mednote.life]
        self._loginapp_addr = loginapp_addr
        self._baseapp_addr = None  # type: settings.AppAddr
        self._conn = None  # type: connection.AppConnection
        self._serializer = serializer.Serializer()
        self._protocol = None  # type: CommunicationProtocol

        self._in_buffer = b''

    def on_receive_data(self, data):
        """Handle incoming data from a server."""
        logger.debug('[%s] Received data (%s)', self, devonly.func_args_values())
        if self._in_buffer:
            # Waiting for next chunks of a message
            data = self._in_buffer + data
        msg = self._serializer.deserialize(data)
        if msg is None:
            logger.debug('[%s] Got chunk of a message', self)
            self._in_buffer += data
            return
        logger.debug('[%s] Message "%s" fields: %s', self, msg.name, msg.get_values())
        self._protocol.on_receive_msg(msg)
        self._in_buffer = b''

    async def send(self, msg: message.Message):
        data = self._serializer.serialize(msg)
        await self._conn.send(data)

    async def start(self):
        await self.connect(self._loginapp_addr, settings.ComponentEnum.LOGINAPP)

    def stop(self):
        if self._conn is None:
            return
        self._conn.close()
        self._baseapp_addr = None
        self._conn = None
        self._protocol = None

    async def connect(self, addr: settings.AppAddr,
                      component: settings.ComponentEnum):
        if self._protocol is not None:
            self._protocol.fini()
        if self._conn is not None:
            self._conn.close()
        self._protocol = self._PROTOCOLS[component](client=self)
        self._conn = connection.AppConnection(host=addr.host, port=addr.port,
                                              client_app=self)
        await self._conn.connect()
        await self._protocol.on_connected()

    async def fire(self, msg_name, *values) -> Any:
        method = getattr(self._protocol, msg_name)
        return await method(*values)

    def __str__(self) -> str:
        return f'{__class__.__name__}({self._loginapp_addr})'
