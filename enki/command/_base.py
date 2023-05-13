from __future__ import annotations

import abc
import asyncio
import enum
import logging
import functools
from dataclasses import dataclass
import time
from typing import Coroutine, List, Any, Optional

from enki.core.enkitype import Result
from enki import settings
from enki.misc import devonly
from enki.net.client import StreamClient, TCPClient
from enki.core.message import IMsgReceiver, Message, MsgDescr

logger = logging.getLogger(__name__)

TIMEOUT_ERROR_MSG = 'Timeout Error'


@dataclass
class CommandResult(Result):
    success: bool
    result: Any = None
    text: str = ''


@dataclass
class _RequestData:
    sent_msg_spec: MsgDescr
    success_msg_spec: Optional[MsgDescr]
    error_msg_specs: List[MsgDescr]
    future: asyncio.Future
    timeout: float


class ICommand(abc.ABC):

    @abc.abstractmethod
    def execute(self) -> Any:
        pass


class IAwaitableCommand(ICommand):

    @property
    @abc.abstractmethod
    def waiting_for_ids(self) -> list[int]:
        pass

    @abc.abstractmethod
    def get_timeout_err_text(self) -> str:
        pass


class AwaitableCommandState(enum.Enum):
    INITIALIZED = enum.auto()
    WAITING_RESPONSE = enum.auto()
    MSG_RECEIVED = enum.auto()
    CANCELLED_BY_TIMEOUT = enum.auto()
    ERROR_CONNECTION_CLOSED = enum.auto()
    EXECUTED = enum.auto()


class Command(IAwaitableCommand, IMsgReceiver):
    """Base class for commands.

    The command is a request-response communication approach between
    the client and the server. A descendent class encapsulates request and
    response data and gives the asynchronous interface to use the "execute"
    command method like a coroutine.

    A descendent should override the "execute" method and set the response and
    request messages to the variables below.
    """
    _req_msg_spec: MsgDescr
    _success_resp_msg_spec: Optional[MsgDescr]
    _error_resp_msg_specs: list[MsgDescr]

    def __init__(self, client: TCPClient):
        self._client = client
        self._req_data_by_msg_id: dict[int, _RequestData] = {}
        self._state = AwaitableCommandState.INITIALIZED
        self._resp_future: asyncio.Future[Any] = asyncio.get_event_loop(
        ).create_future()

    @property
    def status(self) -> AwaitableCommandState:
        return self._state

    def on_receive_msg(self, msg: Message) -> bool:
        """
        The method returns True if the command is waiting for the message.
        I.e. the message will be handled.
        """
        logger.debug(f'[{self}]  ({devonly.func_args_values()})')
        req_data = self._req_data_by_msg_id.get(msg.id, None)
        if req_data is None:
            logger.debug(
                f'[{self}] The message "{msg.id}" is not being waited for')
            return False
        future = req_data.future
        future.set_result(msg)
        logger.debug('[%s] The message "%s" is set to the future', self,
                     msg.id)

        self._state = AwaitableCommandState.MSG_RECEIVED
        return True

    def on_end_receive_msg(self):
        if self._state == AwaitableCommandState.WAITING_RESPONSE:
            self._state = AwaitableCommandState.ERROR_CONNECTION_CLOSED
        self._resp_future.cancel()

    async def execute(self) -> Any:
        raise NotImplementedError

    @functools.cached_property
    def waiting_for_ids(self) -> list[int]:
        ids = []
        if self._success_resp_msg_spec is not None:
            ids.append(self._success_resp_msg_spec.id)
        ids += [s.id for s in self._error_resp_msg_specs]
        return ids

    def get_timeout_err_text(self) -> str:
        success_msg = self._success_resp_msg_spec.name \
            if self._success_resp_msg_spec else '<not set>'
        error_msgs = ', '.join(f'"{m.name}"'
                               for m in self._error_resp_msg_specs)
        return f'No response nor for success message "{success_msg}" ' \
               f'nor for error messages {error_msgs} ' \
               f'(sent message = "{self._req_msg_spec.name}")'

    def _waiting_for(
        self,
        timeout: float = settings.WAITING_FOR_SERVER_TIMEOUT
    ) -> Coroutine[None, None, Optional[Message]]:
        """Waiting for a response on the sent message."""
        logger.debug(f'[{self}]  ({devonly.func_args_values()})')
        awaitable_data = _RequestData(
            sent_msg_spec=self._req_msg_spec,
            success_msg_spec=self._success_resp_msg_spec,
            error_msg_specs=self._error_resp_msg_specs,
            future=self._resp_future,
            timeout=timeout)
        if self._success_resp_msg_spec is not None:
            self._req_data_by_msg_id[
                self._success_resp_msg_spec.id] = awaitable_data
        for error_msg_spec in self._error_resp_msg_specs:
            self._req_data_by_msg_id[error_msg_spec.id] = awaitable_data

        coro = self._future_with_timeout(awaitable_data)
        self._state = AwaitableCommandState.WAITING_RESPONSE
        return coro

    async def _future_with_timeout(self, req_data: _RequestData) -> Any:
        """Coroutine wrapping timeout to future."""
        try:
            res = await asyncio.wait_for(req_data.future, req_data.timeout)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            self._state = AwaitableCommandState.CANCELLED_BY_TIMEOUT
            return None

        return res

    def __str__(self):
        state = f'waiting for "{self.waiting_for_ids}"'
        return f'{self.__class__.__name__}({state})'


