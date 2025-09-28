"""Скрипт для анализа сериализованных KBEngine-сообщений."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pyperclip

from enki.kbeenum import ComponentType
from enki.misc.log import setup_root_logger
from tools.msgreader.cli_args.args_types import CommandNameEnum
from tools.msgreader.cli_args.cli_args import get_cli_args_info
from tools.msgreader.outer import MsgInfoOuter
from tools.msgreader.readers.hex_bites_reader import HexBitesReader
from tools.msgreader.readers.stream_reader.ip2component import Ip2ComponentType

logger = logging.getLogger(__name__)


def main() -> None:
    """Точка входа."""
    cli_args_info = get_cli_args_info()
    setup_root_logger(level_name=cli_args_info.main_args.log_level.value)

    if cli_args_info.main_args.command_name == CommandNameEnum.STREAM:
        stread_args = cli_args_info.stream_args
        assert stread_args is not None

        mapping_file = Path(stread_args.component_name_by_ip_file)
        if not mapping_file.exists():
            logger.error(
                "The file contained the ip to component name mapping "
                "does not exist ('%s')",
                mapping_file,
            )
            sys.exit(1)

        Ip2ComponentType(mapping_file)

        # for stdin_line in iter(sys.stdin.readline, b""):
        #     line = stdin_line.strip()
        #     if not line.strip():
        #         time.sleep(1)
        #     logger.debug("line = %s", line)

        raise NotImplementedError

    if cli_args_info.main_args.command_name == CommandNameEnum.HEX:
        hex_args = cli_args_info.hex_args
        if hex_args is None:
            logger.error(
                "No arguments for the hex message reader. Logic error. Exit"
            )
            sys.exit(1)

        try:
            comp_type: ComponentType = ComponentType.__members__[
                hex_args.component_name.upper()
            ]
        except KeyError:
            logger.error("Invalid component name. Exit")
            sys.exit(1)

        if not hex_args.read_from_clipboard and hex_args.hex_data is None:
            logger.error(
                'There is no hex data in the console arguments. See "help"'
            )
            sys.exit(1)

        if hex_args.read_from_clipboard and not pyperclip.paste().strip():
            logger.error(
                'There is no hex data in the memory buffer arguments. See "help"'
            )
            sys.exit(1)

        if hex_args.read_from_clipboard:
            hex_data = pyperclip.paste().strip()
        else:
            hex_data = hex_args.hex_data

        if hex_args.find_msg_id:
            msg_id_res = HexBitesReader().read_msg_id(hex_data)
            if not msg_id_res.success:
                logger.error(msg_id_res.text)
                sys.exit(1)

            msg_id = msg_id_res.result.msg_id
            assert msg_id is not None

            MsgInfoOuter().print_msg_id(msg_id)
            sys.exit(0)

        res = HexBitesReader().read_data(
            hex_data, hex_args.no_envelop_msg_name, comp_type
        )
        if not res.success:
            logger.error(res.text)
            sys.exit(1)

        msg = res.result.msg
        assert msg is not None

        MsgInfoOuter().print_msg(
            msg, show_fileds=cli_args_info.main_args.show_msg_fields
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
