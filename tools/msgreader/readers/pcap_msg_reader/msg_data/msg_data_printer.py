"""Message data handling module for KBEngine messages."""

import logging
import sys
from abc import ABC, abstractmethod
from ipaddress import IPv4Address

from enki import msg_parser, msgspec
from enki.kbeenum import ComponentType
from enki.msg_parser.imsg_parser import IMsgParser
from enki.msg_parser.machine_msg_parser import (
    OnBroadcastInterfaceMsgParser,
    QueryComponentIDMsgParser,
)
from tools.msgreader.readers.deserializers import normalize_wireshark_data

from .msg_data import MsgData

logger = logging.getLogger(__package__)


class IMsgDataPrinter(ABC):
    """Interface for displaying KBEngine message data."""

    @abstractmethod
    def show_msg_data(self, msg_data: MsgData) -> None:
        """Display parsed message data."""


class MsgDataPrinter(IMsgDataPrinter):
    """Class for displaying KBEngine message data via logging."""

    def __init__(
        self, ignored_msgs: list[str], show_data: bool, parse_msg: bool
    ) -> None:
        """Initialize the printer with a list of messages to ignore.

        Args:
            ignored_msgs: List of message names to ignore during display.
                          These messages will be filtered out and not shown.
            show_data: флаг нужно ли отображать байты данных сообщения
            parse_msg: флаг нужно ли парсить данные сообщения

        """
        self._logger = self._setup_stdout_logger()
        self._ignored_msg_names = set(ignored_msgs)
        self._show_data = show_data
        self._parse_msg = parse_msg

    def _setup_stdout_logger(self) -> logging.Logger:
        """Set up a logger that outputs only to stdout.

        Returns:
            logging.Logger: Configured logger instance.

        """
        # Create a logger with a specific name
        logger = logging.getLogger("MsgDataPrinter.stdout")
        logger.setLevel(logging.INFO)

        # Clear any existing handlers
        logger.handlers = []

        # Create a handler for stdout
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.INFO)

        # Formatting - message only without extra information
        formatter = logging.Formatter("%(message)s")
        stdout_handler.setFormatter(formatter)

        # Add the handler
        logger.addHandler(stdout_handler)

        # Disable propagation to the root logger
        logger.propagate = False

        return logger

    def show_msg_data(self, msg_data: MsgData) -> None:
        """Display parsed message data.

        Args:
            msg_data: Message data to display.

        """
        # Use logger.info() to output to stdout
        if not msg_data.deserialize_msg_result.success:
            self._logger.info("Unparsed message (msg_data = %s)", msg_data)
            return

        msg = msg_data.deserialize_msg_result.result.msg
        assert msg is not None

        if msg.name in self._ignored_msg_names:
            # Filter out ignored messages
            return

        src_comp_str = msg_data.src_comp_type.name.capitalize()
        dst_comp_str = msg_data.dst_comp_type.name.capitalize()

        # Handle unknown destination components
        if (
            msg_data.dst_comp_type == ComponentType.UNKNOWN_COMPONENT
            and msg_data.net_chunk_data.dst == IPv4Address("255.255.255.255")
        ):
            dst_comp_str = str(msg_data.net_chunk_data.dst)

        host = f"{msg_data.host_comp_type.name.capitalize()}-{msg_data.component_id}"
        msg_dt = str(msg_data.net_chunk_data.time)

        transport_prot = "TCP" if msg_data.net_chunk_data.is_tcp else "UDP"

        data_str = ""
        if self._show_data:
            data = normalize_wireshark_data(msg_data.net_chunk_data.data)
            data_str = f"data = {data!r} "

        pd_str = ""
        if self._parse_msg:
            # Machine::onBroadcastInterface и Machine::queryComponentID могут
            # без оболочки отправлятся другим компонентам.
            if msg.name == msgspec.machine.queryComponentID.name:
                parser: type[IMsgParser] = QueryComponentIDMsgParser
            if msg.name == msgspec.machine.onBroadcastInterface.name:
                parser = OnBroadcastInterfaceMsgParser
            else:
                msg_descr = msgspec.get_comp_msg_specs(
                    msg_data.dst_comp_type
                ).msg_spec_by_id[msg.id]
                parser = msg_parser.get_msg_parser(
                    msg_descr.component_type, msg_descr
                )
            try:
                parser_result = parser().parse(msg)
                if parser_result.success:
                    pd = parser_result.result
                    assert pd is not None
                    pd_str = f"{pd.asdict()} "
            except Exception as err:
                logger.error(
                    "[%s] The message '%s' cannot be parsed (err = %s, parser = %s, msg_data = %s)",
                    self,
                    msg.name,
                    err,
                    parser(),
                    msg_data,
                )
                pd_str = "<The message is not parsed>"

        text = (
            f"*** [{msg_dt}] [{transport_prot}] {msg.name} "
            f"({src_comp_str} --> {dst_comp_str}). Host '{host}' {data_str}{pd_str}***"
        )
        self._logger.info(text)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"
