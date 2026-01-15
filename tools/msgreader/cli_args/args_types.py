"""Типы, которые получаются после чтения аргументов CLI."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LogLevel(Enum):
    """Внутренее представление уровней логирования."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CommandNameEnum(Enum):
    """Имена доступных команд."""

    PCAP = "pcap"
    HEX = "hex"


@dataclass
class MainArgsInfo:
    """Основные настройки независимо от подпарсера."""

    # Какая подкоманда сработала
    command_name: CommandNameEnum
    # Аргумент основного парсера
    log_level: LogLevel
    show_msg_fields: bool


@dataclass
class OnlinePcapArgsInfo:
    """Настройки для чтения сообщений из стрима (потока данных online)."""

    component_name_by_ip_file: str
    pcap_files_directory: str
    ignored_msgs: list[str]


@dataclass
class HexArgsInfo:
    """Настройки для чтения *одного* сообщения из 16-ричного байтового представления."""  # noqa: E501

    component_name: str
    hex_data: str
    read_from_clipboard: bool
    find_msg_id: bool
    no_envelop_msg_name: str | None


@dataclass
class CliArgsInfo:
    """Настройки необходимые для выполнения, полученные из командной строки."""

    main_args: MainArgsInfo
    online_pcap_args: OnlinePcapArgsInfo | None
    hex_args: HexArgsInfo | None
