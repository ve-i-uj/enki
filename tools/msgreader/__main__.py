"""Скрипт для анализа сообщения из байтов."""

import argparse
import logging
import pprint
import struct
import sys
import time
from datetime import datetime

import pyperclip
import dateutil.parser

from enki import msgspec
from enki.kbeenum import ComponentType
from enki.kbetype.decoders.custom_decoders import MESSAGE_ID
from enki.misc.log import setup_root_logger
from enki.msg.msg_serializer import MessageSerializer
from tools.msgreader.parsers import MESSAGE_PARSERS_BY_COMP_TYPE

TITLE = (
    "The script reads the message data from WireShark and prints "
    "the field values of the message."
)

logger = logging.getLogger(__name__)


def read_args():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument(
        "component_name",
        type=str,
        choices=[
            c.name.lower() for c in msgspec.MSG_COMP_SPEC_BY_COMPONENT.keys()
        ],
        help="The name of the component to which the message is addressed",
    )
    parser.add_argument(
        "hex_data",
        type=str,
        nargs="?",
        help="The hex data of the message copied from WireShark",
    )
    parser.add_argument(
        "--read-stdin",
        dest="read_from_stdin",
        action="store_true",
        help="Read the data forever from the stdin",
    )
    parser.add_argument(
        "--buf",
        dest="read_from_clipboard",
        action="store_true",
        help="Read the data from the clipboard",
    )
    parser.add_argument(
        "--whatis",
        dest="find_msg_id",
        action="store_true",
        help="Try to realize what is the message id",
    )
    parser.add_argument(
        "--bare-msg",
        dest="msg_name",
        type=str,
        help="Try to deserialize the message without envelope (length and number)",
    )
    parser.add_argument(
        "--log-level",
        dest="log_level",
        type=str,
        default="INFO",
        choices=logging._nameToLevel.keys(),
        help="Logging level",
    )

    return parser.parse_args()


def normalize_wireshark_data(str_data: str) -> bytes:
    """Конвертирует скопированные из WireShark данные, как "as Hex String"."""
    return bytes.fromhex(str_data)


def read_from_stdin():
    timeout = 0.1
    try:
        for stdin_line in iter(sys.stdin.readline, b""):
            line = stdin_line.strip()
            if not line:
                logger.debug("There is no data. Sleep 1 second")
                time.sleep(timeout)
                continue

            dt_str, src_ip, dst_ip, src_port, dst_port, hex_data = line.split("|")
            dt = dateutil.parser.parse(dt_str)

            logger.debug("Receive hex stream (data = %s)", line)
            data = normalize_wireshark_data(hex_data)
            logger.debug("Receive data (data = %s)", data)

            if not data:
                continue

            msg_name = None
            if src_ip == dst_ip and len(data) != 2:
                # TODO: [2025-08-31 16:34 burov_alexey@mail.ru]:
                # Пока так.
                # Это проверка контейнера, поэтому это или из контейнера
                # приходит lookApp, или ответ в виде стрима onLookApp
                msg_name = "Loginapp::onLookApp"

            handle_data(
                memoryview(data),
                msg_name=msg_name,
                only_find_msg_id=False,
                component_name="loginapp",
            )
    except KeyboardInterrupt:
        sys.stdout.flush()


