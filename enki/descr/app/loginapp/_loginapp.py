"""Messages of LoginApp"""

from enki import kbetype, dcdescr

# The "importClientMessages" response contains wrong message description of
# the "hello". I override the description here.
hello = dcdescr.MessageDescr(
    id=4,
    lenght=-1,
    name='Loginapp::hello',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.STRING,     # for what version of kbe client the plugin is
        kbetype.STRING,     # for what version of server scripts the plugin is
        kbetype.BLOB,       # encrypted key
    ),
    desc='hello'
)

# These is the real description of the "login" message.
# The "importClientMessages" response has wrong one.
login = dcdescr.MessageDescr(
    id=3,
    lenght=-1,
    name='Loginapp::login',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=(
        kbetype.INT8,       # client type (see ClientType)
        kbetype.BLOB,       # binary data for "onRequestLogin" callback of script layer
        kbetype.STRING,     # account name
        kbetype.STRING,     # password
        kbetype.STRING,     # force login for "bots" client type (not empty value is true)
    ),
    desc='The client requests to log in to the loginapp process of the server. After receiving the request, the process will return a gateway address after verification.'  # noqa
)

importClientMessages = dcdescr.MessageDescr(
    id=5,
    lenght=0,
    name='Loginapp::importClientMessages',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=tuple(),
    desc='The client requests to import the message protocol.'
)

importServerErrorsDescr = dcdescr.MessageDescr(
    id=8,
    lenght=0,
    name='Loginapp::importServerErrorsDescr',
    args_type=dcdescr.MsgArgsType.FIXED,
    field_types=tuple(),
    desc=''
)

__all__ = ('hello', 'login', 'importClientMessages', 'importServerErrorsDescr')
