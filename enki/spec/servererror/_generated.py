"""Server errors."""

from . import _servererror

SUCCESS = _servererror.ServerErrorSpec(
    id=0,
    name='SUCCESS',
    desc='成功。'
)

SERVER_ERR_SRV_NO_READY = _servererror.ServerErrorSpec(
    id=1,
    name='SERVER_ERR_SRV_NO_READY',
    desc='服务器没有准备好。'
)

SERVER_ERR_SRV_OVERLOAD = _servererror.ServerErrorSpec(
    id=2,
    name='SERVER_ERR_SRV_OVERLOAD',
    desc='服务器负载过重。'
)

SERVER_ERR_ILLEGAL_LOGIN = _servererror.ServerErrorSpec(
    id=3,
    name='SERVER_ERR_ILLEGAL_LOGIN',
    desc='非法登录。'
)

SERVER_ERR_NAME_PASSWORD = _servererror.ServerErrorSpec(
    id=4,
    name='SERVER_ERR_NAME_PASSWORD',
    desc='用户名或者密码不正确。'
)

SERVER_ERR_NAME = _servererror.ServerErrorSpec(
    id=5,
    name='SERVER_ERR_NAME',
    desc='用户名不正确。'
)

SERVER_ERR_PASSWORD = _servererror.ServerErrorSpec(
    id=6,
    name='SERVER_ERR_PASSWORD',
    desc='密码不正确。'
)

SERVER_ERR_ACCOUNT_CREATE_FAILED = _servererror.ServerErrorSpec(
    id=7,
    name='SERVER_ERR_ACCOUNT_CREATE_FAILED',
    desc='创建账号失败。'
)

SERVER_ERR_BUSY = _servererror.ServerErrorSpec(
    id=8,
    name='SERVER_ERR_BUSY',
    desc='操作过于繁忙(例如：在服务器前一次请求未执行完毕的情况下连续N次创建账号)。'
)

SERVER_ERR_ACCOUNT_LOGIN_ANOTHER = _servererror.ServerErrorSpec(
    id=9,
    name='SERVER_ERR_ACCOUNT_LOGIN_ANOTHER',
    desc='当前账号在另一处登录了。'
)

SERVER_ERR_ACCOUNT_IS_ONLINE = _servererror.ServerErrorSpec(
    id=10,
    name='SERVER_ERR_ACCOUNT_IS_ONLINE',
    desc='账号已登陆。'
)

SERVER_ERR_PROXY_DESTROYED = _servererror.ServerErrorSpec(
    id=11,
    name='SERVER_ERR_PROXY_DESTROYED',
    desc='与客户端关联的proxy在服务器上已经销毁。'
)

SERVER_ERR_ENTITYDEFS_NOT_MATCH = _servererror.ServerErrorSpec(
    id=12,
    name='SERVER_ERR_ENTITYDEFS_NOT_MATCH',
    desc='EntityDefs不匹配。'
)

SERVER_ERR_SERVER_IN_SHUTTINGDOWN = _servererror.ServerErrorSpec(
    id=13,
    name='SERVER_ERR_SERVER_IN_SHUTTINGDOWN',
    desc='服务器正在关闭中。'
)

SERVER_ERR_NAME_MAIL = _servererror.ServerErrorSpec(
    id=14,
    name='SERVER_ERR_NAME_MAIL',
    desc='Email地址错误。'
)

SERVER_ERR_ACCOUNT_LOCK = _servererror.ServerErrorSpec(
    id=15,
    name='SERVER_ERR_ACCOUNT_LOCK',
    desc='账号被冻结。'
)

SERVER_ERR_ACCOUNT_DEADLINE = _servererror.ServerErrorSpec(
    id=16,
    name='SERVER_ERR_ACCOUNT_DEADLINE',
    desc='账号已过期。'
)

SERVER_ERR_ACCOUNT_NOT_ACTIVATED = _servererror.ServerErrorSpec(
    id=17,
    name='SERVER_ERR_ACCOUNT_NOT_ACTIVATED',
    desc='账号未激活。'
)

SERVER_ERR_VERSION_NOT_MATCH = _servererror.ServerErrorSpec(
    id=18,
    name='SERVER_ERR_VERSION_NOT_MATCH',
    desc='与服务端的版本不匹配。'
)

