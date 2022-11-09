"""ClientApp messages."""

from enki.net.kbeclient.message import MsgDescr

from ._generated import *
from ._client import *

# # We need to override the generated app messages. But SPEC_BY_ID must be
# # the intersection of the generated SPEC_BY_ID and the predefined one.
# SPEC_BY_ID: dict[int, MsgDescr] = {}
# if hasattr(_generated, 'SPEC_BY_ID'):
#     # "_generated" can be empty while code generation
#     SPEC_BY_ID.update(_generated.SPEC_BY_ID)
# SPEC_BY_ID.update(_client.SPEC_BY_ID)
