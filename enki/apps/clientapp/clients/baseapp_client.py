"""Модуль содержит реализацию клиента для серверного компонента KBEngine "Baseapp".

Класс BaseappClient предоставляет интерфейс для взаимодействия с сервером Baseapp:
проверка версий, авторизация, привязка email, смена пароля, выход и релогин.
"""

from __future__ import annotations

import asyncio
import logging
from asyncio import CancelledError, Event, Future, Task
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Literal, TypeAlias, override

from enki import msgspec, settings
from enki.apps.clientapp.clients.msg_waiting_storage import (
    WAIT_FOREVER,
    WaitingRespMsgData,
    WaitingRespMsgStorage,
    WaitingRespTimeout,
)
from enki.kbeenum import ComponentType, ServerError
from enki.kbetype import (
    KBEBlob,
    KBEString,
)
from enki.kbetype.decoders.custom_decoders import KBEEntityId
from enki.kbetype.pytypes.basic_data_types import KBEUInt64
from enki.misc import devonly
from enki.misc.result import Result
from enki.misc.startable import IStartable
from enki.msg.message import Message
from enki.msg.msg_client import TcpMsgClient
from enki.msg_parser.client_msg_parser import (
    OnCreatedProxiesMsgParser,
    OnHelloCBMsgParser,
    OnLoginBaseappFailedMsgParser,
    OnReqAccountBindEmailCBMsgParser,
    OnReqAccountNewPasswordCBMsgParser,
    OnScriptVersionNotMatchMsgParser,
    OnVersionNotMatchMsgParser,
)
from enki.settings import SECOND

if TYPE_CHECKING:
    from enki.msg.msg_descr import MsgId
    from enki.net.addr import Addr

logger = logging.getLogger(__name__)


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


class BaseappConnectionError(Exception):
    """Исключение, возникающее при ошибке подключения к Baseapp."""


class BaseappNoResponseError(Exception):
    """Исключение, возникающее при отсутствии ответа от Baseapp в течение таймаута."""


class BaseappIsNotStartedError(Exception):
    """Исключение, возникающее при попытке взаимодействия с не запущенным Baseapp."""


class BaseappIsStoppingError(Exception):
    """Исключение, возникающее при остановке клиента Baseapp.

    Используется для прерывания ожидания ответа, когда клиент
    переходит в состояние остановки.
    """


class BaseappNoConnectionError(Exception):
    """Исключение, когда клиент не подключен к Baseapp."""


class BaseappNotLoggedInError(Exception):
    """Исключение, когда клиент не авторизован в Baseapp.

    Соединение при этом может быть установлено, но Baseapp::loginBaseapp
    ещё не выполнялся (или завершился неуспешно, либо после logout).
    """


class BaseappResultDataEnum(Enum):
    """Перечисление возможных результатов проверки версий."""

    OK = "OK"
    KBE_VERSION_MISMATCH = "KBE_VERSION_MISMATCH"
    ASSETS_VERSION_MISMATCH = "ASSETS_VERSION_MISMATCH"


@dataclass
class BaseappResultData:
    """Данные результата проверки версий с Baseapp.

    Attributes:
        flag: Результат проверки версий.
        encrypted_key: Зашифрованный ключ для аутентификации.
        kbe_version: Версия KBEngine на сервере (если есть расхождение).
        assets_version: Версия ассетов на сервере (если есть расхождение).
        protocol_md5: MD5 протокола.
        entity_def_md5: MD5 описаний сущностей.
        component_type: Тип компонента сервера.

    """

    flag: BaseappResultDataEnum

    encrypted_key: bytes

    kbe_version: str | None = None
    assets_version: str | None = None
    protocol_md5: str | None = None
    entity_def_md5: str | None = None
    component_type: ComponentType | None = None


@dataclass(frozen=True)
class BaseappHelloResult(Result):
    """Результат проверки версий с Baseapp.

    Attributes:
        success: Флаг успешности операции.
        result: Данные результата проверки версий.
        text: Текстовое описание результата.

    """

    success: bool
    result: BaseappResultData
    text: str = ""


@dataclass(frozen=True)
class BaseappLoginBaseappResult(Result):
    """Результат авторизации в Baseapp.

    Attributes:
        success: Флаг успешности операции.
        result: Данные результата авторизации.
        text: Текстовое описание результата.

    """

    success: bool
    result: ServerError | None
    text: str = ""


