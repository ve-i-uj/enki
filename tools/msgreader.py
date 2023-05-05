"""Скрипт для анализа сообщения из байтов."""

import argparse
import dataclasses
import logging
import pprint
import sys
from dataclasses import dataclass
from typing import Any

import pyperclip

from enki.net import msgspec
from enki.net.kbeclient import kbetype
from enki.net.kbeclient.client import MessageSerializer, Message
from enki.app import handler as handler_package


TITLE = ('The script reads the message data from WireShark and prints '
         'the field values of the message.')

FORMAT = '[%(levelname)s] %(asctime)s [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s'

logger = logging.getLogger(__file__)


def read_args():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('component_name', type=str,
                        choices=['machine', 'interfaces', 'dbmgr'],
                        help='The name of the component to which the message is addressed')
    parser.add_argument('hex_data', type=str, nargs='?',
                        help='The hex data of the message copied from WireShark')
    parser.add_argument('--buf', dest='read_from_clipboard', action='store_true',
                        help='Read the data from the clipboard')
    parser.add_argument('--whatis', dest='find_msg_id', action='store_true',
                        help='Try to realize what is the message id')
    parser.add_argument('--bare-msg', dest='msg_name', type=str,
                        help='Try to deserialize the message without envelope (length and number)')
    parser.add_argument('--log-level', dest='log_level', type=str,
                        default='INFO',
                        choices=logging._nameToLevel.keys(),
                        help='Logging level')

    return parser.parse_args()


def setup_root_logger(level_name: str):
    level = logging.getLevelName(level_name)
    logger = logging.getLogger()
    logger.setLevel(level)
    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(FORMAT)
    stream_handler.setFormatter(formatter)
    logger.handlers = [stream_handler]
    # logger.info(f'Logger was set (log level = "{level_name}")')


@dataclass
class MsgReaderResult:
    msg_id: int
    result: Any


def normalize_wireshark_data(str_data: str) -> bytes:
    """Конвертирует скопированные из WireShark данные, как "as Hex String"."""
    return bytes.fromhex(str_data)


def main():
    namespace = read_args()
    setup_root_logger(level_name=namespace.log_level)

    if not namespace.read_from_clipboard and namespace.hex_data is None:
        logger.error('There is no hex data in the console arguments. See "help"')
        sys.exit(1)

    hex_data: str = namespace.hex_data
    if namespace.read_from_clipboard:
        hex_data = pyperclip.paste()

    try:
        data = memoryview(normalize_wireshark_data(hex_data))
    except ValueError as err:
        logger.error(f'Malformed hex data. Error: {err}')
        sys.exit(1)

    if namespace.msg_name:
        component_name, *msg_names = namespace.msg_name.split('::')
        component_name: str = component_name.lower()
        spec_by_id = msgspec.app.SPEC_BY_ID_MAP.get(component_name)
        if spec_by_id is None:
            logger.error(f'The "{component_name}" is not registered in this MsgReader')
            sys.exit(1)
        serializer = MessageSerializer(spec_by_id)
        if len(msg_names) != 1:
            logger.error(f'Invalid message name '
                         f'(msg_name = "{namespace.msg_name}")')
            sys.exit(1)
        msg_name: str = msg_names[0]
        msg_spec_by_name = {sp.name: sp for sp in spec_by_id.values()}
        if msg_spec_by_name.get(namespace.msg_name) is None:
            logger.error(f'The message specification is not found or handler '
                         f'not registered (msg_name = "{namespace.msg_name}")')
            sys.exit(1)
        msg_spec = msg_spec_by_name[namespace.msg_name]
        handler = handler_package.SERVER_HANDLERS[component_name][msg_spec.id]
        data = kbetype.MESSAGE_ID.encode(msg_spec.id) \
            + kbetype.MESSAGE_LENGTH.encode(len(data)) \
            + data
        msg, tail = serializer.deserialize(memoryview(data))
        if msg is None:
            logger.error(f'Cannot parse data of the "{namespace.msg_name}" message')
            sys.exit(1)
        res = handler().handle(msg)

        logger.info(f'*** {msg.name} (id = {msg.id}) ***')
        pprint.pprint(res.asdict(), indent=4)

        sys.exit(0)


    msg_id, _offset = kbetype.MESSAGE_ID.decode(data)
    if namespace.find_msg_id:
        logger.info(f'The message id is "{msg_id}"')
        sys.exit(0)

    spec_by_id = msgspec.app.SPEC_BY_ID_MAP[namespace.component_name]
    serializer = MessageSerializer(spec_by_id)

    try:
        msg, data_tail = serializer.deserialize(data)
    except KeyError:
        logger.error(f'The data cannot be decoded (msg_id = "{msg_id}")')
        sys.exit(1)

    if msg is None:
        logger.error('The data cannot be parsed to the message')
        sys.exit(1)
    if data_tail:
        logger.warning('There is unparsed data tail after parsing. '
                       'Multiple messages in the data?')

    handlers = handler_package.SERVER_HANDLERS[namespace.component_name]
    if msg.id not in handlers:
        logger.error(f'There is no handler for the "{msg.name}" message')
        sys.exit(1)

    handler = handlers[msg.id]
    res = handler().handle(msg)

    logger.info(f'*** {msg.name} (id = {msg.id}) ***')
    pprint.pprint(res.asdict(), indent=4)


if __name__ == '__main__':
    main()
