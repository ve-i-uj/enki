"""Компонент частично повторяющий функционал KBEngine-компонента Loginapp."""

from __future__ import annotations

import abc
import asyncio
import logging
from asyncio import Future
from typing import TYPE_CHECKING, Generic, TypeAlias, TypeVar

from enki import msgspec
from enki.kbeenum import ComponentType, ServerError
from enki.kbetype import *
from enki.kbetype.pytypes.basic_data_types import KBEBlob, KBEString, KBEUInt16
from enki.misc import devonly
from enki.misc.result import Result
from enki.misc.startable import IStartable
from enki.msg.imsg import IMsgBackChannel, IServerMsgReceiver
from enki.msg.message import Message
from enki.msg.msg_server import (
    TCPMsgBackChannel,
    TCPMsgServer,
)
from enki.msg_parser.client_msg_parser import (
    OnHelloCBParsedMsgData,
    OnLoginFailedParsedMsgData,
    OnLoginSuccessfullyParsedMsgData,
    OnScriptVersionNotMatchParsedMsgData,
    OnVersionNotMatchParsedMsgData,
)
from enki.msg_parser.loginapp_msg_parser import (
    HelloMsgParser,
    ImportClientMessagesMsgParser,
    LoginMsgParser,
    OnClientActiveTickMsgParser,
    ReqAccountResetPasswordMsgParser,
    ReqCreateAccountMsgParser,
    ReqCreateMailAccountMsgParser,
)
from enki.msg_parser.machine_msg_parser import (
    OnBroadcastInterfaceParsedMsgData,
)
from enki.msgspec import (
    get_comp_msg_specs,
)

if TYPE_CHECKING:
    from enki.msg.msg_descr import (
        CompenentMsgSpecs,
        ComponentMsgSpecById,
    )
    from enki.net.addr import Addr

logger = logging.getLogger(__name__)

ComponentInfo: TypeAlias = OnBroadcastInterfaceParsedMsgData


