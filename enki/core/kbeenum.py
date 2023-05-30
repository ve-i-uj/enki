"""Enums of KBEngine."""

from __future__ import annotations

import enum


class DistributionFlag(enum.Enum):
    UNKNOWN = 0x00000000
    CELL_PUBLIC = 0x00000001
    CELL_PRIVATE = 0x00000002
    ALL_CLIENTS = 0x00000004
    CELL_PUBLIC_AND_OWN = 0x00000008
    OWN_CLIENT = 0x00000010
    BASE_AND_CLIENT = 0x00000020
    BASE = 0x00000040
    OTHER_CLIENTS = 0x00000080

    COMPONENT_1 = 253
    COMPONENT_2 = 97
    COMPONENT_3 = 157

    @classmethod
    def get_set_method_flags(cls) -> list[DistributionFlag]:
        return [cls.ALL_CLIENTS, cls.OTHER_CLIENTS, cls.OWN_CLIENT]


class ServerError(enum.Enum):
    """Server errors are mainly used by the server back to the client.

    See kbe/src/lib/server/server_errors.h
    """
    SUCCESS = 0  # Success.
    SRV_NO_READY = 1  # The server is not ready.
    SRV_OVERLOAD = 2  # he server load is too heavy.
    ILLEGAL_LOGIN = 3  # Illegal login.
    NAME_PASSWORD = 4  # The username or password is incorrect.
    NAME = 5  # The username is incorrect.
    PASSWORD = 6  # The password is incorrect.
    ACCOUNT_CREATE_FAILED = 7  # Failed to create account.
    # The operation is too busy (for example, the account was created N times in a row when the previous request of the server was not completed).
    BUSY = 8
    ACCOUNT_LOGIN_ANOTHER = 9  # The current account is logged in another place.
    ACCOUNT_IS_ONLINE = 10  # You have already logged in, and the server refuses to log in again.
    PROXY_DESTROYED = 11  # The proxy associated with the client has been destroyed on the server.
    ENTITYDEFS_NOT_MATCH = 12  # entityDefs does not match.
    IN_SHUTTINGDOWN = 13  # The server is shutting down
    NAME_MAIL = 14  # The email address is wrong.
    ACCOUNT_LOCK = 15  # The account is frozen.
    ACCOUNT_DEADLINE = 16  # The account has expired.
    ACCOUNT_NOT_ACTIVATED = 17  # The account is not activated.
    VERSION_NOT_MATCH = 18  # Does not match the version of the server.
    OP_FAILED = 19  # The operation failed.
    SRV_STARTING = 20  # The server is starting.
    ACCOUNT_REGISTER_NOT_AVAILABLE = 21  # The account registration function is not open.
    CANNOT_USE_MAIL = 22  # Email address cannot be used.
    NOT_FOUND_ACCOUNT = 23  # This account cannot be found.
    DB = 24  # Database error (please check dbmgr log and DB).
    USER1 = 25  # User-defined error code 1
    USER2 = 26  # User-defined error code 2
    USER3 = 27  # User-defined error code 3
    USER4 = 28  # User-defined error code 4
    USER5 = 29  # User-defined error code 5
    USER6 = 30  # User-defined error code 6
    USER7 = 31  # User-defined error code 7
    USER8 = 32  # User-defined error code 8
    USER9 = 33  # User-defined error code 9
    USER10 = 34  # User-defined error code 10
    LOCAL_PROCESSING = 35  # Local processing, usually because something is not processed by a third party but by the KBE server
    ACCOUNT_RESET_PASSWORD_NOT_AVAILABLE = 36  # The account reset password function is not open.
    ACCOUNT_LOGIN_ANOTHER_SERVER = 37  # The current account is logged in on another server
    MAX = 38  # Please put this one at the end of all errors. This is not an error indicator in itself, but only indicates how many error definitions there are in total


class ClientType(enum.Enum):
    """Type of client.

    See COMPONENT_CLIENT_TYPE (kbe/src/lib/common/common.h)
    """
    UNKNOWN = 0
    MOBILE = 1      # Mobile, Phone, Pad
    WIN = 2         # Windows
    LINUX = 3       # Linux    MAC = 4         # Mac
    BROWSER = 5     # Web, HTML5, Flash
    BOTS = 6        # bots
    MINI = 7        # ???
    END = 8


class PropertyUType(enum.Enum):
    """Type of dimension data.

    See ENTITY_BASE_PROPERTY_ALIASID (kbe/src/lib/entitydef/common.h)
    """
    # TODO: [25.04.2021 13:56 burov_alexey@mail.ru]
    # Перевести.
    # Из-за того, что у меня все свойства UINT16 (т.е. оптимизация отключена
    # через <aliasEntityID> false </aliasEntityID>), у этих свойств id беруться
    # из messages_fixed_defaults.xml
    #
    POSITION_XYZ = 40000
    DIRECTION_ROLL_PITCH_YAW = 40001
    SPACE_ID = 40002


class DataDownloadType(enum.Enum):
    STREAM_FILE = 1
    STREAM_STRING = 2


class MsgArgsType(enum.IntEnum):
    """Fixed or variable length of message (see MESSAGE_ARGS_TYPE)"""
    VARIABLE = -1
    FIXED = 0


class ComponentType(enum.IntEnum):
    UNKNOWN_COMPONENT = 0
    DBMGR = 1
    LOGINAPP = 2
    BASEAPPMGR = 3
    CELLAPPMGR = 4
    CELLAPP = 5
    BASEAPP = 6
    CLIENT = 7
    MACHINE = 8
    CONSOLE = 9
    LOGGER = 10
    BOTS = 11
    WATCHER = 12
    INTERFACES = 13
    TOOL = 14
    COMPONENT_END = 15

    def is_multiple_type(self) -> bool:
        # if self in [self.CELLAPP, self.BASEAPP, self.LOGINAPP]:
        # Пока тогда буду считать, что Loginapp один. Т.к. его адрес указывается
        # во внешний мир и пока не очень понятно, как их может быть несколько.
        if self in [self.CELLAPP, self.BASEAPP]:
            return True
        return False


class ShutdownState(enum.IntEnum):
	# enum SHUTDOWN_STATE
	# {
	# 	SHUTDOWN_STATE_STOP = COMPONENT_STATE_RUN,
	# 	SHUTDOWN_STATE_BEGIN = COMPONENT_STATE_SHUTTINGDOWN_BEGIN,
	# 	SHUTDOWN_STATE_RUNNING = COMPONENT_STATE_SHUTTINGDOWN_RUNNING,
	# 	SHUTDOWN_STATE_END = COMPONENT_STATE_STOP
	# };
    STOP = 1
    BEGIN = 2
    RUNNING = 3
    END = 4


class ComponentState(enum.IntEnum):
	INIT = 0
	RUN = 1
	SHUTTINGDOWN_BEGIN = 2
	SHUTTINGDOWN_RUNNING = 3
	STOP = 4