SERVER_ERR_OP_FAILED = _servererror.ServerErrorSpec(
    id=19,
    name='SERVER_ERR_OP_FAILED',
    desc='操作失败。'
)

SERVER_ERR_SRV_STARTING = _servererror.ServerErrorSpec(
    id=20,
    name='SERVER_ERR_SRV_STARTING',
    desc='服务器正在启动中。'
)

SERVER_ERR_ACCOUNT_REGISTER_NOT_AVAILABLE = _servererror.ServerErrorSpec(
    id=21,
    name='SERVER_ERR_ACCOUNT_REGISTER_NOT_AVAILABLE',
    desc='未开放账号注册功能。'
)

SERVER_ERR_CANNOT_USE_MAIL = _servererror.ServerErrorSpec(
    id=22,
    name='SERVER_ERR_CANNOT_USE_MAIL',
    desc='不能使用email地址。'
)

SERVER_ERR_NOT_FOUND_ACCOUNT = _servererror.ServerErrorSpec(
    id=23,
    name='SERVER_ERR_NOT_FOUND_ACCOUNT',
    desc='找不到此账号。'
)

SERVER_ERR_DB = _servererror.ServerErrorSpec(
    id=24,
    name='SERVER_ERR_DB',
    desc='数据库错误(请检查dbmgr日志和DB)。'
)

SERVER_ERR_USER1 = _servererror.ServerErrorSpec(
    id=25,
    name='SERVER_ERR_USER1',
    desc='用户自定义错误码1。'
)

SERVER_ERR_USER2 = _servererror.ServerErrorSpec(
    id=26,
    name='SERVER_ERR_USER2',
    desc='用户自定义错误码2。'
)

SERVER_ERR_USER3 = _servererror.ServerErrorSpec(
    id=27,
    name='SERVER_ERR_USER3',
    desc='用户自定义错误码3。'
)

SERVER_ERR_USER4 = _servererror.ServerErrorSpec(
    id=28,
    name='SERVER_ERR_USER4',
    desc='用户自定义错误码4。'
)

SERVER_ERR_USER5 = _servererror.ServerErrorSpec(
    id=29,
    name='SERVER_ERR_USER5',
    desc='用户自定义错误码5。'
)

SERVER_ERR_USER6 = _servererror.ServerErrorSpec(
    id=30,
    name='SERVER_ERR_USER6',
    desc='用户自定义错误码6。'
)

SERVER_ERR_USER7 = _servererror.ServerErrorSpec(
    id=31,
    name='SERVER_ERR_USER7',
    desc='用户自定义错误码7。'
)

SERVER_ERR_USER8 = _servererror.ServerErrorSpec(
    id=32,
    name='SERVER_ERR_USER8',
    desc='用户自定义错误码8。'
)

SERVER_ERR_USER9 = _servererror.ServerErrorSpec(
    id=33,
    name='SERVER_ERR_USER9',
    desc='用户自定义错误码9。'
)

SERVER_ERR_USER10 = _servererror.ServerErrorSpec(
    id=34,
    name='SERVER_ERR_USER10',
    desc='用户自定义错误码10。'
)

SERVER_ERR_LOCAL_PROCESSING = _servererror.ServerErrorSpec(
    id=35,
    name='SERVER_ERR_LOCAL_PROCESSING',
    desc='本地处理，通常为某件事情不由第三方处理而是由KBE服务器处理。'
)

SERVER_ERR_ACCOUNT_RESET_PASSWORD_NOT_AVAILABLE = _servererror.ServerErrorSpec(
    id=36,
    name='SERVER_ERR_ACCOUNT_RESET_PASSWORD_NOT_AVAILABLE',
    desc='未开放账号重置密码功能。'
)

SERVER_ERR_ACCOUNT_LOGIN_ANOTHER_SERVER = _servererror.ServerErrorSpec(
    id=37,
    name='SERVER_ERR_ACCOUNT_LOGIN_ANOTHER_SERVER',
    desc='当前账号在其他服务器登陆了。'
)

