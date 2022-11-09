#!/usr/bin/env python

"""Plugin application."""

import asyncio
import logging
import os
import signal
from typing import Coroutine, Optional

from enki.app.appl import App
from enki.misc import log
from enki import settings
from enki.enkitype import AppAddr

# The generated code based on the server assets.
import descr
# The user implementation of the server entities.
import entities

logger = logging.getLogger(__name__)

__MAIN_FUTURE: list[Coroutine] = []


async def main():
    log.setup_root_logger(os.environ.get('LOG_LEVEL', 'DEBUG'))

    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    app = App(
        AppAddr('localhost', 20013),
        settings.SERVER_TICK_PERIOD,
        entity_desc_by_uid=descr.entity.DESC_BY_UID,
        entity_impl_by_uid=entities.ENTITY_BY_UID,
        kbenginexml=descr.kbenginexml.root()
    )

    async def stop():
        for task in asyncio.all_tasks():
            # TODO: [2022-09-21 15:33 burov_alexey@mail.ru]:
            # Логика примера расположена в main. Если ещё придёт сигнал
            # остановки на стадии запуска, то нужно отменить main корутину.
            # Для данного примера - это корректно.
            if task.get_coro().__name__ == 'main':
                task.cancel()
        await app.stop()

    loop.add_signal_handler(signal.SIGINT, lambda: loop.create_task(stop()))
    loop.add_signal_handler(signal.SIGTERM, lambda: loop.create_task(stop()))

    res = await app.start(
        account_name='1',
        password='1'
    )
    if not res.success:
        logger.error(res.text)
        await app.stop()
        return

    await asyncio.sleep(3)
    acc: entities.Account = list(app._entity_helper._entities.values())[0]  # type: ignore
    acc.base.reqAvatarList()
    await asyncio.sleep(1)
    if not acc._avatars:
        acc.base.reqCreateAvatar(1, 'User name')
        await asyncio.sleep(2)
        acc.base.reqAvatarList()
        await asyncio.sleep(1)

    acc.base.selectAvatarGame(list(acc._avatars.keys())[0])

    await app.wait_until_stop()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    __MAIN_FUTURE.append(main())
    try:
        loop.run_until_complete(__MAIN_FUTURE[0])
    except asyncio.CancelledError:
        pass
    logger.info('Stopped')
