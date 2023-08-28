"""LoginApp messages."""

from enki.core.message import MsgDescr as _MsgDescr

from ._generated import *
from ._loginapp import *

SPEC_BY_ID: dict[int, _MsgDescr] = {}
SPEC_BY_ID.update(_generated.SPEC_BY_ID)
SPEC_BY_ID.update(_loginapp.SPEC_BY_ID)
