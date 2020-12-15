"""Updater of client messages."""

import enum
import functools
import logging
import pathlib
import signal
from typing import Dict

from tornado import ioloop

from enki.misc import log
from enki import settings, runutil, kbetype
from enki.misc import devonly

from enki.updater import client, parser, codegen

logger = logging.getLogger(__name__)


async def main():
    log.setup_root_logger('DEBUG')
    client_specs = []
    loginapp_specs = []
    baseapp_specs = []

    client_app = client.UpdaterClient(loginapp_addr=settings.LOGIN_APP_ADDR)
    msg_parser = parser.MessagesParser()
    client_code_gen = codegen.MessagesCodeGen(settings.CodeGenDst.CLIENT)
    loginapp_code_gen = codegen.MessagesCodeGen(settings.CodeGenDst.LOGINAPP)
    baseapp_code_gen = codegen.MessagesCodeGen(settings.CodeGenDst.BASEAPP)

    shutdown_func = functools.partial(runutil.shutdown, client_app)
    sig_exit_func = functools.partial(runutil.sig_exit, shutdown_func)
    signal.signal(signal.SIGINT, sig_exit_func)
    signal.signal(signal.SIGTERM, sig_exit_func)

    await client_app.start()
    data = await client_app.fire('get_msg_specs')
    msg_specs = msg_parser.parse_app_msges(data)
    for msg_spec in msg_specs:
        if msg_spec.name.startswith('Client'):
            client_specs.append(msg_spec)
        else:
            loginapp_specs.append(msg_spec)

    # Request baseapp messages
    await client_app.fire('login', settings.LOGIN, settings.PASSWORD)
    data = await client_app.fire('get_msg_specs')
    msg_specs = msg_parser.parse_app_msges(data)
    for msg_spec in msg_specs:
        if msg_spec.name.startswith('Client'):
            client_specs.append(msg_spec)
        else:
            baseapp_specs.append(msg_spec)

    client_code_gen.write(sorted(client_specs, key=lambda s: s.id))
    logger.info(f'Client messages have been written (dst file = '
                f'"{client_code_gen.dst_path}")')
    loginapp_code_gen.write(sorted(loginapp_specs, key=lambda s: s.id))
    logger.info(f'LoginApp messages have been written (dst file = '
                f'"{loginapp_code_gen.dst_path}")')
    baseapp_code_gen.write(sorted(baseapp_specs, key=lambda s: s.id))
    logger.info(f'BaseApp messages have been written (dst file = '
                f'"{baseapp_code_gen.dst_path}")')

    # data = await client_app.fire('get_entity_msg_specs')

    runutil.shutdown(client_app)


if __name__ == '__main__':
    ioloop.IOLoop.current().asyncio_loop.create_task(main())
    ioloop.IOLoop.current().start()
