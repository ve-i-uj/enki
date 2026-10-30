"""Модуль содержит реализацию клиента для серверного компонента KBEngine "Loginapp".

Класс LoginappClient предоставляет интерфейс для взаимодействия с сервером Loginapp:
авторизация, создание аккаунтов, импорт описаний сообщений, проверка версий и т.д.
"""

from __future__ import annotations

import asyncio
import logging
from asyncio import CancelledError, Event, Future, Task
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Literal

from enki import msgspec, settings
from enki.apps.clientapp.clients.msg_waiting_storage import (
    WAIT_FOREVER,
    WaitingRespMsgData,
    WaitingRespMsgStorage,
    WaitingRespTimeout,
)
from enki.kbeenum import ClientType, ComponentType, ServerError
from enki.kbetype import *
from enki.misc import devonly
from enki.misc.result import Result
from enki.misc.startable import IStartable
from enki.msg.message import Message
from enki.msg.msg_client import TcpMsgClient
from enki.msg_parser.client_msg_parser import (
    OnCreateAccountResultMsgParser,
    OnHelloCBMsgParser,
    OnImportClientMessagesMsgParser,
    OnImportClientSDKMsgParser,
    OnImportServerErrorsDescrMsgParser,
    OnLoginFailedMsgParser,
    OnLoginSuccessfullyMsgParser,
    OnReqAccountResetPasswordCBMsgParser,
    OnScriptVersionNotMatchMsgParser,
    OnVersionNotMatchMsgParser,
)
from enki.settings import SECOND

if TYPE_CHECKING:
    from enki.msg.msg_descr import MsgDescr, MsgId
    from enki.net.addr import Addr

logger = logging.getLogger(__name__)


@dataclass
class LoginappLoginResultData:
    """Данные результата авторизации в Loginapp.

    Attributes:
        ret_code: Код результата (ошибка или успех) от сервера.
        data: Дополнительные данные от сервера.
        baseapp_tcp_addr: Адрес BaseApp для TCP-соединения (если авторизация успешна).
        baseapp_udp_addr: Адрес BaseApp для UDP-соединения (если авторизация успешна).

    """

    ret_code: ServerError
    data: bytes
    baseapp_tcp_addr: Addr | None = None
    baseapp_udp_addr: Addr | None = None


class LoginappLoginResult(Result):
    """Результат попытки авторизации в Loginapp.

    Attributes:
        success: Флаг успешности операции.
        result: Данные результата авторизации.
        text: Текстовое описание результата.

    """

    success: bool
    result: LoginappLoginResultData
    text: str = ""


AccountName: TypeAlias = str
AccountEmail: TypeAlias = str
AccountPassword: TypeAlias = str
AccountData: TypeAlias = bytes


class CheckVersionResultDataEnum(Enum):
    """Перечисление возможных результатов проверки версий."""

    OK = "OK"
    KBE_VERSION_MISMATCH = "KBE_VERSION_MISMATCH"
    ASSETS_VERSION_MISMATCH = "ASSETS_VERSION_MISMATCH"


@dataclass
class LoginappHelloResultData:
    """Данные результата приветствия/проверки версий с Loginapp."""

    flag: CheckVersionResultDataEnum
    encrypted_key: bytes
    kbe_version: str | None = None
    assets_version: str | None = None
    protocol_md5: str | None = None
    entity_def_md5: str | None = None
    component_type: ComponentType | None = None


@dataclass(frozen=True)
class LoginappHelloResult(Result):
    """Результат приветствия Loginapp (проверка версий)."""

    success: bool
    result: LoginappHelloResultData
    text: str = ""


@dataclass
class CreateAccountResultData:
    """Данные результата создания аккаунта.

    Attributes:
        ret_code: Код результата от сервера (ошибка или успех).
        data: Дополнительные данные ответа сервера.

    """

    ret_code: ServerError
    data: bytes


@dataclass(frozen=True)
class CreateAccountResult(Result):
    """Результат создания аккаунта.

    Attributes:
        success: Флаг успешности операции.
        result: Данные результата создания аккаунта.
        text: Текстовое описание результата.

    """

    success: bool
    result: CreateAccountResultData
    text: str = ""


@dataclass
class ReqAccountResetPasswordResultData:
    """Данные результата запроса сброса пароля.

    Attributes:
        ret_code: Код результата от сервера (ошибка или успех).

    """

    ret_code: ServerError


@dataclass(frozen=True)
class ReqAccountResetPasswordResult(Result):
    """Результат запроса сброса пароля аккаунта."""

    success: bool
    result: ReqAccountResetPasswordResultData
    text: str = ""