def handle_data(
    data: memoryview,
    msg_name: str | None,
    only_find_msg_id: bool,
    component_name: str,
):
    def print_end():
        return logger.info("\n\n*** ------------- ***\n")

    if msg_name is not None:
        msg_split_name = msg_name.split("::", 1)
        if len(msg_split_name) != 2:
            logger.error('Invalid message name (msg_name = "%s")', msg_name)
            print_end()
            return

        component_name, _msg_name = msg_split_name

        component_name = component_name.lower()
        comp_type = ComponentType.__members__[component_name.upper()]
        comp_msg_spec = msgspec.MSG_COMP_SPEC_BY_COMPONENT[comp_type]

        serializer = MessageSerializer(comp_msg_spec)

        msg_spec_by_name = {
            sp.name: sp for sp in comp_msg_spec.msg_spec_by_id.values()
        }
        msg_spec = msg_spec_by_name.get(msg_name)
        if msg_spec is None:
            logger.error(
                'The message specification is not found (msg_name = "%s")',
                msg_name,
            )
            print_end()
            return

        try:
            parser = MESSAGE_PARSERS_BY_COMP_TYPE[comp_type][msg_spec.id]
        except KeyError as err:
            logger.error(
                "There is no parser for the message id '%s' (err = '%s')",
                msg_spec.id,
                err,
            )

        msg, data_tail = serializer.deserialize_only_data(data, msg_spec.id)
        if msg is None:
            logger.error('Cannot parse data of the "%s" message', msg_name)
            print_end()
            return

        if data_tail:
            logger.warning(
                "There is data tail (data tail = '%s')",
                data_tail.tobytes().decode(),
            )

        res = parser().parse(msg)

        err_text = (
            f'The message "{msg.name}" cannot be parsed '
            f"(parser={parser.__name__})"
        )
        try:
            res = parser().parse(msg)
        except Exception as err:  # noqa: BLE001
            logger.error(err)
            logger.error(err_text)
            print_end()
            return

        if not res.success:
            logger.error(err_text)
            print_end()
            return

        assert res.result is not None

        txt_header = f"*** {msg.name} (id = {msg.id}) ***"
        logger.info(txt_header)
        logger.info(pprint.pformat(res.result.asdict(), indent=4))

        print_end()
        return

    decoded_msg_id, _offset = MESSAGE_ID.decode(data)
    logger.info('The message id is "%s"', decoded_msg_id)

    comp_type = ComponentType.__members__[component_name.upper()]
    comp_msg_spec = msgspec.MSG_COMP_SPEC_BY_COMPONENT[comp_type]
    message_descr = comp_msg_spec.msg_spec_by_id.get(decoded_msg_id)
    if message_descr is None:
        logger.info(
            "There is no info about the message id '%s' for the component '%s'",
            decoded_msg_id,
            comp_type.name,
        )
        print_end()
        return

    logger.info('The message name is "%s"', message_descr.name)

    if only_find_msg_id:
        print_end()
        return

    serializer = MessageSerializer(comp_msg_spec)

    try:
        msg, data_tail = serializer.deserialize(data)
    except (KeyError, struct.error) as err:
        logger.error(
            'The data cannot be decoded (msg_id = "%s", err = "%s")',
            message_descr.id,
            err,
        )
        print_end()
        return

    if msg is None:
        logger.error("The data cannot be parsed to the message")
        print_end()
        return

    if data_tail:
        logger.warning(
            "There is unparsed data tail after parsing. "
            "Multiple messages in the data? (data_tail=%s)",
            data_tail.tobytes(),
        )

    parser_by_msg_id = MESSAGE_PARSERS_BY_COMP_TYPE.get(comp_type)
    if parser_by_msg_id is None or msg.id not in parser_by_msg_id:
        logger.error('There is no parser for the "%s" message', msg.name)
        print_end()
        return

    parser = parser_by_msg_id[msg.id]

    err_text = (
        f'The message "{msg.name}" cannot be parsed (parser={parser.__name__})'
    )
    try:
        res = parser().parse(msg)
    except Exception as err:  # noqa: BLE001
        logger.error(err)
        logger.error(err_text)
        print_end()
        return

    if not res.success:
        logger.error(err_text)
        print_end()
        return

    assert res.result is not None

    txt_header = f"*** {msg.name} (id = {msg.id}) ***"
    logger.info(txt_header)
    logger.info(pprint.pformat(res.result.asdict(), indent=4))
    print_end()


def main() -> None:
    """Точка входа."""
    namespace = read_args()
    setup_root_logger(level_name=namespace.log_level)

    if namespace.read_from_stdin:
        read_from_stdin()

    if not namespace.read_from_clipboard and namespace.hex_data is None:
        logger.error('There is no hex data in the console arguments. See "help"')
        sys.exit(1)

    if namespace.read_from_clipboard and not pyperclip.paste().strip():
        logger.error(
            'There is no hex data in the memory buffer arguments. See "help"'
        )
        sys.exit(1)

    if namespace.read_from_clipboard:
        hex_data = pyperclip.paste().strip()
    else:
        hex_data = namespace.hex_data

    try:
        data = memoryview(normalize_wireshark_data(hex_data))
    except ValueError as err:
        logger.error("Malformed hex data. Error: %s", err)
        sys.exit(1)

    handle_data(
        data, namespace.msg_name, namespace.find_msg_id, namespace.component_name
    )


if __name__ == "__main__":
    main()