class LoginappMock(IStartable, IServerMsgReceiver):
    """Компонент частично повторяющий функционал KBEngine-компонента Loginapp."""

    def __init__(
        self,
        tcp_addr: Addr,
        baseapp_tcp_add: Addr,
        kbe_version: str,
        assets_version: str,
        account_name: str,
        password: str,
        protocol_md5: str,
        entity_def_md5: str,
    ) -> None:
        """Конструктор KBEngine-компонента Loginapp.

        Args:
            tcp_addr (ComponentAddr): адрес приёма TCP-подключений

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        self._server_is_running: Future[None] | None = None

        self._tcp_addr = tcp_addr
        self._baseapp_tcp_add = baseapp_tcp_add

        msg_spec_by_id: ComponentMsgSpecById = get_comp_msg_specs(
            ComponentType.LOGINAPP
        )
        comp_msg_specs: CompenentMsgSpecs = {
            ComponentType.CLIENT: get_comp_msg_specs(ComponentType.CLIENT)
        }
        # Сервер для обслуживания соединений.
        self._tcp_server = TCPMsgServer(
            self._tcp_addr,
            msg_spec_by_id,
            msg_receiver=self,
            comp_msg_specs=comp_msg_specs,
        )
        # Обработчики сообщений
        self._handlers: dict[int, _LoginappHandler] = {
            msgspec.loginapp.hello.id: _LoginappHelloHandler(self),
            msgspec.loginapp.login.id: _LoginappLoginHandler(self),
            msgspec.loginapp.reqCreateAccount.id: _LoginappReqCreateAccountHandler(
                self
            ),
            msgspec.loginapp.reqCreateMailAccount.id: _LoginappReqCreateMailAccountHandler(  # noqa: E501
                self
            ),
            msgspec.loginapp.reqAccountResetPassword.id: _LoginappReqAccountResetPasswordHandler(  # добавить этот обработчик
                self
            ),
            msgspec.loginapp.onClientActiveTick.id: _LoginappOnClientActiveTickHandler(
                self
            ),
            msgspec.loginapp.importClientMessages.id: _ImportClientMessagesHandler(
                self
            ),
        }
        logger.info("[%s] Initialized", self)

        self._kbe_version = KBEString(kbe_version)
        self._assets_version = KBEString(assets_version)
        self._protocol_md5 = KBEString(protocol_md5)
        self._entity_def_md5 = KBEString(entity_def_md5)
        self._componentType = KBEComponentType(ComponentType.LOGINAPP.value)

        self._account_name = KBEString(account_name)
        self._password = KBEString(password)

    @property
    def account_name(self) -> str:
        """Получить версию ассетов."""
        return self._account_name

    @account_name.setter
    def account_name(self, value: KBEString) -> None:
        """Получить версию ассетов."""
        self._account_name = value

    @property
    def password(self) -> str:
        """Получить версию ассетов."""
        return self._password

    @password.setter
    def password(self, value: KBEString) -> None:
        """Получить версию ассетов."""
        self._password = value

    @property
    def baseapp_tcp_add(self) -> Addr:
        """Получить версию ассетов."""
        return self._baseapp_tcp_add

    @property
    def kbe_version(self) -> KBEString:
        """Получить версию ассетов."""
        return self._kbe_version

    @property
    def assets_version(self) -> KBEString:
        """Получить версию ассетов."""
        return self._assets_version

    @property
    def protocol_md5(self) -> KBEString:
        """Получить MD5 протокола."""
        return self._protocol_md5

    @protocol_md5.setter
    def protocol_md5(self, value: KBEString) -> None:
        """Установить MD5 протокола."""
        self._protocol_md5 = value

    @property
    def entity_def_md5(self) -> KBEString:
        """Получить MD5 определений сущностей."""
        return self._entity_def_md5

    @entity_def_md5.setter
    def entity_def_md5(self, value: KBEString) -> None:
        """Установить MD5 определений сущностей."""
        self._entity_def_md5 = value

    @property
    def componentType(self) -> KBEComponentType:
        """Получить тип компонента (только чтение)."""
        return self._componentType

    @property
    def tcp_addr(self) -> Addr:
        return self._tcp_addr

    async def wait_until_stop(self) -> None:
        """Ожидание, когда сервер завершит работу.

        Returns:
            Future: фюче-объект, показывающий работает ли серевер

        """
        if self._server_is_running is None:
            return

        await self._server_is_running

    async def start(self) -> Result:
        """Запустить компонент Супервизор.

        Returns:
            Result: результат запуска компонента

        """
        logger.debug("[%s] ", self)
        res = await self._tcp_server.start()
        if not res.success:
            return res

        # Переменная, что сервер запущен
        self._server_is_running = Future()

        logger.info("[%s] Started", self)
        return Result(success=True, result=None)

    def stop(self) -> None:
        """Остановить компонент."""
        if not self.is_started:
            return

        self._tcp_server.stop()

        if self._server_is_running is not None:
            self._server_is_running.set_result(None)

    @property
    def is_started(self) -> bool:
        """Флаг запущен ли Супервизор.

        Returns:
            bool: Флаг запущен ли Супервизор

        """
        return (
            self._server_is_running is not None and not self._server_is_running.done()
        )

    def on_receive_msg(self, msg: Message, back_channel: IMsgBackChannel) -> None:
        """Колбэк на полученное сообщение.

        Args:
            msg (Message): полученное сервером сообщение
            back_channel (IMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        handler = self._handlers.get(msg.id)
        if handler is None:
            logger.warning("[%s] There is no handler for the message %s", self, msg.id)
            return

        asyncio.create_task(handler.handle(msg, back_channel))  # noqa: RUF006

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"


_T_IMsgBackChannel = TypeVar("_T_IMsgBackChannel", bound=IMsgBackChannel)


class _LoginappHandler(abc.ABC, Generic[_T_IMsgBackChannel]):
    """Абстрактный класс для обработчика сообщения компонента Loginapp."""

    def __init__(self, app: LoginappMock) -> None:
        self._app = app

    @abc.abstractmethod
    async def handle(self, msg: Message, back_channel: _T_IMsgBackChannel) -> None:
        """Обработать сообщение."""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    __repr__ = __str__


class _LoginappHelloHandler(_LoginappHandler[TCPMsgBackChannel]):
    """Обработчик для сообщения Loginapp::hello.

    Используется для проверки живой компонент или нет.
    """

    async def handle(self, msg: Message, back_channel: TCPMsgBackChannel) -> None:
        """Обработать сообщение Loginapp::hello.

        Args:
            msg (Message): сообщение Loginapp::hello
            back_channel (TCPMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        res = HelloMsgParser().parse(msg)
        if not res.success:
            logger.warning(
                "[%s] The message '%s' is not parsed. Reason: '%s'",
                msg,
                self,
                res.text,
            )
            return

        req_pd = res.result
        assert req_pd is not None

        if req_pd.kbe_version != self._app.kbe_version:
            logger.debug(
                "[%s] KBE Version is not match (client version = %s, "
                "server version = %s)",
                self,
                req_pd.kbe_version,
                self._app.kbe_version,
            )
            version_not_match_pd = OnVersionNotMatchParsedMsgData(
                kbe_version=self._app.kbe_version
            )
            resp_msg = Message.create(
                msgspec.client.onVersionNotMatch,
                version_not_match_pd.get_values(),
            )
            await back_channel.send_msg(resp_msg)
            return

        if req_pd.script_version != self._app.assets_version:
            logger.debug(
                "[%s] Assets (scripts) version is not match (client version = %s, "
                "server version = %s)",
                self,
                req_pd.script_version,
                self._app.assets_version,
            )
            assets_version_not_match_pd = OnScriptVersionNotMatchParsedMsgData(
                assets_version=self._app.assets_version
            )
            resp_msg = Message.create(
                msgspec.client.onScriptVersionNotMatch,
                assets_version_not_match_pd.get_values(),
            )
            await back_channel.send_msg(resp_msg)
            return

        pd = OnHelloCBParsedMsgData(
            kbe_version=self._app.kbe_version,
            assets_version=self._app.assets_version,
            protocol_md5=self._app.protocol_md5,
            entity_def_md5=self._app.entity_def_md5,
            componentType=self._app.componentType,
        )
        resp_msg = Message.create(msgspec.client.onHelloCB, pd.get_values())
        await back_channel.send_msg(resp_msg)


class _LoginappLoginHandler(_LoginappHandler[TCPMsgBackChannel]):
    """Обработчик для сообщения Loginapp::login.

    Используется для проверки живой компонент или нет.
    """

    async def handle(self, msg: Message, back_channel: TCPMsgBackChannel) -> None:
        """Обработать сообщение Loginapp::login.

        Args:
            msg (Message): сообщение Loginapp::login
            back_channel (TCPMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        req_res = LoginMsgParser().parse(msg)
        if not req_res.success:
            logger.warning(
                "[%s] The message '%s' is not parsed. Reason: '%s'",
                msg,
                self,
                req_res.text,
            )
            return

        req_pd = req_res.result
        assert req_pd is not None

        if not req_pd.accountName:
            logger.debug(
                "[%s] Account name cannot be empty (client = %s)",
                self,
                back_channel.conn_info.client_addr,
            )
            err_resp_pd = OnLoginFailedParsedMsgData(
                retCode=KBEUInt16(ServerError.NAME.value),
                data=req_pd.clientData,
            )
            resp_msg = Message.create(
                msgspec.client.onLoginFailed, err_resp_pd.get_values()
            )
            await back_channel.send_msg(resp_msg)
            return

        if req_pd.accountName != self._app.account_name:
            logger.debug(
                "[%s] Invalid account name: '%s' (client = %s)",
                self,
                req_pd.accountName,
                back_channel.conn_info.client_addr,
            )
            err_resp_pd = OnLoginFailedParsedMsgData(
                retCode=KBEUInt16(
                    ServerError.NAME.value
                ),  # Используем существующую ошибку для неверного имени
                data=req_pd.clientData,
            )
            resp_msg = Message.create(
                msgspec.client.onLoginFailed, err_resp_pd.get_values()
            )
            await back_channel.send_msg(resp_msg)
            return

        if req_pd.password != self._app.password:
            logger.debug(
                "[%s] Invalid password for account '%s' (client = %s)",
                self,
                req_pd.accountName,
                back_channel.conn_info.client_addr,
            )
            err_resp_pd = OnLoginFailedParsedMsgData(
                retCode=KBEUInt16(
                    ServerError.PASSWORD.value
                ),  # Используем ошибку для неверного пароля
                data=req_pd.clientData,
            )
            resp_msg = Message.create(
                msgspec.client.onLoginFailed, err_resp_pd.get_values()
            )
            await back_channel.send_msg(resp_msg)
            return

        if req_pd.digest != self._app.entity_def_md5:
            logger.debug(
                "[%s] Entity definition MD5 mismatch. Client: %s, Server: %s (client = %s)",
                self,
                req_pd.digest,
                self._app.entity_def_md5,
                back_channel.conn_info.client_addr,
            )
            err_resp_pd = OnLoginFailedParsedMsgData(
                retCode=KBEUInt16(ServerError.ENTITYDEFS_NOT_MATCH.value),
                data=req_pd.clientData,
            )
            resp_msg = Message.create(
                msgspec.client.onLoginFailed, err_resp_pd.get_values()
            )
            await back_channel.send_msg(resp_msg)
            return

        pd = OnLoginSuccessfullyParsedMsgData(
            account_name=KBEString("1"),
            host=KBEString("0.0.0.0"),
            tcpPort=KBEIntPort(self._app.baseapp_tcp_add.port),
            udpPort=KBEIntPort(20005),
            data=KBEBlob(b"client_data"),
        )
        # Есть отличия в KBEngine v1 и v2. Поэтому руками значения в байты.
        # Здесь v2
        data = b""
        data += STRING.encode(pd.account_name)
        data += STRING.encode(pd.host)
        data += INTPORT.encode(pd.tcpPort)
        data += INTPORT.encode(pd.udpPort)
        data += BLOB.encode(pd.data)

        resp_msg = Message.create(msgspec.client.onLoginSuccessfully, (KBEBlob(data),))
        await back_channel.send_msg(resp_msg)


class _LoginappReqCreateAccountHandler(_LoginappHandler[TCPMsgBackChannel]):
    """Обработчик для сообщения Loginapp::reqCreateAccount."""

    def __init__(self, app: LoginappMock) -> None:
        self._app = app

    async def handle(self, msg: Message, back_channel: TCPMsgBackChannel) -> None:
        """Обработать сообщение Loginapp::reqCreateAccount.

        Args:
            msg (Message): сообщение Loginapp::reqCreateAccount
            back_channel (TCPMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        req_res = ReqCreateAccountMsgParser().parse(msg)
        if not req_res.success:
            logger.warning(
                "[%s] The message '%s' is not parsed. Reason: '%s'",
                msg,
                self,
                req_res.text,
            )
            return

        req_pd = req_res.result
        assert req_pd is not None

        if not req_pd.account_name:
            logger.debug(
                "[%s] Account name cannot be empty (client = %s)",
                self,
                back_channel.conn_info.client_addr,
            )
            resp_msg = Message.create(
                msgspec.client.onCreateAccountResult,
                (
                    KBEUInt16(ServerError.NAME.value),
                    req_pd.client_data,
                ),
            )
            await back_channel.send_msg(resp_msg)
            return

        if not req_pd.password:
            logger.debug(
                "[%s] Password cannot be empty (client = %s)",
                self,
                back_channel.conn_info.client_addr,
            )
            resp_msg = Message.create(
                msgspec.client.onCreateAccountResult,
                (
                    KBEUInt16(ServerError.ACCOUNT_CREATE_FAILED.value),
                    req_pd.client_data,
                ),
            )
            await back_channel.send_msg(resp_msg)
            return

        if req_pd.account_name in [self._app.account_name]:
            logger.debug(
                "[%s] Invalid account name: '%s' (client = %s)",
                self,
                req_pd.account_name,
                back_channel.conn_info.client_addr,
            )
            resp_msg = Message.create(
                msgspec.client.onCreateAccountResult,
                (
                    KBEUInt16(ServerError.NAME.value),
                    req_pd.client_data,
                ),
            )
            await back_channel.send_msg(resp_msg)
            return

        logger.info("[%s] Account '%s' created successfully", self, req_pd.account_name)

        resp_msg = Message.create(
            msgspec.client.onCreateAccountResult,
            (
                KBEUInt16(ServerError.SUCCESS.value),
                KBERowByteData(),
            ),
        )
        await back_channel.send_msg(resp_msg)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    __repr__ = __str__


class _LoginappReqCreateMailAccountHandler(_LoginappHandler[TCPMsgBackChannel]):
    """Обработчик для сообщения Loginapp::reqCreateMailAccount."""

    def __init__(self, app: LoginappMock) -> None:
        self._app = app

    async def handle(self, msg: Message, back_channel: TCPMsgBackChannel) -> None:
        """Обработать сообщение Loginapp::reqCreateMailAccount."""
        logger.debug("[%s] %s", self, devonly.func_args_values())

        req_res = ReqCreateMailAccountMsgParser().parse(msg)
        if not req_res.success:
            logger.warning(
                "[%s] The message '%s' is not parsed. Reason: '%s'",
                msg,
                self,
                req_res.text,
            )
            return

        req_pd = req_res.result
        assert req_pd is not None

        if not req_pd.account_name:
            logger.debug(
                "[%s] Account name cannot be empty (client = %s)",
                self,
                back_channel.conn_info.client_addr,
            )
            resp_msg = Message.create(
                msgspec.client.onCreateAccountResult,
                (
                    KBEUInt16(ServerError.NAME.value),
                    req_pd.client_data,
                ),
            )
            await back_channel.send_msg(resp_msg)
            return

        if not req_pd.password:
            logger.debug(
                "[%s] Password cannot be empty (client = %s)",
                self,
                back_channel.conn_info.client_addr,
            )
            resp_msg = Message.create(
                msgspec.client.onCreateAccountResult,
                (
                    KBEUInt16(ServerError.ACCOUNT_CREATE_FAILED.value),
                    req_pd.client_data,
                ),
            )
            await back_channel.send_msg(resp_msg)
            return

        # Как-будто этот аккаунт уже существует
        if req_pd.account_name in [self._app.account_name]:
            logger.debug(
                "[%s] Invalid account name: '%s' (client = %s)",
                self,
                req_pd.account_name,
                back_channel.conn_info.client_addr,
            )
            resp_msg = Message.create(
                msgspec.client.onCreateAccountResult,
                (
                    KBEUInt16(ServerError.NAME.value),
                    req_pd.client_data,
                ),
            )
            await back_channel.send_msg(resp_msg)
            return

        if "@" not in req_pd.account_name:
            logger.debug(
                "[%s] The account name is not email: '%s' (client = %s)",
                self,
                req_pd.account_name,
                back_channel.conn_info.client_addr,
            )
            resp_msg = Message.create(
                msgspec.client.onCreateAccountResult,
                (
                    KBEUInt16(ServerError.NAME_MAIL.value),
                    req_pd.client_data,
                ),
            )
            await back_channel.send_msg(resp_msg)

        logger.info(
            "[%s] Mail account '%s' created successfully",
            self,
            req_pd.account_name,
        )

        resp_msg = Message.create(
            msgspec.client.onCreateAccountResult,
            (
                KBEUInt16(ServerError.SUCCESS.value),
                req_pd.client_data,
            ),
        )
        await back_channel.send_msg(resp_msg)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    __repr__ = __str__


class _LoginappReqAccountResetPasswordHandler(_LoginappHandler[TCPMsgBackChannel]):
    """Обработчик для сообщения Loginapp::reqAccountResetPassword.

    Запрос на сброс пароля аккаунта.
    """

    async def handle(self, msg: Message, back_channel: TCPMsgBackChannel) -> None:
        """Обработать сообщение Loginapp::reqAccountResetPassword.

        Args:
            msg (Message): сообщение Loginapp::reqAccountResetPassword
            back_channel (TCPMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        req_res = ReqAccountResetPasswordMsgParser().parse(msg)
        req_pd = req_res.result
        assert req_pd is not None

        account_name = req_pd.account_name.strip()

        logger.info(
            "[%s] reqAccountResetPassword: accountName(%s) (client = %s)",
            self,
            account_name,
            back_channel.conn_info.client_addr,
        )

        # Имитируем отправку письма для сброса пароля
        logger.info(
            "[%s] Password reset email sent to account '%s' (client = %s)",
            self,
            account_name,
            back_channel.conn_info.client_addr,
        )

        # Отправляем успешный ответ клиенту
        resp_msg = Message.create(
            msgspec.client.onReqAccountResetPasswordCB,
            (KBEUInt16(ServerError.SUCCESS.value),),
        )
        await back_channel.send_msg(resp_msg)


class _LoginappOnClientActiveTickHandler(_LoginappHandler[TCPMsgBackChannel]):
    """Обработчик для сообщения Loginapp::onClientActiveTick.

    Подтверждение, что клиент живой.
    """

    async def handle(self, msg: Message, back_channel: TCPMsgBackChannel) -> None:
        """Обработать сообщение Loginapp::onClientActiveTick.

        Args:
            msg (Message): сообщение Loginapp::onClientActiveTick
            back_channel (TCPMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        req_res = OnClientActiveTickMsgParser().parse(msg)
        req_pd = req_res.result
        assert req_pd is not None

        resp_msg = Message.create(msgspec.client.onAppActiveTickCB, ())
        await back_channel.send_msg(resp_msg)


class _ImportClientMessagesHandler(_LoginappHandler[TCPMsgBackChannel]):
    """Обработчик для сообщения Loginapp::onClientActiveTick.

    Подтверждение, что клиент живой.
    """

    async def handle(self, msg: Message, back_channel: TCPMsgBackChannel) -> None:
        """Обработать сообщение Loginapp::importClientMessages.

        Args:
            msg (Message): сообщение Loginapp::importClientMessages
            back_channel (TCPMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        req_res = ImportClientMessagesMsgParser().parse(msg)
        req_pd = req_res.result
        assert req_pd is not None

        data = KBERowByteData(
            b"\x06\x02\xf0\x0c`\x00\x08\x00\x02\x00Client_onReloginBaseappFailed\x00\x00\x01\x03\t\x00\xff\xffClient_onEntityLeaveWorldOptimized\x00\xff\x00\n\x00\xff\xffClient_onRemoteMethodCallOptimized\x00\xff\x00\x0b\x00\xff\xffClient_onUpdatePropertysOptimized\x00\xff\x00\x0c\x00\xff\xffClient_onSetEntityPosAndDir\x00\xff\x00\r\x00\x0c\x00Client_onUpdateBasePos\x00\x00\x03\r\r\r\x0e\x00\xff\xffClient_onUpdateBaseDir\x00\xff\x00\x0f\x00\x08\x00Client_onUpdateBasePosXZ\x00\x00\x02\r\r\x10\x00\xff\xffClient_onUpdateData\x00\xff\x00\x11\x00\xff\xffClient_onUpdateData_ypr\x00\xff\x00\x12\x00\xff\xffClient_onUpdateData_yp\x00\xff\x00\x13\x00\xff\xffClient_onUpdateData_yr\x00\xff\x00\x14\x00\xff\xffClient_onUpdateData_pr\x00\xff\x00\x15\x00\xff\xffClient_onUpdateData_y\x00\xff\x00\x16\x00\xff\xffClient_onUpdateData_p\x00\xff\x00\x17\x00\xff\xffClient_onUpdateData_r\x00\xff\x00\x18\x00\xff\xffClient_onUpdateData_xz\x00\xff\x00\x19\x00\xff\xffClient_onUpdateData_xz_ypr\x00\xff\x00\x1a\x00\xff\xffClient_onUpdateData_xz_yp\x00\xff\x00\x1b\x00\xff\xffClient_onUpdateData_xz_yr\x00\xff\x00\x1c\x00\xff\xffClient_onUpdateData_xz_pr\x00\xff\x00\x1d\x00\xff\xffClient_onUpdateData_xz_y\x00\xff\x00\x1e\x00\xff\xffClient_onUpdateData_xz_p\x00\xff\x00\x1f\x00\xff\xffClient_onUpdateData_xz_r\x00\xff\x00 \x00\xff\xffClient_onUpdateData_xyz\x00\xff\x00!\x00\xff\xffClient_onUpdateData_xyz_ypr\x00\xff\x00\"\x00\xff\xffClient_onUpdateData_xyz_yp\x00\xff\x00#\x00\xff\xffClient_onUpdateData_xyz_yr\x00\xff\x00$\x00\xff\xffClient_onUpdateData_xyz_pr\x00\xff\x00%\x00\xff\xffClient_onUpdateData_xyz_y\x00\xff\x00&\x00\xff\xffClient_onUpdateData_xyz_p\x00\xff\x00'\x00\xff\xffClient_onUpdateData_xyz_r\x00\xff\x00(\x00\xff\xffClient_onUpdateData_ypr_optimized\x00\xff\x00)\x00\xff\xffClient_onUpdateData_yp_optimized\x00\xff\x00*\x00\xff\xffClient_onUpdateData_yr_optimized\x00\xff\x00+\x00\xff\xffClient_onUpdateData_pr_optimized\x00\xff\x00,\x00\xff\xffClient_onUpdateData_y_optimized\x00\xff\x00-\x00\xff\xffClient_onUpdateData_p_optimized\x00\xff\x00.\x00\xff\xffClient_onUpdateData_r_optimized\x00\xff\x00/\x00\xff\xffClient_onUpdateData_xz_optimized\x00\xff\x000\x00\xff\xffClient_onUpdateData_xz_ypr_optimized\x00\xff\x001\x00\xff\xffClient_onUpdateData_xz_yp_optimized\x00\xff\x002\x00\xff\xffClient_onUpdateData_xz_yr_optimized\x00\xff\x003\x00\xff\xffClient_onUpdateData_xz_pr_optimized\x00\xff\x004\x00\xff\xffClient_onUpdateData_xz_y_optimized\x00\xff\x005\x00\xff\xffClient_onUpdateData_xz_p_optimized\x00\xff\x006\x00\xff\xffClient_onUpdateData_xz_r_optimized\x00\xff\x007\x00\xff\xffClient_onUpdateData_xyz_optimized\x00\xff\x008\x00\xff\xffClient_onUpdateData_xyz_ypr_optimized\x00\xff\x009\x00\xff\xffClient_onUpdateData_xyz_yp_optimized\x00\xff\x00:\x00\xff\xffClient_onUpdateData_xyz_yr_optimized\x00\xff\x00;\x00\xff\xffClient_onUpdateData_xyz_pr_optimized\x00\xff\x00<\x00\xff\xffClient_onUpdateData_xyz_y_optimized\x00\xff\x00=\x00\xff\xffClient_onUpdateData_xyz_p_optimized\x00\xff\x00>\x00\xff\xffClient_onUpdateData_xyz_r_optimized\x00\xff\x00?\x00\xff\xffClient_onImportServerErrorsDescr\x00\xff\x00@\x00\xff\xffClient_onImportClientSDK\x00\xff\x00A\x00\xff\xffClient_initSpaceData\x00\xff\x00B\x00\xff\xffClient_setSpaceData\x00\x00\x03\x04\x01\x01C\x00\xff\xffClient_delSpaceData\x00\x00\x02\x04\x01D\x00\x02\x00Client_onReqAccountResetPasswordCB\x00\x00\x01\x03E\x00\x02\x00Client_onReqAccountBindEmailCB\x00\x00\x01\x03F\x00\x02\x00Client_onReqAccountNewPasswordCB\x00\x00\x01\x03G\x00\xff\xffClient_onReloginBaseappSuccessfully\x00\xff\x00H\x00\x00\x00Client_onAppActiveTickCB\x00\x00\x00\xf5\x01\xff\xffClient_onCreateAccountResult\x00\xff\x00\xf6\x01\xff\xffClient_onLoginSuccessfully\x00\xff\x00\xf7\x01\xff\xffClient_onLoginFailed\x00\xff\x00\xf8\x01\xff\xffClient_onCreatedProxies\x00\x00\x03\x05\x08\x01\xf9\x01\x02\x00Client_onLoginBaseappFailed\x00\x00\x01\x03\xfa\x01\xff\xffClient_onRemoteMethodCall\x00\xff\x00\xfb\x01\xff\xffClient_onEntityEnterWorld\x00\xff\x00\xfc\x01\x04\x00Client_onEntityLeaveWorld\x00\x00\x01\x08\xfd\x01\xff\xffClient_onEntityEnterSpace\x00\xff\x00\xfe\x01\x04\x00Client_onEntityLeaveSpace\x00\x00\x01\x08\xff\x01\xff\xffClient_onUpdatePropertys\x00\xff\x00\x00\x02\x04\x00Client_onEntityDestroyed\x00\x00\x01\x08\x02\x02\xff\xffClient_onStreamDataStarted\x00\x00\x03\x07\x04\x01\x03\x02\xff\xffClient_onStreamDataRecv\x00\xff\x00\x04\x02\x02\x00Client_onStreamDataCompleted\x00\x00\x01\x07\x05\x02\x02\x00Client_onKicked\x00\x00\x01\x03\x06\x02\xff\xffClient_onImportClientMessages\x00\xff\x00\x07\x02\xff\xffClient_onImportClientEntityDef\x00\xff\x00\t\x02\xff\xffClient_onHelloCB\x00\xff\x00\n\x02\xff\xffClient_onScriptVersionNotMatch\x00\xff\x00\x0b\x02\xff\xffClient_onVersionNotMatch\x00\xff\x00\x0c\x02\x05\x00Client_onControlEntity\x00\x00\x02\x08\x06\x02\x00\xff\xffLoginapp_reqCreateAccount\x00\x00\x00\x03\x00\xff\xffLoginapp_login\x00\x00\x00\x04\x00\xff\xffLoginapp_hello\x00\x00\x00\x05\x00\x00\x00Loginapp_importClientMessages\x00\x00\x00\x06\x00\xff\xffLoginapp_reqCreateMailAccount\x00\x00\x00\x07\x00\xff\xffLoginapp_importClientSDK\x00\x00\x00\x08\x00\x00\x00Loginapp_importServerErrorsDescr\x00\x00\x00\x0b\x00\x00\x00Loginapp_onClientActiveTick\x00\x00\x00\x0c\x00\xff\xffLoginapp_reqAccountResetPassword\x00\x00\x01\x01"
        )
        resp_msg = Message.create(msgspec.client.onImportClientMessages, (data,))
        await back_channel.send_msg_content(resp_msg)
