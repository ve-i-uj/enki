"""Updater of client messages (code generator)."""

import argparse
import functools
import importlib
import logging
import signal
import shutil
from typing import List

from tornado import ioloop

from enki.misc import log, runutil
from enki import settings

from ninmah import exception

logger = logging.getLogger(__name__)


def get_arg_parser():
    desc = 'Ninmah. Code generator for client-server communication messages.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--clean-up-only', dest='clean_up_only', action='store_true',
                        help='Only clean up all generated modules and exit then')
    parser.add_argument('--log-level', dest='log_level', type=str,
                        help='Log level (default: %(default)s)', default='DEBUG')

    return parser


async def main():
    arg_parser = get_arg_parser()
    try:
        namespace = arg_parser.parse_args()
    except SystemExit:
        # run with --help arguments
        await runutil.shutdown(timeout=0)
        return

    log.setup_root_logger(namespace.log_level)

    # Clean up all old generated code
    type_file = settings.CodeGenDstPath.TYPE
    with type_file.open('w'):
        pass
    app_root = settings.CodeGenDstPath.APP
    for app_name in ('baseapp', 'client', 'loginapp'):
        path = app_root / app_name / '_generated.py'
        with path.open('w'):
            pass
    entity_root = settings.CodeGenDstPath.ENTITY
    shutil.rmtree(entity_root)
    entity_root.mkdir()
    with (entity_root / '__init__.py').open('w'):
        pass
    error_root = settings.CodeGenDstPath.SERVERERROR
    with error_root.open('w'):
        pass
    logger.info('All old generated modules have been deleted')

    if namespace.clean_up_only:
        await runutil.shutdown(timeout=0)
        logger.info('Code generator has been started with "--clean-up-only". Exit')
        return

    # The old code can be invalid. We should delete the old generated code at
    # first. And only then generate new one. That's why import statements
    # using only after old code deletion.
    from ninmah import parser, codegen, datagetter

    account_name = settings.ACCOUNT_NAME
    password = settings.PASSWORD

    shutdown_func = functools.partial(runutil.shutdown, 0)
    sig_exit_func = functools.partial(runutil.sig_exit, shutdown_func)
    signal.signal(signal.SIGINT, sig_exit_func)
    signal.signal(signal.SIGTERM, sig_exit_func)

    # Generate app descriptions
    login_app_data, base_app_data = await datagetter.app_get_data(account_name, password)

    parser_ = parser.ClientMsgesParser()
    msg_specs: List[parser.ParsedAppMessageDC] = []
    for app_data in (login_app_data, base_app_data):
        msg_specs.extend(parser_.parse(app_data))

    code_generator = codegen.AppMessagesCodeGen(settings.CodeGenDstPath.APP)
    code_generator.generate(msg_specs)

    # Generate entity descriptions
    type_dst_path = settings.CodeGenDstPath.TYPE
    entity_dst_path = settings.CodeGenDstPath.ENTITY

    data = await datagetter.entity_get_data(account_name, password)

    parser_ = parser.EntityDefParser()
    type_specs, entities = parser_.parse(data)

    type_code_gen = codegen.TypesCodeGen(type_dst_path)
    type_code_gen.generate(type_specs)
    # The generated types will be using by the next code generators.
    # That's why we need to reload a new created module.
    from enki import descr
    importlib.reload(descr.deftype._generated)
    importlib.reload(descr.deftype)

    entity_code_gen = codegen.EntitiesCodeGen(entity_dst_path)
    entity_code_gen.generate(entities)

    # Generate error descriptions
    error_dst_path = settings.CodeGenDstPath.SERVERERROR

    error_data = await datagetter.error_get_data()

    parser_ = parser.ServerErrorParser()
    error_specs = parser_.parse(error_data)

    error_code_gen = codegen.ErrorCodeGen(error_dst_path)
    error_code_gen.generate(error_specs)

    await runutil.shutdown(0)


if __name__ == '__main__':

    async def _main():
        try:
            await main()
        except exception.StopClientException as err:
            logger.info(err)
        except Exception as err:
            logger.error(err, exc_info=True)
        await runutil.shutdown(0)

    ioloop.IOLoop.current().asyncio_loop.create_task(_main())
    ioloop.IOLoop.current().start()
