"""Server errors."""

from enki import servererror

SUCCESS = servererror.ServerErrorSpec(
    id=0,
    name='SUCCESS',
    desc='成功。'
)

SERVER_ERR_SRV_NO_READY = servererror.ServerErrorSpec(
    id=1,
    name='SERVER_ERR_SRV_NO_READY',
    desc='服务器没有准备好。'
)

SERVER_ERR_SRV_OVERLOAD = servererror.ServerErrorSpec(
    id=2,
    name='SERVER_ERR_SRV_OVERLOAD',
    desc='服务器负载过重。'
)

SERVER_ERR_ILLEGAL_LOGIN = servererror.ServerErrorSpec(
    id=3,
    name='SERVER_ERR_ILLEGAL_LOGIN',
    desc='非法登录。'
)

SERVER_ERR_NAME_PASSWORD = servererror.ServerErrorSpec(
    id=4,
    name='SERVER_ERR_NAME_PASSWORD',
    desc='用户名或者密码不正确。'
)

SERVER_ERR_NAME = servererror.ServerErrorSpec(
    id=5,
    name='SERVER_ERR_NAME',
    desc='用户名不正确。'
)

SERVER_ERR_PASSWORD = servererror.ServerErrorSpec(
    id=6,
    name='SERVER_ERR_PASSWORD',
    desc='密码不正确。'
)

SERVER_ERR_ACCOUNT_CREATE_FAILED = servererror.ServerErrorSpec(
    id=7,
    name='SERVER_ERR_ACCOUNT_CREATE_FAILED',
    desc='创建账号失败。'
)

SERVER_ERR_BUSY = servererror.ServerErrorSpec(
    id=8,
    name='SERVER_ERR_BUSY',
    desc='操作过于繁忙(例如：在服务器前一次请求未执行完毕的情况下连续N次创建账号)。'
)

SERVER_ERR_ACCOUNT_LOGIN_ANOTHER = servererror.ServerErrorSpec(
    id=9,
    name='SERVER_ERR_ACCOUNT_LOGIN_ANOTHER',
    desc='当前账号在另一处登录了。'
)

SERVER_ERR_ACCOUNT_IS_ONLINE = servererror.ServerErrorSpec(
    id=10,
    name='SERVER_ERR_ACCOUNT_IS_ONLINE',
    desc='账号已登陆。'
)

SERVER_ERR_PROXY_DESTROYED = servererror.ServerErrorSpec(
    id=11,
    name='SERVER_ERR_PROXY_DESTROYED',
    desc='与客户端关联的proxy在服务器上已经销毁。'
)

SERVER_ERR_ENTITYDEFS_NOT_MATCH = servererror.ServerErrorSpec(
    id=12,
    name='SERVER_ERR_ENTITYDEFS_NOT_MATCH',
    desc='EntityDefs不匹配。'
)

SERVER_ERR_SERVER_IN_SHUTTINGDOWN = servererror.ServerErrorSpec(
    id=13,
    name='SERVER_ERR_SERVER_IN_SHUTTINGDOWN',
    desc='服务器正在关闭中。'
)

SERVER_ERR_NAME_MAIL = servererror.ServerErrorSpec(
    id=14,
    name='SERVER_ERR_NAME_MAIL',
    desc='Email地址错误。'
)

SERVER_ERR_ACCOUNT_LOCK = servererror.ServerErrorSpec(
    id=15,
    name='SERVER_ERR_ACCOUNT_LOCK',
    desc='账号被冻结。'
)

SERVER_ERR_ACCOUNT_DEADLINE = servererror.ServerErrorSpec(
    id=16,
    name='SERVER_ERR_ACCOUNT_DEADLINE',
    desc='账号已过期。'
)

SERVER_ERR_ACCOUNT_NOT_ACTIVATED = servererror.ServerErrorSpec(
    id=17,
    name='SERVER_ERR_ACCOUNT_NOT_ACTIVATED',
    desc='账号未激活。'
)

SERVER_ERR_VERSION_NOT_MATCH = servererror.ServerErrorSpec(
    id=18,
    name='SERVER_ERR_VERSION_NOT_MATCH',
    desc='与服务端的版本不匹配。'
)

