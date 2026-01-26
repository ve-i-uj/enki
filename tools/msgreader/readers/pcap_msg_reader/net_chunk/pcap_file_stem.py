"""Represents the stem of a pcap filename with KBEngine component information."""

import ipaddress
import logging
from ipaddress import IPv4Address

from enki.kbeenum import ComponentType

logger = logging.getLogger(__name__)


class PcapFileStem:
    """Represents the stem of a pcap filename with KBEngine component information.

    The filename stem should follow the format:
    '{component_name}-{component_id}-{host_ip_addr}' where component_name is
    a valid KBEngine component type, component_id is an integer,  and
    host_ip_addr is an IP address string.
    """

    def __init__(self, filename_stem: str) -> None:
        """Initialize PcapFileStem from a filename stem string.

        Args:
            filename_stem: Filename stem in format
                'component_name-component_id-host_ip_addr'

        Raises:
            ValueError: If the filename stem format is invalid or contains
                       invalid component information

        """
        assert self.validate(filename_stem), "Invalid file name"

        self._filename_stem = filename_stem

        parts = filename_stem.split("-")
        self._component_name = parts[0]
        self._component_id = int(parts[1])
        self._host_ip_addr = IPv4Address(parts[2])

    @property
    def filename_stem(self) -> str:
        return self._filename_stem

    @property
    def component_type(self) -> ComponentType:
        """Get the ComponentType enum value for this component."""
        return ComponentType.from_name(self._component_name.upper())

    @property
    def component_id(self) -> int:
        """Get the numeric identifier of this component instance."""
        return self._component_id

    @property
    def host_ip_addr(self) -> IPv4Address:
        """Get the IP address of the host."""
        return self._host_ip_addr

    @classmethod
    def validate(cls, filename_stem: str) -> bool:
        """Validate the filename stem.

        Args:
            filename_stem: The filename stem to validate

        Returns:
            Validation flag

        """
        # Check for required hyphen separators
        parts = filename_stem.split("-")

        if len(parts) < 3:
            logger.warning(
                "[%s] Filename stem '%s' must contain at least two hyphens. "
                "Expected format: '{component_name}-{component_id}-{host_ip_addr}'",
                cls.__name__,
                filename_stem,
            )
            return False

        # The last part is the IP address
        host_ip_addr = parts[-1]
        try:
            IPv4Address(ipaddress.ip_address(host_ip_addr))
        except ValueError as err:
            logger.warning(
                "[%s] Invalid ip v4 address in the file name (err = %s)",
                cls.__name__,
                err,
            )
            return False

        # The component ID is the second to last part
        component_id_str: str = parts[-2]
        if not component_id_str.isnumeric():
            logger.warning(
                "[%s] Component ID must be an integer, got: '%s'",
                cls.__name__,
                component_id_str,
            )
            return False

        # The component name is everything before the last two parts
        component_name = "-".join(parts[:-2])

        # Validate component name exists in ComponentType
        if not ComponentType.is_valid_name(component_name.upper()):
            valid_names = list(ComponentType.__members__.keys())
            logger.warning(
                "[%s] Invalid component name: '%s'. Valid component names are: %s",
                cls.__name__,
                component_name,
                valid_names,
            )
            return False

        logger.debug(
            "[%s] The filename stem '%s' is valid", cls.__name__, filename_stem
        )
        return True

    def __str__(self) -> str:
        """String representation in the original format."""
        return f"{self.__class__.__name__}('{self._filename_stem}')"

    __repr__ = __str__