class StreamCommand(Command):
    """Команда обрабатывающая в ответ не другую команду, а стрим."""

    def __init__(self, client: StreamClient):
        super().__init__(client)
        # Данные будут идти пока сервер не закроет соединение. Future нужна,
        # чтобы сохранять, что передача стрима окончена.
        self._result_future = asyncio.get_event_loop().create_future()
        self._chunks: list[list] = []
        self._last_chunk_time = 0.0

    @property
    def last_chunk_time(self) -> float:
        return self._last_chunk_time

    @property
    def is_updated(self) -> bool:
        return self._last_chunk_time > 0.0

    def on_receive_msg(self, msg: Message) -> bool:
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._chunks.append(msg.get_values())
        self._last_chunk_time = time.time()
        return True

    def on_end_receive_msg(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._result_future.set_result(self._chunks)

    async def get_result(self) -> list[list]:
        return await self._result_future


from . import _base

logger = logging.getLogger(__name__)


@dataclass
class LookAppResultData:
    component_type: int
    component_id: int
    istate: int


@dataclass
class LookAppCommandResult(_base.CommandResult):
    success: bool
    result: LookAppResultData
    text: str = ''


class LookAppCommand(_base.StreamCommand):
    """The base class for the 'lookApp' command."""

    def __init__(self, client: StreamClient, req_msg_spec: MsgDescr,
                 fake_resp_msg_spec: MsgDescr):
        """Constructor.

        Args:
            client (StreamClient): клиент, который в ответ на подключение
                получит открытый стрим
            req_msg_spec (MsgDescr): сообщение, на которое сервер откроет скрим
            fake_resp_msg_spec (MsgDescr): фэйковое сообщение, в котором описаны
                поля для декодирования стрима (см. Enki::fakeRespLookApp)
        """
        super().__init__(client)
        client.set_resp_msg_spec(fake_resp_msg_spec)

        self._req_msg_spec = req_msg_spec
        self._success_resp_msg_spec = None
        self._error_resp_msg_specs = []

        self._msg = Message(spec=self._req_msg_spec, fields=tuple())

    async def execute(self) -> LookAppCommandResult:
        await self._client.send(self._msg)
        timeout_time = time.time() + settings.WAITING_FOR_SERVER_TIMEOUT
        while timeout_time > time.time():
            if self.is_updated:
                break
            await asyncio.sleep(settings.SECOND * 0.5)

        if self._client.is_stopped:
            return LookAppCommandResult(False,
                                        text=self.get_timeout_err_text())

        self._client.stop()
        res = await self.get_result()
        if not res:
            return LookAppCommandResult(False, text='No data from server')

        return LookAppCommandResult(True, LookAppResultData(*res[0]))