SERVER_ERR_OP_FAILED = servererror.ServerErrorSpec(
    id=19,
    name='SERVER_ERR_OP_FAILED',
    desc='操作失败。'
)

SERVER_ERR_SRV_STARTING = servererror.ServerErrorSpec(
    id=20,
    name='SERVER_ERR_SRV_STARTING',
    desc='服务器正在启动中。'
)

SERVER_ERR_ACCOUNT_REGISTER_NOT_AVAILABLE = servererror.ServerErrorSpec(
    id=21,
    name='SERVER_ERR_ACCOUNT_REGISTER_NOT_AVAILABLE',
    desc='未开放账号注册功能。'
)

SERVER_ERR_CANNOT_USE_MAIL = servererror.ServerErrorSpec(
    id=22,
    name='SERVER_ERR_CANNOT_USE_MAIL',
    desc='不能使用email地址。'
)

SERVER_ERR_NOT_FOUND_ACCOUNT = servererror.ServerErrorSpec(
    id=23,
    name='SERVER_ERR_NOT_FOUND_ACCOUNT',
    desc='找不到此账号。'
)

SERVER_ERR_DB = servererror.ServerErrorSpec(
    id=24,
    name='SERVER_ERR_DB',
    desc='数据库错误(请检查dbmgr日志和DB)。'
)

SERVER_ERR_USER1 = servererror.ServerErrorSpec(
    id=25,
    name='SERVER_ERR_USER1',
    desc='用户自定义错误码1。'
)

SERVER_ERR_USER2 = servererror.ServerErrorSpec(
    id=26,
    name='SERVER_ERR_USER2',
    desc='用户自定义错误码2。'
)

SERVER_ERR_USER3 = servererror.ServerErrorSpec(
    id=27,
    name='SERVER_ERR_USER3',
    desc='用户自定义错误码3。'
)

SERVER_ERR_USER4 = servererror.ServerErrorSpec(
    id=28,
    name='SERVER_ERR_USER4',
    desc='用户自定义错误码4。'
)

SERVER_ERR_USER5 = servererror.ServerErrorSpec(
    id=29,
    name='SERVER_ERR_USER5',
    desc='用户自定义错误码5。'
)

SERVER_ERR_USER6 = servererror.ServerErrorSpec(
    id=30,
    name='SERVER_ERR_USER6',
    desc='用户自定义错误码6。'
)

SERVER_ERR_USER7 = servererror.ServerErrorSpec(
    id=31,
    name='SERVER_ERR_USER7',
    desc='用户自定义错误码7。'
)

SERVER_ERR_USER8 = servererror.ServerErrorSpec(
    id=32,
    name='SERVER_ERR_USER8',
    desc='用户自定义错误码8。'
)

SERVER_ERR_USER9 = servererror.ServerErrorSpec(
    id=33,
    name='SERVER_ERR_USER9',
    desc='用户自定义错误码9。'
)

SERVER_ERR_USER10 = servererror.ServerErrorSpec(
    id=34,
    name='SERVER_ERR_USER10',
    desc='用户自定义错误码10。'
)

SERVER_ERR_LOCAL_PROCESSING = servererror.ServerErrorSpec(
    id=35,
    name='SERVER_ERR_LOCAL_PROCESSING',
    desc='本地处理，通常为某件事情不由第三方处理而是由KBE服务器处理。'
)

SERVER_ERR_ACCOUNT_RESET_PASSWORD_NOT_AVAILABLE = servererror.ServerErrorSpec(
    id=36,
    name='SERVER_ERR_ACCOUNT_RESET_PASSWORD_NOT_AVAILABLE',
    desc='未开放账号重置密码功能。'
)

SERVER_ERR_ACCOUNT_LOGIN_ANOTHER_SERVER = servererror.ServerErrorSpec(
    id=37,
    name='SERVER_ERR_ACCOUNT_LOGIN_ANOTHER_SERVER',
    desc='当前账号在其他服务器登陆了。'
)
