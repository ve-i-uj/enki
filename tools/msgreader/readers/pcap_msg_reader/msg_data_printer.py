"""Message data handling module for KBEngine messages."""

import logging
import sys
from abc import ABC, abstractmethod

from enki.kbeenum import ComponentType

from .msg_data import MsgData


class IMsgDataPrinter(ABC):
    """Interface for displaying KBEngine message data."""

    @abstractmethod
    def show_msg_data(self, msg_data: MsgData) -> None:
        """Display parsed message data."""


class MsgDataPrinter(IMsgDataPrinter):
    """Class for displaying KBEngine message data via logging."""

    def __init__(self, ignored_msgs: list[str]) -> None:
        """Initialize the printer with a list of messages to ignore.

        Args:
            ignored_msgs: List of message names to ignore during display.
                          These messages will be filtered out and not shown.

        """
        self._logger = self._setup_stdout_logger()
        self._ignored_msg_names = set(ignored_msgs)

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

        src_comp = msg_data.src_comp_type.name.capitalize()
        dst_comp = msg_data.dst_comp_type.name.capitalize()

        # Handle unknown destination components
        if msg_data.dst_comp_type == ComponentType.UNKNOWN_COMPONENT:
            dst_comp = str(msg_data.net_chunk_data.dst)

        host = f"{msg_data.host_comp_type.name.capitalize()}-{msg_data.component_id}"
        msg_dt = str(msg_data.net_chunk_data.time)

        text = f"*** [{msg_dt}] {msg.name} ({src_comp} --> {dst_comp}). Host '{host}' ***"
        self._logger.info(text)