@dataclass
class BaseappReqAccountNewPasswordResultData:
    """Данные результата смены пароля аккаунта.

    Attributes:
        ret_code: Код результата от сервера (ошибка или успех).

    """

    ret_code: ServerError


@dataclass(frozen=True)
class BaseappReqAccountNewPasswordResult(Result):
    """Результат запроса смены пароля аккаунта в Baseapp.

    Attributes:
        success: Флаг успешности операции.
        result: Данные результата смены пароля.
        text: Текстовое описание результата.

    """

    success: bool
    result: BaseappReqAccountNewPasswordResultData | None = None
    text: str = ""


@dataclass
class BaseappReqAccountBindEmailResultData:
    """Данные результата привязки email к аккаунту.

    Attributes:
        ret_code: Код результата от сервера (ошибка или успех).

    """

    ret_code: ServerError


@dataclass(frozen=True)
class BaseappReqAccountBindEmailResult(Result):
    """Результат запроса привязки email к аккаунту в Baseapp.

    Attributes:
        success: Флаг успешности операции.
        result: Данные результата привязки email.
        text: Текстовое описание результата.

    """

    success: bool
    result: BaseappReqAccountBindEmailResultData | None = None
    text: str = ""


@dataclass
class BaseappLogoutResultData:
    """Данные результата выхода из Baseapp.

    Attributes:
        sent: Признак, что сообщение Baseapp::logoutBaseapp отправлено.

    """

    sent: bool


@dataclass(frozen=True)
class BaseappLogoutResult(Result):
    """Результат выхода из Baseapp.

    Attributes:
        success: Флаг успешности операции.
        result: Данные результата выхода.
        text: Текстовое описание результата.

    """

    success: bool
    result: BaseappLogoutResultData | None = None
    text: str = ""


@dataclass
class BaseappReloginResultData:
    """Данные результата релогина в Baseapp.

    Attributes:
        sent: Признак, что сообщение Baseapp::reloginBaseapp отправлено.

    """

    sent: bool


@dataclass(frozen=True)
class BaseappReloginResult(Result):
    """Результат релогина в Baseapp.

    Attributes:
        success: Флаг успешности операции.
        result: Данные результата релогина.
        text: Текстовое описание результата.

    """

    success: bool
    result: BaseappReloginResultData | None = None
    text: str = ""


EntityIDType: TypeAlias = int
RndUuidType: TypeAlias = int
NO_ENTITY_ID = EntityIDType(0)
NO_RND_UUID = RndUuidType(0)


