"""Updater of client messages."""

import argparse
import functools
import logging
import os
import signal
import sys
from typing import Tuple, List

from tornado import ioloop

from enki.misc import log, runutil
from enki import settings, command, kbeenum, kbeclient, message

from ninmah import parser, codegen

logger = logging.getLogger(__name__)


def get_arg_parser():
    desc = 'Ninmah. Code generator for client-server communication messages.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--generate', dest='generate', type=str,
                        action='append', nargs='+',
                        choices=['app', 'entity', 'error'],
                        help='The namespace of messages that will be generated')
    parser.add_argument('--clean-up', dest='clean_up', action='store_true',
                        help='Clean up all generated modules')
    parser.add_argument('--send-message', dest='send_message_data', type=str,
                        help='Send the message to the server. Format: <MSG_NAME> '
                             '<ARG_1> <ARG_2> .. <ARG_N> (example: %s)'
                             '' % "Loginapp::hello '2.5.10', '0.1.0', b''")
    parser.add_argument('--log-level', dest='log_level', type=str,
                        help='Log level (default: %(default)s)', default='DEBUG')

    return parser


async def _app_get_data(account_name: str, password: str) -> Tuple[bytes, bytes]:
    """Request LoginApp, BaseApp, ClientApp messages."""
    client = kbeclient.Client(settings.LOGIN_APP_ADDR)
    cmd = command.loginapp.ImportClientMessagesCommand(client)
    client.set_msg_receiver(cmd)
    await client.start()
    login_app_data = await cmd.execute()

    # Request baseapp messages
    cmd = command.loginapp.LoginCommand(
        client_type=kbeenum.ClientType.UNKNOWN, client_data=b'',
        account_name=account_name, password=password, force_login=False,
        client=client
    )
    client.set_msg_receiver(cmd)
    login_result = await cmd.execute()

    await client.stop()

    baseapp_addr = settings.AppAddr(host=login_result.host,
                                    port=login_result.tcp_port)
    client = kbeclient.Client(baseapp_addr)
    await client.start()

    cmd = command.baseapp.ImportClientMessagesCommand(client)
    client.set_msg_receiver(cmd)
    base_app_data = await cmd.execute()

    await client.stop()

    return login_app_data, base_app_data


async def _entity_get_data(account_name: str, password: str) -> bytes:
    """Request data of entity methods, property etc."""
    client = kbeclient.Client(settings.LOGIN_APP_ADDR)
    await client.start()
    cmd = command.loginapp.LoginCommand(
        client_type=kbeenum.ClientType.UNKNOWN, client_data=b'',
        account_name=account_name, password=password, force_login=False,
        client=client
    )
    client.set_msg_receiver(cmd)
    login_result = await cmd.execute()

    await client.stop()

    baseapp_addr = settings.AppAddr(host=login_result.host,
                                    port=login_result.tcp_port)
    client = kbeclient.Client(baseapp_addr)
    await client.start()

    cmd = command.baseapp.ImportClientEntityDefCommand(client)
    client.set_msg_receiver(cmd)
    data = await cmd.execute()

    await client.stop()

    return data


async def _error_get_data() -> bytes:
    """Request error messages."""
    client = kbeclient.Client(settings.LOGIN_APP_ADDR)
    cmd = command.loginapp.ImportServerErrorsDescrCommand(client)
    client.set_msg_receiver(cmd)
    await client.start()
    error_data = await cmd.execute()

    await client.stop()

    return error_data


async def main():
    arg_parser = get_arg_parser()
    try:
        namespace = arg_parser.parse_args()
    except SystemExit:
        # run with --help arguments
        await runutil.shutdown(timeout=0)
        return

    if namespace.generate is None:
        arg_parser.print_help(sys.stderr)
        await runutil.shutdown(timeout=0)
        return

    account_name = settings.ACCOUNT_NAME
    password = settings.PASSWORD

    log.setup_root_logger(namespace.log_level)

    shutdown_func = functools.partial(runutil.shutdown, 0)
    sig_exit_func = functools.partial(runutil.sig_exit, shutdown_func)
    signal.signal(signal.SIGINT, sig_exit_func)
    signal.signal(signal.SIGTERM, sig_exit_func)

    generate = sum(namespace.generate, [])

    if 'app' in generate:
        login_app_data, base_app_data = await _app_get_data(account_name, password)

        parser_ = parser.ClientMsgesParser()
        msg_specs: List[message.MessageSpec] = []
        for app_data in (login_app_data, base_app_data):
            msg_specs.extend(parser_.parse_app_msges(app_data))

        code_generator = codegen.AppMessagesCodeGen(settings.CodeGenDstPath.APP)
        code_generator.generate(msg_specs)

    if 'entity' in generate:
        type_dst_path = settings.CodeGenDstPath.TYPE
        entity_dst_path = settings.CodeGenDstPath.ENTITY

        data = await _entity_get_data(account_name, password)

        parser_ = parser.EntityDefParser()
        type_specs, entities = parser_.parse(data)

        type_code_gen = codegen.TypesCodeGen(type_dst_path)
        type_code_gen.generate(type_specs)

        entity_code_gen = codegen.EntitiesCodeGen(entity_dst_path)
        entity_code_gen.generate(entities, type_specs)

    if 'error' in generate:
        error_dst_path = settings.CodeGenDstPath.SERVERERROR

        error_data = await _error_get_data()

        parser_ = parser.ServerErrorParser()
        error_specs = parser_.parse(error_data)

        error_code_gen = codegen.ErrorCodeGen(error_dst_path)
        error_code_gen.generate(error_specs)

    await runutil.shutdown(0)


if __name__ == '__main__':

    async def _main():
        try:
            await main()
        except Exception as err:
            logger.error(err, exc_info=True)
            await runutil.shutdown(0)

    ioloop.IOLoop.current().asyncio_loop.create_task(_main())
    ioloop.IOLoop.current().start()