@dataclass
class ImportClientMessagesResultData:
    """Данные результата импорта описаний сообщений клиента.

    Attributes:
        client_msgs_descr: Список описаний сообщений, адресованных клиенту.
        loginapp_msgs_descr: Список описаний сообщений для Loginapp.

    """

    client_msgs_descr: list[MsgDescr]
    loginapp_msgs_descr: list[MsgDescr]


@dataclass(frozen=True)
class ImportClientMessagesResult(Result):
    """Результат импорта описаний сообщений клиент-серверного взаимодействия."""

    success: bool
    result: ImportClientMessagesResultData | None = None
    text: str = ""


@dataclass
class ServerErrorInfo:
    """Информация об ошибке сервера — идентификатор, имя и описание."""

    id: int
    name: str
    desc: str


@dataclass
class ImportServerErrorsDescrResultData:
    """Данные результата импорта описаний серверных ошибок."""

    server_error_infos: list[ServerErrorInfo]


@dataclass(frozen=True)
class ImportServerErrorsDescrResult(Result):
    success: bool
    result: ImportServerErrorsDescrResultData | None = None
    text: str = ""


@dataclass
class OnClientActiveTickResultData:
    """Данные результата отправки сигнала активности клиента.

    Attributes:
        resp_dt: Время получения подтверждения от сервера.

    """

    resp_dt: datetime


@dataclass(frozen=True)
class OnClientActiveTickResult(Result):
    """Результат отправки сигнала активности клиента.

    Attributes:
        success: Флаг успешности операции.
        result: Данные подтверждения от сервера.
        text: Текстовое описание результата.

    """

    success: bool
    result: OnClientActiveTickResultData
    text: str = ""


class LoginappConnectionError(Exception):
    """Исключение, возникающее при ошибке подключения к Loginapp."""


class LoginappNoResponseError(Exception):
    """Исключение, возникающее при отсутствии ответа от Loginapp в течение таймаута."""


class LoginappIsNotStartedError(Exception):
    """Исключение, возникающее при попытке взаимодействия с не запущенным Loginapp."""


class LoginappIsStopping(Exception):
    pass


class LoginAppNotLoggedInError(Exception):
    """Исключение, когда пользователь не авторизован в LoginApp."""


@dataclass(frozen=True)
class ImportClientSDKResultData:
    pending_files_number: int
    file_name: str
    data_size: int
    data: memoryview


@dataclass(frozen=True)
class ImportClientSDKResult(Result):
    success: bool
    result: ImportClientSDKResultData | None
    text: str = ""


