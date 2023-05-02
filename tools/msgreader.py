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
from enki.net.command.machine import RunningComponentInfo
from enki.app.handler import base, machinehandler


TITLE = ('The script reads the message data from WireShark and prints '
         'the field values of the message.')

FORMAT = '[%(levelname)s] %(asctime)s [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s'

logger = logging.getLogger(__file__)


def read_args():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('component_name', type=str,
                        choices=['machine', 'interfaces'],
                        help='The name of the component to which the message is addressed')
    parser.add_argument('hex_data', type=str, nargs='?',
                        help='The hex data of the message copied from WireShark')
    parser.add_argument('--buf', dest='read_from_clipboard', action='store_true',
                        help='Read the data from the clipboard')
    parser.add_argument('--whatis', dest='find_msg_id', action='store_true',
                        help='Try to realize what is the message id')
    parser.add_argument('--log-level', dest='log_level', type=str,
                        default='DEBUG',
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


SPEC_BY_ID_MAP = {
    'machine': msgspec.app.machine.SPEC_BY_ID,
}

MSG_HANDLER_MAP: dict[str, dict[int, base.Handler]] = {
    'machine': {
        msgspec.app.machine.onBroadcastInterface.id: machinehandler.OnBroadcastInterfaceHandler(),
        msgspec.app.machine.onFindInterfaceAddr.id: machinehandler.OnFindInterfaceAddrHandler(),
    }
}


def asdict(obj) -> dict[str, Any]:
    return {**dataclasses.asdict(obj),
            **{'__' + a: getattr(obj, a) for a in getattr(obj, '__add_to_dict__', [])}}


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

    if namespace.find_msg_id:
        msg_id, _offset = kbetype.MESSAGE_ID.decode(data)
        logger.info(f'The message id is "{msg_id}"')
        sys.exit(0)

    spec_by_id = SPEC_BY_ID_MAP[namespace.component_name]
    serializer = MessageSerializer(spec_by_id)

    msg, data_tail = serializer.deserialize(data)
    if msg is None:
        logger.error('The data cannot be parsed to the message')
        sys.exit(1)
    if data_tail:
        logger.warning('There is unparsed data tail after parsing. '
                       'Multiple messages in the data?')

    handlers = MSG_HANDLER_MAP[namespace.component_name]
    if msg.id not in handlers:
        logger.error(f'There is no handler for the "{msg.name}" message')
        sys.exit(1)

    handler = handlers[msg.id]
    res = handler.handle(msg)

    dct = asdict(res.result)
    pprint.pprint(dct, indent=4)


if __name__ == '__main__':
    main()
