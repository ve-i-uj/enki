"""System manager."""

import abc
import asyncio
import contextlib
import datetime
import logging
from typing import Optional

from enki import command, msgspec
from enki.misc import devonly
from enki.interface import IApp, IResult
from enki.kbeclient.message import Message

logger = logging.getLogger(__name__)


class IPeriodic(abc.ABC):

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def _periodic(self):
        pass


class _ServerTickPeriodic(IPeriodic):

    def __init__(self, app: IApp, period: float):
        self._app = app
        self._period = period
        self._task: Optional[asyncio.Task] = None
        self._active: bool = False
        logger.debug('[%s] %s', self, devonly.func_args_values())

    async def _periodic(self):
        await asyncio.sleep(self._period)
        while self._active:
            cmd = command.baseapp.OnClientActiveTickCommand(
                client=self._app.client,
                timeout=self._period
            )
            res: IResult = await self._app.send_command(cmd)
            if not res.success:
                logger.warning(f'[{self}] No connection with the server')
                self._app.on_end_receive_msg()
                break
            await asyncio.sleep(self._period)

    def start(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._task = asyncio.create_task(self._periodic())
        self._active = True

    async def stop(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._active = False
        if self._task is None:
            logger.warning(f'[{self}] The task has not been started')
            return
        self._task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._task

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(app={self._app}, period={self._period})'


class SysMgr:
    """System manager."""

    def __init__(self, app: IApp):
        self._app = app

        self._last_server_tick_time: datetime.datetime = datetime.datetime.now()
        self._server_tick: Optional[_ServerTickPeriodic] = None
        logger.debug('[%s] %s', self, devonly.func_args_values())

    def start_server_tick(self, period: float):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        self._server_tick = _ServerTickPeriodic(self._app, period)
        self._server_tick.start()

    async def stop_server_tick(self):
        logger.debug('[%s] %s', self, devonly.func_args_values())
        if self._server_tick is None:
            logger.warning(f'[{self}] The loop of the "onClientActiveTick" '
                           f'message has not beed started')
            return
        await self._server_tick.stop()

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'
