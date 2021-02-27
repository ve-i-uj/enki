"""Enums of KBEngine."""

import enum


class ServerError(enum.Enum):
    """Server errors are mainly used by the server back to the client.

    See kbe/src/lib/server/server_errors.h
    """
    SERVER_SUCCESS = 0  # Success.
    SERVER_ERR_SRV_NO_READY = 1  # The server is not ready.
    SERVER_ERR_SRV_OVERLOAD = 2  # he server load is too heavy.
    SERVER_ERR_ILLEGAL_LOGIN = 3  # Illegal login.
    SERVER_ERR_NAME_PASSWORD = 4  # The username or password is incorrect.
    SERVER_ERR_NAME = 5  # The username is incorrect.
    SERVER_ERR_PASSWORD = 6  # The password is incorrect.
    SERVER_ERR_ACCOUNT_CREATE_FAILED = 7  # Failed to create account.
    SERVER_ERR_BUSY = 8  # The operation is too busy (for example, the account was created N times in a row when the previous request of the server was not completed).
    SERVER_ERR_ACCOUNT_LOGIN_ANOTHER = 9  # The current account is logged in another place.
    SERVER_ERR_ACCOUNT_IS_ONLINE = 10  # You have already logged in, and the server refuses to log in again.
    SERVER_ERR_PROXY_DESTROYED = 11  # The proxy associated with the client has been destroyed on the server.
    SERVER_ERR_ENTITYDEFS_NOT_MATCH = 12  # entityDefs does not match.
    SERVER_ERR_IN_SHUTTINGDOWN = 13  # The server is shutting down
    SERVER_ERR_NAME_MAIL = 14  # The email address is wrong.
    SERVER_ERR_ACCOUNT_LOCK = 15  # The account is frozen.
    SERVER_ERR_ACCOUNT_DEADLINE = 16  # The account has expired.
    SERVER_ERR_ACCOUNT_NOT_ACTIVATED = 17  # The account is not activated.
    SERVER_ERR_VERSION_NOT_MATCH = 18  # Does not match the version of the server.
    SERVER_ERR_OP_FAILED = 19  # The operation failed.
    SERVER_ERR_SRV_STARTING = 20  # The server is starting.
    SERVER_ERR_ACCOUNT_REGISTER_NOT_AVAILABLE = 21  # The account registration function is not open.
    SERVER_ERR_CANNOT_USE_MAIL = 22  # Email address cannot be used.
    SERVER_ERR_NOT_FOUND_ACCOUNT = 23  # This account cannot be found.
    SERVER_ERR_DB = 24  # Database error (please check dbmgr log and DB).
    SERVER_ERR_USER1 = 25  # User-defined error code 1
    SERVER_ERR_USER2 = 26  # User-defined error code 2
    SERVER_ERR_USER3 = 27  # User-defined error code 3
    SERVER_ERR_USER4 = 28  # User-defined error code 4
    SERVER_ERR_USER5 = 29  # User-defined error code 5
    SERVER_ERR_USER6 = 30  # User-defined error code 6
    SERVER_ERR_USER7 = 31  # User-defined error code 7
    SERVER_ERR_USER8 = 32  # User-defined error code 8
    SERVER_ERR_USER9 = 33  # User-defined error code 9
    SERVER_ERR_USER10 = 34  # User-defined error code 10
    SERVER_ERR_LOCAL_PROCESSING = 35  # Local processing, usually because something is not processed by a third party but by the KBE server
    SERVER_ERR_ACCOUNT_RESET_PASSWORD_NOT_AVAILABLE = 36  # The account reset password function is not open.
    SERVER_ERR_ACCOUNT_LOGIN_ANOTHER_SERVER = 37  # The current account is logged in on another server
    SERVER_ERR_MAX = 38  # Please put this one at the end of all errors. This is not an error indicator in itself, but only indicates how many error definitions there are in total