class LoginappClient(IStartable):
    """Клиент для серверного компонента KBEngine 'Loginapp'.

    Attributes:
        _tcp_msg_client: TCP-клиент для обмена сообщениями с Loginapp.
        _wait_response_seconds: Таймаут ожидания ответа от сервера в секундах.
        _stopping: Флаг, указывающий, что клиент находится в процессе остановки.
        _logging_in: Флаг, указывающий, что выполняется вход в систему.
        _logged_in: Флаг, указывающий, что клиент успешно авторизован.
        _waiting_resp_storage: Хранилище объектов, ожидающих ответных сообщений.
        _receiving_msgs_task: Задача, обрабатывающая входящие сообщения.
        _server_tick_period: Интервал между отправками сигналов активности в секундах.
        _server_tick_task: Задача, отправляющая периодические сигналы активности.
        _server_tick_last_dt: Время последней успешной отправки сигнала активности.
        _server_tick_event: Событие для управления периодической отправкой сигналов.

    """

    def __init__(
        self,
        loginapp_addr: Addr,
        client_type: Literal[
            ComponentType.CLIENT, ComponentType.BOTS, ComponentType.TOOL
        ],
        wait_response_seconds: int,
        server_tick_period: float,
    ) -> None:
        """Конструктор клиента Loginapp.

        Args:
            loginapp_addr: Адрес сервера Loginapp (IP и порт).
            client_type: Тип клиента (CLIENT, BOTS или TOOL).
            wait_response_seconds: Время ожидания ответа от сервера в секундах.
            server_tick_period: Частота отправки сигнала onClientActiveTick (в секундах).

        """
        self._tcp_msg_client: TcpMsgClient = TcpMsgClient(
            loginapp_addr,
            client_type,
            on_end_receive_msg_cb=self._on_end_receive_msg_cb,
        )
        self._wait_response_seconds = wait_response_seconds
        self._stopping = False
        self._logging_in = False
        self._logged_in = False
        self._waiting_resp_storage = WaitingRespMsgStorage()
        self._receiving_msgs_task: Task | None = None
        self._server_tick_period = server_tick_period
        self._server_tick_task: Task | None = None
        self._server_tick_last_dt: datetime | None = None
        self._server_tick_event = Event()

    @property
    def is_started(self) -> bool:
        """Флаг: установлено ли TCP-соединение с Loginapp."""
        return self._tcp_msg_client.is_started

    async def start(self) -> Result:
        """Запустить объект: устанавливает TCP-соединение с Loginapp и запускает фоновые задачи.

        Returns:
            Result: результат запуска объекта.

        """
        start_res = await self._tcp_msg_client.start()
        if not start_res.success:
            text = f'Loginapp is not reachable. Reason: "{start_res.text}")'
            logger.debug("[%s] %s", self, text)
            return Result(success=False, result=None, text=text)
        self._start_receiving_msgs()
        self._server_tick_task = asyncio.create_task(
            self._send_periodical_tick(self._wait_response_seconds)
        )
        logger.info("[%s] Connected to Loginapp (%s)", self, self._tcp_msg_client)
        return Result(success=True, result=None)

    def stop(self) -> None:
        """Остановить клиент: закрывает TCP-соединение и отменяет все ожидающие запросы."""
        if self._stopping:
            logger.info("[%s] The client is already stopping", self)
            return
        self._stopping = True
        # После этого завершится цикл в _start_receiving_msgs. Но нужно ещё вывести
        # _send_periodical_tick из ожидания.
        self._tcp_msg_client.stop()
        self._server_tick_event.set()
        # Отменить все фьюче, ожидающие сообщения
        for obj in self._waiting_resp_storage.get_all():
            obj.future.cancel()

    async def wait_until_stop(self) -> None:
        """Ожидание, когда сервер завершит работу."""
        if self._receiving_msgs_task is not None:
            await self._receiving_msgs_task
        self._receiving_msgs_task = None
        if self._server_tick_task is not None:
            await self._server_tick_task
        self._server_tick_task = None

    def _check_client_is_started(self) -> None:
        """Проверить, что клиент запущен (соединение установлено).

        Raises:
            LoginappIsNotStartedError: Если соединение не установлено.

        """
        if not self._tcp_msg_client.is_started:
            text = "There is no connection to Loginapp"
            logger.warning("[%s] %s", self, text)
            raise LoginappIsNotStartedError(text)

    @property
    def _is_logged_in(self) -> bool:
        """Флаг: авторизован ли клиент в Loginapp."""
        return self._receiving_msgs_task is not None and not self._stopping

    # TODO: [25.07.2026 19:52 burov_alexey@mail.ru]
    # Это скорее к подключению к Baseapp относится
    def _check_client_is_logged_in(self) -> None:
        """Проверить, что клиент авторизован в Loginapp.

        Raises:
            LoginAppNotLoggedInError: Если авторизация не выполнена.

        """
        if not self._is_logged_in:
            text = "There is no login to Loginapp"
            logger.warning("[%s] %s", self, text)
            raise LoginAppNotLoggedInError(text)

    async def _send_msg(
        self,
        msg: Message,
        resp_msgs: list[MsgId] | None = None,
        wait_seconds: WaitingRespTimeout = WAIT_FOREVER,
    ) -> Message | None:
        """Отправить сообщение и ожидать ответ.

        Args:
            msg: Отправляемое сообщение.
            resp_msgs: Список идентификаторов ожидаемых ответных сообщений.
            wait_seconds: Максимальное время ожидания ответа (в секундах).

        Returns:
            Message | None: Ответное сообщение, если ожидается ответ, иначе None.

        Raises:
            LoginappIsNotStartedError: Если клиент не запущен.
            LoginappConnectionError: Если не удалось отправить сообщение.
            LoginappNoResponseError: Если не получен ответ в течение таймаута.
            LoginappIsStopping: Если клиент останавливается во время ожидания.

        """
        self._check_client_is_started()

        resp_wait_obj = None
        if resp_msgs is not None:
            resp_wait_obj = WaitingRespMsgData(
                msg,
                resp_msgs=resp_msgs,
                timeout=wait_seconds,
                future=Future(),
            )
            self._waiting_resp_storage.add_waiting_obj(resp_wait_obj)

        success = await self._tcp_msg_client.send_msg(msg)
        if not success:
            if resp_wait_obj is not None:
                assert resp_wait_obj.resp_msgs
                self._waiting_resp_storage.pop_waiting_obj(resp_wait_obj.resp_msgs[0])

            err_text = (
                f"[{self}] The message is not sent (client = '{self._tcp_msg_client}', "
                f"msg = '{msg}')"
            )
            logger.warning(err_text)
            raise LoginappConnectionError(err_text)

        if resp_wait_obj is not None:
            # Ждём ответа
            try:
                async with asyncio.timeout(resp_wait_obj.timeout):
                    resp_msg = await resp_wait_obj.future

            except TimeoutError as err:
                self._waiting_resp_storage.pop_waiting_obj(resp_wait_obj.resp_msgs[0])
                err_text = (
                    f"[{self}] There is no response. Waiting stopped by timeout "
                    f"(client = '{self._tcp_msg_client}', msg = '{msg}')"
                )
                logger.warning(err_text)
                raise LoginappNoResponseError(err_text) from err

            except CancelledError as err:
                # При остановке все ожидающие ответного сообщения фьючи
                # завершаются. Поэтому ловим здесь это исключение.
                if self._stopping:
                    text = "Loginapp is stopping"
                    raise LoginappIsStopping(text) from err
                # А вот это будет непонятно почему. Поэтому дальше ошибку.
                raise

            return resp_msg

        return None

    def _start_receiving_msgs(self) -> None:
        """Запустить фоновую задачу получения сообщений от Loginapp."""

        async def receive_msgs() -> None:
            if self._tcp_msg_client is None or not self._tcp_msg_client.is_started:
                logger.warning("[%s] There is not started Baseapp client", self)
                return
            # TODO: [2026-02-10 20:49 burov_alexey@mail.ru]:
            # Больше SERVER_TICK_PERIOD должен быть сброс со стороны Baseapp.
            # Таймаут стоит на ожидание ответа. При каждом новом ответе таймаут
            # тоже обновляется.
            # Это нужно оформить.
            async for msg in self._tcp_msg_client.wait_and_iterate_resp_msgs(
                settings.SERVER_TICK_PERIOD * 1.5
            ):
                self._handle_msg(msg)
            logger.debug("[%s] Receiving messgaes is stopped", self)

        self._receiving_msgs_task = asyncio.create_task(receive_msgs())

    def _handle_msg(self, msg: Message) -> None:
        """Обработать входящее сообщение: разрешить ожидание ответа.

        Args:
            msg: Полученное сообщение.

        """
        # logger.debug("[%s] %s", self, devonly.func_args_values())
        if not self._waiting_resp_storage.is_empty:
            waiting_resp_obj = self._waiting_resp_storage.pop_waiting_obj(msg.id)
            assert waiting_resp_obj is not None
            waiting_resp_obj.future.set_result(msg)
            return

    async def _send_periodical_tick(self, wait_timeout: int) -> None:
        """Периодически отправлять сигнал активности (onClientActiveTick).

        Args:
            wait_timeout: Таймаут ожидания ответа на tick (в секундах).

        """
        self._check_client_is_started()
        # Пока можно получать ответные сообщения
        while not self._stopping:
            try:
                res = await self.onClientActiveTick(wait_timeout)
                self._server_tick_last_dt = res.result.resp_dt
            except (
                LoginappIsNotStartedError,
                LoginappConnectionError,
                LoginappNoResponseError,
            ) as err:
                # Не получилось отправить сообщение о том, что клиент живой.
                # Предупреждение в лог и ждём, когда кикнут или будет понятно,
                # что проблемы с сетью. Сами ничего не делаем.
                logger.warning(
                    "[%s] Server tick is not sent. Last tick '%s' (err = %s)",
                    self,
                    (
                        self._server_tick_last_dt
                        if self._server_tick_last_dt is not None
                        else "<Never>"
                    ),
                    err,
                )
            except LoginappIsStopping:
                # Остановка, поэтому просто останавливаем отправку.
                logger.info("The client is stopping. Stop tick sending")
                continue
            self._server_tick_event.clear()
            try:
                async with asyncio.timeout(self._server_tick_period):
                    await self._server_tick_event.wait()
            except TimeoutError:
                pass

    def _on_end_receive_msg_cb(self) -> None:
        """Колбэк на окончание получения данных от сервера.

        Вызывается при разрыве соединения или остановке клиента.
        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        if not self._stopping:
            # Это разрыв соединения
            logger.warning("[%s] The connection is lost", self)
            self.stop()

        self._logged_in = False
        self._logging_in = False

    async def hello(
        self,
        kbe_version: str,
        assets_version: str,
        encrypted_key: bytes,
        wait_seconds: int = 5 * SECOND,
    ) -> LoginappHelloResult:
        """Проверить версии KBEngine и ассетов (Loginapp::hello).

        Args:
            kbe_version: Версия KBEngine, ожидаемая плагином.
            assets_version: Версия ассетов, ожидаемая плагином.
            encrypted_key: Зашифрованный ключ для аутентификации.
            wait_seconds: Таймаут ожидания ответа в секундах (по умолчанию 5).

        Returns:
            LoginappHelloResult: Результат проверки версий.

        Raises:
            LoginappIsNotStartedError: Если клиент не запущен.
            LoginappConnectionError: Если не удалось отправить сообщение.
            LoginappNoResponseError: Если не получен ответ в течение таймаута.

        """
        if not self._tcp_msg_client.is_started:
            text = "There is no connection to Loginapp"
            logger.warning("[%s] %s", self, text)
            raise LoginappIsNotStartedError(text)

        msg = Message.create(
            msgspec.loginapp.hello,
            values=(
                KBEString(kbe_version),
                KBEString(assets_version),
                KBEBlob(encrypted_key),
            ),
        )
        resp_msg = await self._send_msg(
            msg,
            resp_msgs=[
                msgspec.client.onVersionNotMatch.id,
                msgspec.client.onScriptVersionNotMatch.id,
                msgspec.client.onHelloCB.id,
            ],
            wait_seconds=wait_seconds,
        )

        assert resp_msg is not None
        if resp_msg.id == msgspec.client.onVersionNotMatch.id:
            onVersionNotMatch_res = OnVersionNotMatchMsgParser().parse(resp_msg)
            assert onVersionNotMatch_res.result is not None
            onVersionNotMatch_pd = onVersionNotMatch_res.result  # noqa: N806
            plugin_kbe_version = msg.get_values()[0]
            server_kbe_version = onVersionNotMatch_pd.kbe_version
            text = (
                f'Plugin designed for KBEngine version "{plugin_kbe_version}". '
                f'But actual KBEngine version is "{server_kbe_version}"'
            )
            logger.warning("[%s] %s", self, text)

            return LoginappHelloResult(
                success=False,
                result=LoginappHelloResultData(
                    flag=CheckVersionResultDataEnum.KBE_VERSION_MISMATCH,
                    kbe_version=server_kbe_version,
                    encrypted_key=encrypted_key,
                ),
                text=text,
            )

        if resp_msg.id == msgspec.client.onScriptVersionNotMatch.id:
            onScriptVersionNotMatch_res = (  # noqa: N806
                OnScriptVersionNotMatchMsgParser().parse(resp_msg)
            )
            assert onScriptVersionNotMatch_res.result is not None
            onScriptVersionNotMatch_pd = onScriptVersionNotMatch_res.result
            plugin_assets_version = msg.get_values()[1]
            server_assets_version = onScriptVersionNotMatch_pd.assets_version
            text = (
                f'Plugin designed for assets version "{plugin_assets_version}". '
                f'But actual script version is "{server_assets_version}"'
            )

            return LoginappHelloResult(
                success=False,
                result=LoginappHelloResultData(
                    flag=CheckVersionResultDataEnum.ASSETS_VERSION_MISMATCH,
                    assets_version=server_assets_version,
                    encrypted_key=encrypted_key,
                ),
                text=text,
            )

        onHelloCB_res = OnHelloCBMsgParser().parse(resp_msg)  # noqa: N806
        assert onHelloCB_res.result is not None
        onHelloCB_pd = onHelloCB_res.result  # noqa: N806

        return LoginappHelloResult(
            success=True,
            result=LoginappHelloResultData(
                flag=CheckVersionResultDataEnum.OK,
                encrypted_key=encrypted_key,
                kbe_version=onHelloCB_pd.kbe_version,
                assets_version=onHelloCB_pd.assets_version,
                protocol_md5=onHelloCB_pd.protocol_md5,
                entity_def_md5=onHelloCB_pd.entity_def_md5,
                component_type=onHelloCB_pd.component_type,
            ),
        )

    async def login(
        self,
        client_type: ClientType,
        client_data: bytes,
        account_name: AccountName,
        password: AccountPassword,
        entitydefs_hash: str,
        force_login: bool,
        wait_seconds: float = 5 * SECOND,
    ) -> LoginappLoginResult:
        """Авторизоваться в Loginapp и получить адрес Baseapp (Loginapp::login).

        Args:
            client_type: Тип клиента (значение из ClientType).
            client_data: Дополнительные данные клиента.
            account_name: Имя учётной записи.
            password: Пароль.
            entitydefs_hash: Хеш описаний сущностей.
            force_login: Принудительная авторизация (завершает другие сессии).
            wait_seconds: Таймаут ожидания ответа в секундах (по умолчанию 5).

        Returns:
            LoginappLoginResult: Результат авторизации.

        Raises:
            LoginappIsNotStartedError: Если клиент не запущен.
            LoginappConnectionError: Если не удалось отправить сообщение.
            LoginappNoResponseError: Если не получен ответ в течение таймаута.

        """
        if self._logging_in:
            return LoginappLoginResult(
                success=False, result=None, text="It's already trying login"
            )

        if self._logged_in:
            return LoginappLoginResult(
                success=False, result=None, text="It's already logged in"
            )

        self._logging_in = True
        msg = Message.create(
            msgspec.loginapp.login,
            values=(
                KBEInt8(client_type.value),
                KBEBlob(client_data),
                KBEString(account_name),
                KBEString(password),
                KBEString(entitydefs_hash),
                KBEString("1" if force_login else ""),
            ),
        )
        resp_msg = await self._send_msg(
            msg,
            resp_msgs=[
                msgspec.client.onLoginFailed.id,
                msgspec.client.onLoginSuccessfully.id,
            ],
            wait_seconds=wait_seconds,
        )

        assert resp_msg is not None
        if resp_msg.id == msgspec.client.onLoginFailed.id:
            onLoginFailed_res = OnLoginFailedMsgParser().parse(resp_msg)
            assert onLoginFailed_res.result is not None
            onLoginFailed_pd = onLoginFailed_res.result  # noqa: N806
            err_text = (
                f"Login Falied (reason = "
                f"'{onLoginFailed_pd.ret_code.name}', data = "
                f"'{onLoginFailed_pd.data.decode()}')"
            )

            logger.info("%s", err_text)
            return LoginappLoginResult(
                success=False,
                result=LoginappLoginResultData(
                    ret_code=onLoginFailed_pd.ret_code,
                    data=onLoginFailed_pd.data,
                ),
                text=err_text,
            )

        res = OnLoginSuccessfullyMsgParser().parse(resp_msg)
        assert res.result is not None
        pd = res.result
        logger.info(
            "The LoginApp login is successful. The BaseApp address is %s and %s",
            pd.baseapp_tcp_address,
            pd.baseapp_udp_address,
        )
        self._logged_in = True
        return LoginappLoginResult(
            success=True,
            result=LoginappLoginResultData(
                ServerError.SUCCESS,
                pd.data,
                pd.baseapp_tcp_address,
                pd.baseapp_udp_address,
            ),
        )

    async def reqCreateAccount(
        self,
        username: AccountName,
        password: AccountPassword,
        create_account_data: AccountData,
        wait_seconds: int = 5 * SECOND,
    ) -> CreateAccountResult:
        """Создать учётную запись (Loginapp::reqCreateAccount).

        Args:
            username: Имя учётной записи.
            password: Пароль.
            create_account_data: Дополнительные данные для создания аккаунта.
            wait_seconds: Таймаут ожидания ответа в секундах (по умолчанию 5).

        Returns:
            CreateAccountResult: Результат создания аккаунта.

        Raises:
            LoginappIsNotStartedError: Если клиент не запущен.
            LoginappConnectionError: Если не удалось отправить сообщение.
            LoginappNoResponseError: Если не получен ответ в течение таймаута.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        msg = Message.create(
            msgspec.loginapp.reqCreateAccount,
            values=(
                KBEString(username),
                KBEString(password),
                KBERowByteData(create_account_data),
            ),
        )
        resp_msg = await self._send_msg(
            msg,
            resp_msgs=[msgspec.client.onCreateAccountResult.id],
            wait_seconds=wait_seconds,
        )

        assert resp_msg is not None
        assert resp_msg.id == msgspec.client.onCreateAccountResult.id
        res = OnCreateAccountResultMsgParser().parse(resp_msg)
        assert res.result is not None
        pd = res.result
        if res.result.ret_code != ServerError.SUCCESS:
            return CreateAccountResult(
                False, CreateAccountResultData(pd.ret_code, pd.data)
            )

        return CreateAccountResult(True, CreateAccountResultData(pd.ret_code, pd.data))

    async def reqCreateMailAccount(
        self,
        email: AccountEmail,
        password: AccountPassword,
        create_account_data: AccountData,
        wait_seconds: float = 5 * SECOND,
    ) -> CreateAccountResult:
        """Создать аккаунт по email (Loginapp::reqCreateMailAccount).

        Args:
            email: Email пользователя.
            password: Пароль.
            create_account_data: Дополнительные данные для создания аккаунта.
            wait_seconds: Таймаут ожидания ответа в секундах (по умолчанию 5).

        Returns:
            CreateAccountResult: Результат создания аккаунта.

        Raises:
            LoginappIsNotStartedError: Если клиент не запущен.
            LoginappConnectionError: Если не удалось отправить сообщение.
            LoginappNoResponseError: Если не получен ответ в течение таймаута.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        msg = Message.create(
            msgspec.loginapp.reqCreateMailAccount,
            values=(
                KBEString(email),
                KBEString(password),
                KBEBlob(create_account_data),
            ),
        )
        resp_msg = await self._send_msg(
            msg,
            resp_msgs=[msgspec.client.onCreateAccountResult.id],
            wait_seconds=wait_seconds,
        )
        assert resp_msg.id == msgspec.client.onCreateAccountResult.id
        res = OnCreateAccountResultMsgParser().parse(resp_msg)
        assert res.result is not None
        pd = res.result
        if res.result.ret_code != ServerError.SUCCESS:
            return CreateAccountResult(
                False, CreateAccountResultData(pd.ret_code, pd.data)
            )
        return CreateAccountResult(True, CreateAccountResultData(pd.ret_code, pd.data))

    async def reqAccountResetPassword(
        self,
        account_name: AccountName,
        wait_seconds: float = 5 * SECOND,
    ) -> ReqAccountResetPasswordResult:
        """Запросить сброс пароля аккаунта (Loginapp::reqAccountResetPassword).

        Args:
            account_name: Имя аккаунта, для которого запрашивается сброс пароля.
            wait_seconds: Таймаут ожидания ответа в секундах (по умолчанию 5).

        Returns:
            ReqAccountResetPasswordResult: Результат запроса. Если success=True,
                сервер отправит письмо для сброса пароля на email аккаунта.

        Raises:
            LoginappIsNotStartedError: Если клиент не запущен.
            LoginappConnectionError: Если не удалось отправить сообщение.
            LoginappNoResponseError: Если не получен ответ в течение таймаута.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        msg = Message.create(
            msgspec.loginapp.reqAccountResetPassword,
            values=(KBEString(account_name),),
        )
        resp_msg = await self._send_msg(
            msg,
            resp_msgs=[msgspec.client.onReqAccountResetPasswordCB.id],
            wait_seconds=wait_seconds,
        )

        assert resp_msg is not None
        assert resp_msg.id == msgspec.client.onReqAccountResetPasswordCB.id
        res = OnReqAccountResetPasswordCBMsgParser().parse(resp_msg)
        if not res.success:
            return ReqAccountResetPasswordResult(
                success=False,
                result=ReqAccountResetPasswordResultData(res.result.ret_code),
                text=f"Failed to parse response: {res.text}",
            )
        ret_code = res.result.ret_code
        if ret_code != ServerError.SUCCESS:
            return ReqAccountResetPasswordResult(
                success=False,
                result=ReqAccountResetPasswordResultData(res.result.ret_code),
                text=f"Account password reset failed with code: {ret_code.name}",
            )
        logger.info(
            "[%s] Account password reset request accepted for account '%s'",
            self,
            account_name,
        )
        return ReqAccountResetPasswordResult(
            success=True,
            result=ReqAccountResetPasswordResultData(res.result.ret_code),
            text="Account password reset request accepted",
        )

    async def importClientMessages(
        self,
        wait_seconds: float = 5 * SECOND,
    ) -> ImportClientMessagesResult:
        """Запросить описания сообщений клиент-серверного взаимодействия у Loginapp.

        Args:
            wait_seconds: Таймаут ожидания ответа в секундах (по умолчанию 5).

        Returns:
            ImportClientMessagesResult: Результат с описаниями сообщений.

        Raises:
            LoginappIsNotStartedError: Если клиент не запущен.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        msg = Message.create(msgspec.loginapp.importClientMessages, ())
        try:
            resp_msg = await self._send_msg(
                msg,
                resp_msgs=[msgspec.client.onImportClientMessages.id],
                wait_seconds=wait_seconds,
            )
        except LoginappIsStopping as err:
            logger.debug("[%s] %s", self, err)
            return ImportClientMessagesResult(success=False, result=None, text=str(err))
        except (
            LoginappConnectionError,
            LoginappNoResponseError,
        ) as err:
            logger.warning("[%s] %s", self, err)
            return ImportClientMessagesResult(success=False, result=None, text=str(err))
        assert resp_msg is not None
        assert resp_msg.id == msgspec.client.onImportClientMessages.id
        res = OnImportClientMessagesMsgParser().parse(resp_msg)
        if not res.success:
            err_text = f"Failed to parse importClientMessages response: {res.text}"
            logger.warning("[%s] %s", self, err_text)
            return ImportClientMessagesResult(
                success=False,
                result=None,
                text=err_text,
            )
        assert res.result is not None
        logger.info(
            "[%s] Successfully imported %d client messages from Loginapp",
            self,
            len(res.result.msg_specs),
        )
        client_msg_desrs = []
        loginapp_msg_desrs = []
        for msg_spec in res.result.msg_specs:
            if msg_spec.component_type == ComponentType.CLIENT:
                client_msg_desrs.append(msg_spec)
            elif msg_spec.component_type == ComponentType.LOGINAPP:
                loginapp_msg_desrs.append(msg_spec)
            else:
                logger.warning(
                    "[%s] Unexpected message component type: %s for message '%s'",
                    self,
                    msg_spec.component_type,
                    msg_spec,
                )
        return ImportClientMessagesResult(
            success=True,
            result=ImportClientMessagesResultData(
                client_msgs_descr=client_msg_desrs,
                loginapp_msgs_descr=loginapp_msg_desrs,
            ),
        )

    async def importServerErrorsDescr(
        self,
        wait_seconds: float = WAIT_FOREVER,
    ) -> ImportServerErrorsDescrResult:
        """Запросить описания серверных ошибок у Loginapp.

        Args:
            wait_seconds: Таймаут ожидания ответа в секундах (по умолчанию бесконечно).

        Returns:
            ImportServerErrorsDescrResult: Результат с описаниями ошибок.

        Raises:
            LoginappIsNotStartedError: Если клиент не запущен.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        msg = Message.create(msgspec.loginapp.importServerErrorsDescr, ())
        try:
            resp_msg = await self._send_msg(
                msg,
                resp_msgs=[msgspec.client.onImportServerErrorsDescr.id],
                wait_seconds=wait_seconds,
            )
        except LoginappIsStopping as err:
            logger.debug("[%s] %s", self, err)
            return ImportServerErrorsDescrResult(
                success=False, result=None, text=str(err)
            )
        except (
            LoginappConnectionError,
            LoginappNoResponseError,
        ) as err:
            logger.warning("[%s] %s", self, err)
            return ImportServerErrorsDescrResult(
                success=False, result=None, text=str(err)
            )
        assert resp_msg is not None
        assert resp_msg.id == msgspec.client.onImportServerErrorsDescr.id
        res = OnImportServerErrorsDescrMsgParser().parse(resp_msg)
        if not res.success:
            logger.warning("[%s] %s", self, res.text)
            return ImportServerErrorsDescrResult(
                success=False,
                result=None,
                text=res.text,
            )
        assert res.result is not None
        return ImportServerErrorsDescrResult(
            success=True,
            result=ImportServerErrorsDescrResultData(
                server_error_infos=[
                    ServerErrorInfo(i.id, i.name, i.desc)
                    for i in res.result.server_error_infos
                ]
            ),
        )

    async def importClientSDK(
        self,
        options: str,
        chunk_size: int,
        cb_host: str,
        cb_port: int,
        wait_seconds: float = WAIT_FOREVER,
    ) -> ImportClientSDKResult:
        """Импортировать клиентский SDK через Loginapp.

        Запрашивает файлы SDK у Loginapp.

        Args:
            options: Параметры SDK.
            chunk_size: Размер чанка для передачи.
            cb_host: Хост callback.
            cb_port: Порт callback.
            wait_seconds: Таймаут ожидания ответа в секундах (по умолчанию бесконечно).

        Returns:
            ImportClientSDKResult: Результат импорта.

        Raises:
            LoginappIsNotStartedError: Если клиент не запущен.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        msg = Message.create(
            msgspec.loginapp.importClientSDK,
            (
                KBEString(options),
                KBEInt32(chunk_size),
                KBEString(cb_host),
                KBEUInt16(cb_port),
            ),
        )
        try:
            resp_msg = await self._send_msg(
                msg,
                resp_msgs=[msgspec.client.onImportClientSDK.id],
                wait_seconds=wait_seconds,
            )
        except LoginappIsStopping as err:
            logger.debug("[%s] %s", self, err)
            return ImportClientSDKResult(success=False, result=None, text=str(err))
        except (
            LoginappConnectionError,
            LoginappNoResponseError,
        ) as err:
            logger.warning("[%s] %s", self, err)
            return ImportClientSDKResult(success=False, result=None, text=str(err))
        assert resp_msg is not None
        assert resp_msg.id == msgspec.client.onImportServerErrorsDescr.id
        res = OnImportClientSDKMsgParser().parse(resp_msg)
        if not res.success:
            logger.warning("[%s] %s", self, res.text)
            return ImportClientSDKResult(
                success=False,
                result=None,
                text=res.text,
            )
        assert res.result is not None
        pd = res.result
        return ImportClientSDKResult(
            success=True,
            result=ImportClientSDKResultData(
                pending_files_number=pd.remainingFiles,
                file_name=pd.sendFileName,
                data_size=pd.datasize,
                data=memoryview(pd.data),
            ),
        )

    async def onClientActiveTick(self, wait_seconds: int) -> OnClientActiveTickResult:
        """Отправить серверу сигнал активности клиента и ожидать подтверждения.

        Отправляет сообщение Loginapp::onClientActiveTick и ожидает ответ
        Client::onAppActiveTickCB от сервера.

        Args:
            wait_seconds: Таймаут ожидания ответа в секундах.

        Returns:
            OnClientActiveTickResult: Результат с временем подтверждения.

        Raises:
            LoginappIsNotStartedError: Если клиент не запущен.
            LoginappConnectionError: Если не удалось отправить сообщение.
            LoginappNoResponseError: Если нет ответа от сервера в течение таймаута.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        msg = Message.create(msgspec.loginapp.onClientActiveTick, ())
        await self._send_msg(
            msg,
            resp_msgs=[msgspec.client.onAppActiveTickCB.id],
            wait_seconds=wait_seconds,
        )
        # logger.debug("[%s] Received Loginapp::onAppActiveTickCB response", self)
        return OnClientActiveTickResult(
            success=True, result=OnClientActiveTickResultData(resp_dt=datetime.now())
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    __repr__ = __str__
