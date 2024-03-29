from __future__ import annotations

import abc
import asyncio
from asyncio import Future
import dataclasses
import enum
import logging
import functools
import time
from dataclasses import dataclass
from typing import Coroutine, List, Any, Optional

from enki import settings
from enki.core import utils
from enki.misc import devonly
from enki.core.enkitype import AppAddr, Result
from enki.core.message import Message, MsgDescr
from enki.net.client import MsgTCPClient, TCPClient
from enki.net.inet import IClientMsgReceiver, IMsgForwarder

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

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


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


class TCPCommand(IAwaitableCommand, IClientMsgReceiver):
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

    def __init__(self, client: MsgTCPClient):
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

    def _waiting_for(self, timeout: float = settings.WAITING_FOR_SERVER_TIMEOUT
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
