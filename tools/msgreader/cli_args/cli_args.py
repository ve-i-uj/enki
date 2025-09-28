"""Файл получающий настройки для запуска скрипта."""

from __future__ import annotations

from argparse import ArgumentParser, _SubParsersAction

from .args_types import (
    CliArgsInfo,
    CommandNameEnum,
    HexArgsInfo,
    LogLevel,
    MainArgsInfo,
    StreamArgsInfo,
)


def _get_main_parser() -> ArgumentParser:
    """Возвращает главный парсер."""
    assert __package__ is not None
    parser = ArgumentParser(
        prog=__package__.split(".")[0],
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


def _add_stream_subparser(subparsers: _SubParsersAction) -> ArgumentParser:
    """Добавить команду-парсер к основному парсеру."""
    subparser = subparsers.add_parser("stream", help="the stream reader")

    subparser.add_argument(
        "--component-name-by-ip-file",
        type=str,
        required=True,
        dest="component_name_by_ip_file",
        help="the file contained the KBEngine component name by ip mapping",
    )
    subparser.add_argument(
        "--pcap-files-directory",
        type=str,
        required=True,
        dest="pcap_files_directory",
        help="the directory contained pcap files",
    )
    subparser.add_argument(
        "--out-file",
        type=str,
        required=False,
        dest="out_file",
        help="the output file",
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
    _add_stream_subparser(subparsers)
    _add_hex_subparser(subparsers)

    namespace = main_parser.parse_args()

    command_name = CommandNameEnum(namespace.command_name)

    main_args = MainArgsInfo(
        command_name=command_name,
        log_level=LogLevel(namespace.log_level),
        show_msg_fields=namespace.show_msg_fields,
    )

    stream_args = None
    hex_args = None

    if main_args.command_name == CommandNameEnum.STREAM:
        stream_args = StreamArgsInfo(
            component_name_by_ip_file=namespace.component_name_by_ip_file,
            pcap_files_directory=namespace.pcap_files_directory,
            out_file=namespace.out_file,
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
        stream_args=stream_args,
        hex_args=hex_args,
    )