ERROR_BY_ID = {
    0: SUCCESS,
    1: SERVER_ERR_SRV_NO_READY,
    2: SERVER_ERR_SRV_OVERLOAD,
    3: SERVER_ERR_ILLEGAL_LOGIN,
    4: SERVER_ERR_NAME_PASSWORD,
    5: SERVER_ERR_NAME,
    6: SERVER_ERR_PASSWORD,
    7: SERVER_ERR_ACCOUNT_CREATE_FAILED,
    8: SERVER_ERR_BUSY,
    9: SERVER_ERR_ACCOUNT_LOGIN_ANOTHER,
    10: SERVER_ERR_ACCOUNT_IS_ONLINE,
    11: SERVER_ERR_PROXY_DESTROYED,
    12: SERVER_ERR_ENTITYDEFS_NOT_MATCH,
    13: SERVER_ERR_SERVER_IN_SHUTTINGDOWN,
    14: SERVER_ERR_NAME_MAIL,
    15: SERVER_ERR_ACCOUNT_LOCK,
    16: SERVER_ERR_ACCOUNT_DEADLINE,
    17: SERVER_ERR_ACCOUNT_NOT_ACTIVATED,
    18: SERVER_ERR_VERSION_NOT_MATCH,
    19: SERVER_ERR_OP_FAILED,
    20: SERVER_ERR_SRV_STARTING,
    21: SERVER_ERR_ACCOUNT_REGISTER_NOT_AVAILABLE,
    22: SERVER_ERR_CANNOT_USE_MAIL,
    23: SERVER_ERR_NOT_FOUND_ACCOUNT,
    24: SERVER_ERR_DB,
    25: SERVER_ERR_USER1,
    26: SERVER_ERR_USER2,
    27: SERVER_ERR_USER3,
    28: SERVER_ERR_USER4,
    29: SERVER_ERR_USER5,
    30: SERVER_ERR_USER6,
    31: SERVER_ERR_USER7,
    32: SERVER_ERR_USER8,
    33: SERVER_ERR_USER9,
    34: SERVER_ERR_USER10,
    35: SERVER_ERR_LOCAL_PROCESSING,
    36: SERVER_ERR_ACCOUNT_RESET_PASSWORD_NOT_AVAILABLE,
    37: SERVER_ERR_ACCOUNT_LOGIN_ANOTHER_SERVER
}

__all__ = (
    'SUCCESS', 'SERVER_ERR_SRV_NO_READY',
    'SERVER_ERR_SRV_OVERLOAD', 'SERVER_ERR_ILLEGAL_LOGIN',
    'SERVER_ERR_NAME_PASSWORD', 'SERVER_ERR_NAME',
    'SERVER_ERR_PASSWORD', 'SERVER_ERR_ACCOUNT_CREATE_FAILED',
    'SERVER_ERR_BUSY', 'SERVER_ERR_ACCOUNT_LOGIN_ANOTHER',
    'SERVER_ERR_ACCOUNT_IS_ONLINE', 'SERVER_ERR_PROXY_DESTROYED',
    'SERVER_ERR_ENTITYDEFS_NOT_MATCH', 'SERVER_ERR_SERVER_IN_SHUTTINGDOWN',
    'SERVER_ERR_NAME_MAIL', 'SERVER_ERR_ACCOUNT_LOCK',
    'SERVER_ERR_ACCOUNT_DEADLINE', 'SERVER_ERR_ACCOUNT_NOT_ACTIVATED',
    'SERVER_ERR_VERSION_NOT_MATCH', 'SERVER_ERR_OP_FAILED',
    'SERVER_ERR_SRV_STARTING', 'SERVER_ERR_ACCOUNT_REGISTER_NOT_AVAILABLE',
    'SERVER_ERR_CANNOT_USE_MAIL', 'SERVER_ERR_NOT_FOUND_ACCOUNT',
    'SERVER_ERR_DB', 'SERVER_ERR_USER1',
    'SERVER_ERR_USER2', 'SERVER_ERR_USER3',
    'SERVER_ERR_USER4', 'SERVER_ERR_USER5',
    'SERVER_ERR_USER6', 'SERVER_ERR_USER7',
    'SERVER_ERR_USER8', 'SERVER_ERR_USER9',
    'SERVER_ERR_USER10', 'SERVER_ERR_LOCAL_PROCESSING',
    'SERVER_ERR_ACCOUNT_RESET_PASSWORD_NOT_AVAILABLE', 'SERVER_ERR_ACCOUNT_LOGIN_ANOTHER_SERVER',
    'ERROR_BY_ID'
)
