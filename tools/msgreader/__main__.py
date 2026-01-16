"""Скрипт для анализа сериализованных KBEngine-сообщений."""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from pathlib import Path

import pyperclip

from enki.kbeenum import ComponentType
from enki.misc import devonly
from enki.misc.log import setup_root_logger
from tools.msgreader.cli_args.args_types import CommandNameEnum
from tools.msgreader.cli_args.cli_args import get_cli_args_info
from tools.msgreader.outer import MsgInfoOuter
from tools.msgreader.readers.hex_bites_reader import (
    HexBitesReader,
)
from tools.msgreader.readers.pcap_msg_reader_app import PcapMsgReaderApp

logger = logging.getLogger(__name__)


async def main() -> None:
    """Точка входа."""
    cli_args_info = get_cli_args_info()
    setup_root_logger(level_name=cli_args_info.main_args.log_level.value)

    if cli_args_info.main_args.command_name == CommandNameEnum.PCAP:
        online_pcap_args = cli_args_info.online_pcap_args
        assert online_pcap_args is not None

        pcap_files_directory = Path(online_pcap_args.pcap_files_directory)
        if not pcap_files_directory.is_dir():
            logger.error(
                "The path is not a directory or not exsist (path = '%s')",
                pcap_files_directory,
            )
            sys.exit(1)

        mapping_file = Path(online_pcap_args.component_name_by_ip_file)
        if not mapping_file.exists() or not mapping_file.is_file():
            logger.error(
                "The file contained the ip to component name mapping "
                "does not exist ('%s')",
                mapping_file,
            )
            sys.exit(1)

        pcap_msg_reader_app = PcapMsgReaderApp(
            pcap_files_directory, mapping_file, online_pcap_args.ignored_msgs
        )

        async def ask_exit(pcap_msg_reader_app: PcapMsgReaderApp, sig) -> None:
            logger.debug("%s", devonly.func_args_values())
            if pcap_msg_reader_app.stopping:
                return

            logger.info(
                "The '%s' signal catched. Stop the application ...", sig
            )
            while not pcap_msg_reader_app.is_started:
                logger.info("The application is not started yet. Wait to stop")
                await asyncio.sleep(0)

            await pcap_msg_reader_app.stop()
            logger.info("The application is stopping now ...")

        loop = asyncio.get_event_loop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig,
                lambda *signame: asyncio.create_task(
                    ask_exit(pcap_msg_reader_app, sig)
                ),
            )

        # await asyncio.sleep(1)

        # loop.run_until_complete(asyncio.sleep(1))

        logger.info("The application has been started")
        await pcap_msg_reader_app.start()

        # try:
        #     logger.info("[%s] The application has been started")
        #     loop.run_until_complete(pcap_msg_reader_app.start())
        # except KeyboardInterrupt:
        #     logger.info("The application is stopping now ...")
        # try:
        #     loop.run_until_complete(pcap_msg_reader_app.stop())
        # except KeyboardInterrupt:
        #     pass
        # loop.run_until_complete(pcap_msg_reader_app.wait_until_stop())
        # logger.info("The application has been succesfully stoped")

        await pcap_msg_reader_app.wait_until_stop()
        logger.info("The application has been succesfully stoped")
        sys.exit(0)

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
    asyncio.run(main())
