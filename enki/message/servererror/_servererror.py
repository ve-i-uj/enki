"""Description of server errors.

It's a representation of server files server_errors_defaults.xml / server_errors.xml
"""

import logging

from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ServerErrorSpec:
    id: int
    name: str
    desc: str