class BaseappClient(IStartable):
    """Клиент для серверного компонента KBEngine 'Baseapp'."""

    NO_ENTITY_ID: EntityIDType = NO_ENTITY_ID
    NO_RND_UUID: RndUuidType = NO_RND_UUID

    def __init__(
        self,
        baseapp_addr: Addr,
        client_type: Literal[
            ComponentType.CLIENT, ComponentType.BOTS, ComponentType.TOOL
        ],
        wait_response_seconds: int,
        server_tick_period: float,
    ) -> None:
        """Конструктор клиента Baseapp.

        Args:
            baseapp_addr: Адрес сервера Baseapp (IP и порт).
            client_type: Тип клиента (CLIENT, BOTS или TOOL).
            wait_response_seconds: Время ожидания ответа от сервера в секундах.
            server_tick_period: Частота отправки сигнала onClientActiveTick (в секундах)

        """
        self._tcp_msg_client: TcpMsgClient = TcpMsgClient(
            baseapp_addr,
            client_type,
            on_end_receive_msg_cb=self._on_end_receive_msg_cb,
        )
        self._wait_response_seconds = wait_response_seconds
        self._stopping = False
        self._waiting_resp_storage = WaitingRespMsgStorage()
        self._receiving_msgs_task: Task[None] | None = None
        self._server_tick_period = server_tick_period
        self._server_tick_task: Task[None] | None = None
        self._server_tick_last_dt: datetime | None = None
        self._server_tick_event = Event()

        self._account_entity_id = self.NO_ENTITY_ID
        self._rnd_uuid = self.NO_RND_UUID

    @property
    def account_entity_id(self) -> EntityIDType:
        """Id сущности, подключённой к серверу."""
        return self._account_entity_id

    @property
    def rnd_uuid(self) -> RndUuidType:
        """Ключ сессии аккаунта."""
        return self._rnd_uuid

    @property
    def is_started(self) -> bool:
        """Флаг: установлено ли TCP-соединение с Baseapp."""
        return self._tcp_msg_client.is_started

    @override
    async def start(self) -> Result:
        """Запустить объект.

        Устанавливает TCP-соединение с Baseapp и запускает фоновые задачи.

        Returns:
            Result: результат запуска объекта.

        """
        start_res = await self._tcp_msg_client.start()
        if not start_res.success:
            text = f'Baseapp is not reachable. Reason: "{start_res.text}")'
            logger.debug("[%s] %s", self, text)

            return Result(success=False, result=None, text=text)

        self._start_receiving_msgs()
        self._server_tick_task = asyncio.create_task(
            self._send_periodical_tick(self._wait_response_seconds)
        )

        logger.info("[%s] Connected to Baseapp (%s)", self, self._tcp_msg_client)

        return Result(success=True, result=None)

    def stop(self) -> None:
        """Остановить клиент.

        Закрывает TCP-соединение и отменяет все ожидающие запросы.
        """
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
            BaseappIsNotStartedError: Если соединение не установлено.

        """
        if not self._tcp_msg_client.is_started:
            text = "There is no connection to Baseapp"
            logger.warning("[%s] %s", self, text)
            raise BaseappIsNotStartedError(text)

    @property
    def _is_connected(self) -> bool:
        """Флаг: подключен ли клиент в Baseapp.

        Клиент считается подключенным, если запущена фоновая задача
        получения сообщений и не инициирована остановка.
        """
        return self._receiving_msgs_task is not None and not self._stopping

    def _check_client_is_connected(self) -> None:
        """Проверить, что клиент авторизован в Baseapp.

        Raises:
            BaseappNoConnectionError: Если нет подключения

        """
        if not self._is_connected:
            text = "There is no login to Baseapp"
            logger.warning("[%s] %s", self, text)
            raise BaseappNoConnectionError(text)

    @property
    def _is_logged_in(self) -> bool:
        """Флаг: авторизован ли клиент в Baseapp.

        Клиент считается авторизованным, если установлено TCP-соединение,
        успешно выполнен Baseapp::loginBaseapp и клиент не инициировал
        остановку.
        """
        return (
            self._account_entity_id != self.NO_ENTITY_ID
            and self._rnd_uuid != self.NO_RND_UUID
        )

    def _check_is_logged_in(self) -> None:
        """Проверить, что клиент авторизован в Baseapp.

        Raises:
            BaseappNotLoggedInError: Если авторизация не выполнена
                (не было успешного Baseapp::loginBaseapp либо
                соединение потеряно).

        """
        if not self._is_logged_in:
            text = "There is no login to Baseapp"
            logger.warning("[%s] %s", self, text)
            raise BaseappNotLoggedInError(text)

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
            BaseappIsNotStartedError: Если клиент не запущен.
            BaseappConnectionError: Если не удалось отправить сообщение.
            BaseappNoResponseError: Если не получен ответ в течение таймаута.
            BaseappIsStopping: Если клиент останавливается во время ожидания.

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
                _ = self._waiting_resp_storage.pop_waiting_obj(
                    resp_wait_obj.resp_msgs[0]
                )

            err_text = (
                f"[{self}] The message is not sent (client = '{self._tcp_msg_client}', "
                f"msg = '{msg}')"
            )
            logger.warning(err_text)
            raise BaseappConnectionError(err_text)

        if resp_wait_obj is not None:
            # Ждём ответа
            try:
                async with asyncio.timeout(resp_wait_obj.timeout):
                    resp_msg = await resp_wait_obj.future

            except TimeoutError as err:
                _ = self._waiting_resp_storage.pop_waiting_obj(
                    resp_wait_obj.resp_msgs[0]
                )
                err_text = (
                    f"[{self}] There is no response. Waiting stopped by timeout "
                    f"(client = '{self._tcp_msg_client}', msg = '{msg}')"
                )
                logger.warning(err_text)
                raise BaseappNoResponseError(err_text) from err

            except CancelledError as err:
                # При остановке все ожидающие ответного сообщения фьючи
                # завершаются. Поэтому ловим здесь это исключение.
                if self._stopping:
                    text = "Baseapp is stopping"
                    raise BaseappIsStoppingError(text) from err
                # А вот это будет непонятно почему. Поэтому дальше ошибку.
                raise

            return resp_msg

        return None

    def _start_receiving_msgs(self) -> None:
        """Запустить фоновую задачу получения сообщений от Baseapp."""

        async def receive_msgs() -> None:
            if not self._tcp_msg_client.is_started:
                logger.warning("[%s] There is not started Baseapp client", self)
                return

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
        logger.debug("[%s] %s", self, devonly.func_args_values())
        if self._waiting_resp_storage.is_waiting_for(msg.id):
            waiting_resp_obj = self._waiting_resp_storage.pop_waiting_obj(msg.id)
            assert waiting_resp_obj is not None
            waiting_resp_obj.future.set_result(msg)
            return

        if msg.id == msgspec.client.onCreatedProxies.id:
            res = OnCreatedProxiesMsgParser().parse(msg)
            assert res.result is not None
            self._account_entity_id = EntityIDType(res.result.entity_id)
            self._rnd_uuid = RndUuidType(res.result.rnd_uuid)

    async def _send_periodical_tick(self, wait_timeout: int) -> None:
        """Периодически отправлять сигнал активности (onClientActiveTick).

        Args:
            wait_timeout: Таймаут ожидания ответа на tick (в секундах).

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        # Пока можно получать ответные сообщения
        while not self._stopping:
            try:
                res = await self.onClientActiveTick(wait_timeout)
                self._server_tick_last_dt = res.result.resp_dt
            except (
                BaseappIsNotStartedError,
                BaseappConnectionError,
                BaseappNoResponseError,
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
            except BaseappIsStoppingError:
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

    async def loginBaseapp(
        self,
        account_name: str,
        password: str,
        wait_seconds: float = 5 * SECOND,
    ) -> BaseappLoginBaseappResult:
        """Авторизоваться в Baseapp (Baseapp::loginBaseapp).

        Args:
            account_name: Имя учётной записи.
            password: Пароль.
            wait_seconds: Таймаут ожидания ответа в секундах (по умолчанию 5).

        Returns:
            BaseappLoginResult: результат авторизации.

        Raises:
            BaseappConnectionError: Если не удалось отправить сообщение.
            BaseappNoResponseError: Если не получен ответ в течение таймаута.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        # После удачного логина посыпятся сообщения на синхронизацию состояния
        # Client::onUpdatePropertys и Client::onCreatedProxies . При удаче
        # сообщения Client::onLoginSuccessfully не будет.
        #
        # На данном моменте есть подключение к Baseapp, уже должны быть
        # проверены версии движка и скриптов через ::hello. Можно делать логин.

        msg = Message.create(
            msgspec.baseapp.loginBaseapp,
            (KBEString(account_name), KBEString(password)),
        )
        resp_msg = await self._send_msg(
            msg,
            resp_msgs=[
                msgspec.client.onUpdatePropertys.id,
                msgspec.client.onCreatedProxies.id,
                msgspec.client.onLoginBaseappFailed.id,
            ],
            wait_seconds=wait_seconds,
        )
        assert resp_msg is not None

        if resp_msg.id == msgspec.client.onLoginBaseappFailed.id:
            onLoginBaseappFailed_res = OnLoginBaseappFailedMsgParser().parse(resp_msg)
            assert onLoginBaseappFailed_res.result is not None
            onLoginBaseappFailed_pd = onLoginBaseappFailed_res.result  # noqa: N806
            err_text = (
                f"Login Falied (reason = '{onLoginBaseappFailed_pd.ret_code.name}')"
            )

            logger.info("%s", err_text)
            return BaseappLoginBaseappResult(
                success=False,
                result=onLoginBaseappFailed_pd.ret_code,
                text=err_text,
            )

        # Это сообщение обновления сущности. Отправляем его в обычный цикл
        # обработки (больше это сообщение уже никто не ожидает).
        self._handle_msg(resp_msg)

        return BaseappLoginBaseappResult(success=True, result=None)

    async def hello(
        self,
        kbe_version: str,
        assets_version: str,
        encrypted_key: bytes,
        wait_seconds: int = 5 * SECOND,
    ) -> BaseappHelloResult:
        """Проверяет версии.

        Returns:
            bool: True если сервер доступен, иначе False.

        """
        msg = Message.create(
            msgspec.baseapp.hello,
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
            onVersionNotMatch_res = OnVersionNotMatchMsgParser().parse(  # noqa: N806
                resp_msg
            )
            assert onVersionNotMatch_res.result is not None
            onVersionNotMatch_pd = onVersionNotMatch_res.result  # noqa: N806

            plugin_kbe_version = msg.get_values()[0]
            server_kbe_version = onVersionNotMatch_pd.kbe_version
            text = (
                f'Plugin designed for KBEngine version "{plugin_kbe_version}". '
                f'But actual KBEngine version is "{server_kbe_version}"'
            )
            logger.warning("[%s] %s", self, text)
            return BaseappHelloResult(
                success=False,
                result=BaseappResultData(
                    flag=BaseappResultDataEnum.KBE_VERSION_MISMATCH,
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
            onScriptVersionNotMatch_pd = (  # noqa: N806
                onScriptVersionNotMatch_res.result
            )

            plugin_assets_version = msg.get_values()[1]
            server_assets_version = onScriptVersionNotMatch_pd.assets_version
            text = (
                f'Plugin designed for assets version "{plugin_assets_version}". '
                f'But actual script version is "{server_assets_version}"'
            )
            return BaseappHelloResult(
                success=False,
                result=BaseappResultData(
                    flag=BaseappResultDataEnum.ASSETS_VERSION_MISMATCH,
                    assets_version=server_assets_version,
                    encrypted_key=encrypted_key,
                ),
                text=text,
            )

        onHelloCB_res = OnHelloCBMsgParser().parse(resp_msg)  # noqa: N806
        assert onHelloCB_res.result is not None

        onHelloCB_pd = onHelloCB_res.result  # noqa: N806

        return BaseappHelloResult(
            success=True,
            result=BaseappResultData(
                flag=BaseappResultDataEnum.OK,
                encrypted_key=encrypted_key,
                kbe_version=onHelloCB_pd.kbe_version,
                assets_version=onHelloCB_pd.assets_version,
                protocol_md5=onHelloCB_pd.protocol_md5,
                entity_def_md5=onHelloCB_pd.entity_def_md5,
                component_type=onHelloCB_pd.component_type,
            ),
        )

    async def reqAccountNewPassword(  # noqa: N802
        self,
        entity_id: int,
        old_password: str,
        new_password: str,
        wait_seconds: int = 5 * SECOND,
    ) -> BaseappReqAccountNewPasswordResult:
        """Сменить пароль аккаунта (Baseapp::reqAccountNewPassword).

        Отправляет сообщение Baseapp::reqAccountNewPassword и ожидает
        ответ Client::onReqAccountNewPasswordCB от сервера.
        Требует предварительной авторизации через Baseapp::loginBaseapp.

        Args:
            entity_id: ID сущности аккаунта.
            old_password: Старый пароль.
            new_password: Новый пароль.
            wait_seconds: Таймаут ожидания ответа в секундах (по умолчанию 5).

        Returns:
            BaseappReqAccountNewPasswordResult: результат операции:
                success=True — сервер подтвердил смену пароля (ret_code
                в result имеет значение ServerError.SUCCESS);
                success=False — сервер отказал, код возврата в result.ret_code.

        Raises:
            BaseappIsNotStartedError: Если клиент не запущен.
            BaseappNoConnectionError: Если фоновый цикл получения сообщений
                не запущен или клиент инициировал остановку.
            BaseappNotLoggedInError: Если клиент не авторизован в Baseapp
                (не было успешного Baseapp::loginBaseapp либо соединение
                потеряно, либо выполнен logout).
            BaseappConnectionError: Если не удалось отправить сообщение.
            BaseappNoResponseError: Если ответ не получен за wait_seconds.
            BaseappIsStoppingError: Если клиент останавливается во время
                ожидания ответа.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        self._check_client_is_connected()
        self._check_is_logged_in()

        msg = Message.create(
            msgspec.baseapp.reqAccountNewPassword,
            values=(
                KBEEntityId(entity_id),
                KBEString(old_password),
                KBEString(new_password),
            ),
        )

        resp_msg = await self._send_msg(
            msg,
            [msgspec.client.onReqAccountNewPasswordCB.id],
            wait_seconds,
        )
        assert resp_msg is not None

        res = OnReqAccountNewPasswordCBMsgParser().parse(resp_msg)
        assert res.result is not None
        pd = res.result

        if pd.ret_code != ServerError.SUCCESS:
            err_text = str(pd.ret_code)
            logger.info("[%s] Account password change failed: %s", self, err_text)
            return BaseappReqAccountNewPasswordResult(
                success=False,
                result=BaseappReqAccountNewPasswordResultData(ret_code=pd.ret_code),
                text=err_text,
            )

        logger.info("[%s] Account password change succeeded", self)
        return BaseappReqAccountNewPasswordResult(
            success=True,
            result=BaseappReqAccountNewPasswordResultData(ret_code=pd.ret_code),
        )

    async def logoutBaseapp(  # noqa: N802
        self,
        key: int,
        entity_id: int,
    ) -> BaseappLogoutResult:
        """Разлогиниться на Baseapp (Baseapp::logoutBaseapp).

        Отправляет сообщение Baseapp::logoutBaseapp. Ответа от сервера
        на это сообщение не предусмотрено — успех означает лишь факт
        отправки.

        Args:
            key: Ключ сессии аккаунта.
            entity_id: ID сущности аккаунта.

        Returns:
            BaseappLogoutResult: результат операции:
                success=True — сообщение отправлено (result.sent == True);
                success=False — отправка не удалась
                (в text — причина, result.sent == False).

        Raises:
            BaseappIsNotStartedError: Если клиент не запущен (соединение
                с Baseapp не установлено).
            BaseappConnectionError: Если не удалось отправить сообщение.
            BaseappIsStoppingError: Если клиент останавливается во время
                отправки сообщения.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        msg = Message.create(
            msgspec.baseapp.logoutBaseapp,
            values=(
                KBEUInt64(key),
                KBEEntityId(entity_id),
            ),
        )

        # Ответа сервера не ждём — _send_msg только отправит сообщение.
        _msg = await self._send_msg(msg)

        logger.info("[%s] Logout successful", self)
        return BaseappLogoutResult(
            success=True,
            result=BaseappLogoutResultData(sent=True),
        )

    async def reloginBaseapp(  # noqa: N802
        self,
        account_name: str,
        password: str,
        key: int = 0,
        entity_id: int = 0,
    ) -> BaseappReloginResult:
        """Перелогиниться на Baseapp (Baseapp::reloginBaseapp).

        Отправляет сообщение Baseapp::reloginBaseapp. Ответа от сервера
        на это сообщение не предусмотрено — успех означает лишь факт
        отправки; фактическое завершение релогина отслеживается
        через дальнейшие серверные сообщения (обновление сущности и т.п.).

        Args:
            account_name: Имя аккаунта.
            password: Пароль.
            key: Ключ сессии (опционально, по умолчанию 0).
            entity_id: ID сущности (опционально, по умолчанию 0).

        Returns:
            BaseappReloginResult: результат операции:
                success=True — сообщение отправлено (result.sent == True);
                success=False — клиент не подключён либо отправка
                не удалась (в text — причина).

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        if not self._tcp_msg_client.is_started:
            err_text = "The client is not alive"
            logger.warning("[%s] %s", self, err_text)
            return BaseappReloginResult(
                success=False,
                result=BaseappReloginResultData(sent=False),
                text=err_text,
            )

        msg = Message.create(
            msgspec.baseapp.reloginBaseapp,
            values=(
                KBEString(account_name),
                KBEString(password),
                KBEUInt64(key),
                KBEEntityId(entity_id),
            ),
        )

        success = await self._tcp_msg_client.send_msg(msg)
        if not success:
            err_text = "Failed to send relogin message"
            logger.warning("[%s] %s", self, err_text)
            return BaseappReloginResult(
                success=False,
                result=BaseappReloginResultData(sent=False),
                text=err_text,
            )

        logger.info("[%s] Relogin request sent for account '%s'", self, account_name)
        return BaseappReloginResult(
            success=True,
            result=BaseappReloginResultData(sent=True),
        )

    async def reqAccountBindEmail(  # noqa: N802
        self,
        entity_id: int,
        password: str,
        email: str,
        wait_seconds: int = 5 * SECOND,
    ) -> BaseappReqAccountBindEmailResult:
        """Привязать email к аккаунту (Baseapp::reqAccountBindEmail).

        Отправляет сообщение Baseapp::reqAccountBindEmail и ожидает
        ответ Client::onReqAccountBindEmailCB от сервера.
        Требует предварительной авторизации через Baseapp::loginBaseapp.

        Args:
            entity_id: ID сущности аккаунта.
            password: Пароль аккаунта.
            email: Email для привязки.
            wait_seconds: Таймаут ожидания ответа в секундах (по умолчанию 5).

        Returns:
            BaseappReqAccountBindEmailResult: результат операции:
                success=True — сервер подтвердил привязку email (ret_code
                в result имеет значение ServerError.SUCCESS);
                success=False — сервер отказал, код возврата в result.ret_code.

        Raises:
            BaseappIsNotStartedError: Если клиент не запущен.
            BaseappNoConnectionError: Если фоновый цикл получения сообщений
                не запущен или клиент инициировал остановку.
            BaseappNotLoggedInError: Если клиент не авторизован в Baseapp
                (не было успешного Baseapp::loginBaseapp либо соединение
                потеряно, либо выполнен logout).
            BaseappConnectionError: Если не удалось отправить сообщение.
            BaseappNoResponseError: Если ответ не получен за wait_seconds.
            BaseappIsStoppingError: Если клиент останавливается во время
                ожидания ответа.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        self._check_client_is_connected()
        self._check_is_logged_in()

        msg = Message.create(
            msgspec.baseapp.reqAccountBindEmail,
            values=(
                KBEEntityId(entity_id),
                KBEString(password),
                KBEString(email),
            ),
        )

        resp_msg = await self._send_msg(
            msg,
            [msgspec.client.onReqAccountBindEmailCB.id],
            wait_seconds,
        )
        assert resp_msg is not None

        res = OnReqAccountBindEmailCBMsgParser().parse(resp_msg)
        assert res.result is not None
        pd = res.result

        if pd.ret_code != ServerError.SUCCESS:
            err_text = str(pd.ret_code)
            logger.info("[%s] Account email binding failed: %s", self, err_text)
            return BaseappReqAccountBindEmailResult(
                success=False,
                result=BaseappReqAccountBindEmailResultData(ret_code=pd.ret_code),
                text=err_text,
            )

        logger.info("[%s] Account email binding succeeded", self)
        return BaseappReqAccountBindEmailResult(
            success=True,
            result=BaseappReqAccountBindEmailResultData(ret_code=pd.ret_code),
        )

    async def onClientActiveTick(  # noqa: N802
        self, wait_seconds: int
    ) -> OnClientActiveTickResult:
        """Отправить серверу сигнал активности клиента и ожидать подтверждения.

        Отправляет сообщение Baseapp::onClientActiveTick и ожидает ответ
        Client::onAppActiveTickCB от сервера.

        Args:
            wait_seconds: Таймаут ожидания ответа в секундах.

        Returns:
            OnClientActiveTickResult: Результат с временем подтверждения.

        Raises:
            BaseappIsNotStartedError: Если клиент не запущен.
            BaseappConnectionError: Если не удалось отправить сообщение.
            BaseappNoResponseError: Если нет ответа от сервера в течение таймаута.

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())
        msg = Message.create(msgspec.baseapp.onClientActiveTick, ())
        msg = await self._send_msg(
            msg,
            resp_msgs=[msgspec.client.onAppActiveTickCB.id],
            wait_seconds=wait_seconds,
        )

        logger.debug("[%s] Received Baseapp::onAppActiveTickCB response", self)
        return OnClientActiveTickResult(
            success=True,
            result=OnClientActiveTickResultData(resp_dt=datetime.now(tz=UTC)),
        )

    def __str__(self) -> str:
        """Строковое представление клиента Baseapp."""
        return f"{self.__class__.__name__}()"

    __repr__ = __str__
