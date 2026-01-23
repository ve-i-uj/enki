"""Файл получающий настройки для запуска скрипта."""

from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction  # type: ignore

from .args_types import (
    CliArgsInfo,
    CommandNameEnum,
    HexArgsInfo,
    LogLevel,
    MainArgsInfo,
    OnlinePcapArgsInfo,
)


def _get_main_parser() -> ArgumentParser:
    """Возвращает главный парсер."""
    assert __package__ is not None
    parser = ArgumentParser(
        prog="msgreader",
        description="The script read serialized KBEngine-messages",
    )
    parser.add_argument(
        "--log-level",
        dest="log_level",
        type=str,
        default=LogLevel.INFO.value,
        choices=[e.value for e in LogLevel],
        help="logging level",
    )
    parser.add_argument(
        "--show-msg-fields",
        dest="show_msg_fields",
        action="store_true",
        help="Show message fields values",
    )

    return parser


def _add_pcap_subparser(subparsers: _SubParsersAction) -> ArgumentParser:
    """Добавить команду-парсер к основному парсеру."""
    subparser: ArgumentParser = subparsers.add_parser(
        "pcap", help="the pcap-file reader"
    )

    subparser.add_argument(
        "--component-name-by-ip-file",
        type=str,
        required=True,
        dest="component_name_by_ip_file",
        help="the file contained the mapping of the KBEngine component name by ip",
    )
    subparser.add_argument(
        "--pcap-files-directory",
        type=str,
        required=True,
        dest="pcap_files_directory",
        help="the directory contained pcap files",
    )
    subparser.add_argument(
        "--ignored-msgs",
        nargs="*",
        dest="ignored_msgs",
        help="message names for ignoring in the printed info",
    )
    subparser.add_argument(
        "--show-data",
        action="store_true",
        default=False,
        dest="show_data",
        help="show data in output (default: False)",
    )
    subparser.add_argument(
        "--parse-msg",
        action="store_true",
        default=False,
        dest="parse_msg",
        help="parse messages (default: False)",
    )

    return subparser


def _add_hex_subparser(subparsers: _SubParsersAction) -> ArgumentParser:
    """Добавить команду-парсер к основному парсеру.

    Добавляется подпарсер для однаразового чтения сериализованного
    KBEngine-сообщения. Сообщение в виде 16-ричного байтового представления.
    """
    subparser = subparsers.add_parser(
        "hex", help="the CLI hex one shot message parser"
    )

    subparser.add_argument(
        "component_name",
        type=str,
        choices=[
            "dbmgr",
            "loginapp",
            "baseappmgr",
            "cellappmgr",
            "cellapp",
            "baseapp",
            "client",
            "machine",
            "logger",
            "interfaces",
            "supervisor",
        ],
        help="the component name (the message receiver)",
    )
    subparser.add_argument(
        "hex_data",
        type=str,
        nargs="?",
        help="the hex data of the message (copied from WireShark e.g.)",
    )
    subparser.add_argument(
        "--buf",
        dest="read_from_clipboard",
        action="store_true",
        help="read the data from the clipboard",
    )
    subparser.add_argument(
        "--whatis",
        dest="find_msg_id",
        action="store_true",
        help="try to realize what is the message id",
    )
    subparser.add_argument(
        "--no-envelop-msg-name",
        dest="no_envelop_msg_name",
        type=str,
        help="try to deserialize the message without envelope (without length and number)",
    )

    return subparser


def get_cli_args_info() -> CliArgsInfo:
    """Возвращает данные из командной строки."""
    main_parser = _get_main_parser()
    subparsers: _SubParsersAction[ArgumentParser] = main_parser.add_subparsers(
        required=True, dest="command_name", help="---------------"
    )
    _add_pcap_subparser(subparsers)
    _add_hex_subparser(subparsers)

    namespace = main_parser.parse_args()

    command_name = CommandNameEnum(namespace.command_name)

    main_args = MainArgsInfo(
        command_name=command_name,
        log_level=LogLevel(namespace.log_level),
        show_msg_fields=namespace.show_msg_fields,
    )

    online_pcap_args = None
    hex_args = None

    if main_args.command_name == CommandNameEnum.PCAP:
        online_pcap_args = OnlinePcapArgsInfo(
            component_name_by_ip_file=namespace.component_name_by_ip_file,
            pcap_files_directory=namespace.pcap_files_directory,
            ignored_msgs=(
                [] if namespace.ignored_msgs is None else namespace.ignored_msgs
            ),
            show_data=namespace.show_data,
            parse_msg=namespace.parse_msg,
        )

    if main_args.command_name == CommandNameEnum.HEX:
        hex_args = HexArgsInfo(
            component_name=namespace.component_name,
            hex_data=namespace.hex_data,
            read_from_clipboard=namespace.read_from_clipboard,
            find_msg_id=namespace.find_msg_id,
            no_envelop_msg_name=namespace.no_envelop_msg_name,
        )

    return CliArgsInfo(
        main_args=main_args,
        online_pcap_args=online_pcap_args,
        hex_args=hex_args,
    )
