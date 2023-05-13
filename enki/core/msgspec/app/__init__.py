"""The descriptions of all possible application messages."""

from . import baseapp, client, loginapp, cellapp, machine, logger, interfaces
from . import dbmgr, cellappmgr

SPEC_BY_ID_MAP = {
    'client':machine.SPEC_BY_ID,
    'machine':machine.SPEC_BY_ID,
    'dbmgr': dbmgr.SPEC_BY_ID,
    'interfaces': interfaces.SPEC_BY_ID,
    'logger': logger.SPEC_BY_ID,
    'cellappmgr': cellappmgr.SPEC_BY_ID,
}
