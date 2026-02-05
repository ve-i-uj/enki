"""Интерфейсы клиента KBEngine."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import NoReturn, TypeAlias

from enki import msgspec
from enki.kbetype.pytypes.basic_data_types import KBEString
from enki.misc.result import Result
from enki.msg.imsg import IClientMsgReceiver, IClientMsgSender
from enki.msg.message import Message


class IGameServerAccounManagerCallbacks(ABC):

    @abstractmethod
    def on_login(
        self, account_name: str, password: str, success: bool, reason: str
    ):
        """Ответ на попытку подключения."""

    @abstractmethod
    def on_create_account(self, success: bool, reason: str):
        """Ответ на создание аккаунта."""

    @abstractmethod
    def on_reset_password(self, success: bool, reason: str):
        """Ответ на сброс пароля."""

    @abstractmethod
    def on_bind_account_email(self, success: bool, reason: str):
        """Ответ на привязку email к аккаунту."""

    @abstractmethod
    def on_set_new_password(self, success: bool, reason: str):
        """Ответ на выставление нового пароля."""

    @abstractmethod
    def on_kicked(self, reason: str):
        """Уведомление на принудительное отключение сервером."""

    @abstractmethod
    def on_server_not_available(self, reason: str):
        """Уведомление, что сервер недоступен."""

    @abstractmethod
    def on_relogin(self, reason: str):
        """Уведомление о переподключении."""

    @abstractmethod
    def on_logout(self, reason: str):
        pass


class LoginToGameServerResultEnum(Enum):
    OK = 0
    INVALID_PASSWORD = 1
    INVALID_USERNAME = 2
    UNKNOWN = 9


class LoginToGameServerResult(Result):
    success: bool
    result: LoginToGameServerResultEnum
    text: str = ""


class IGameServerAccounManager(ABC):
    """Действия, связанные с учётной записью."""

    @abstractmethod
    def _get_user_callbacks(self) -> IGameServerAccounManagerCallbacks:
        pass

    @abstractmethod
    async def check_game_server_is_accessable(
        self,
    ) -> bool:
        """Проверяет доступность игрового сервера.

        Returns:
            bool: True если сервер доступен, иначе False.

        """
        # Игровой или доступен или нет. Другое пользователю и знать не нужно

    @abstractmethod
    def login(self) -> LoginToGameServerResult:
        """Выполняет аутентификацию на игровом сервере.

        Returns:
            Результат логина.

        """
        # В самом конце ещё пользователю нужно сообщить в колбэк. Если логин
        # удачный, то игра началась.

    @abstractmethod
    async def logout(self):
        pass

    @abstractmethod
    async def create_account(self, username: str, password: str) -> bool:
        pass

    @abstractmethod
    async def reset_password(self, username: str):
        """Скинуть пароль."""

    @abstractmethod
    def bind_account_email(self, entity_id: int, password: str, email: str):
        """Привязать попробовать email к аккаунту."""

    @abstractmethod
    def set_new_password(
        self, entity_id: int, oldpassword: str, newpassword: str
    ):
        """Задать новый пароль."""

    @abstractmethod
    def _on_kicked(self, entity_id: int, oldpassword: str, newpassword: str):
        """Следит за принудительным отключением."""

    @abstractmethod
    def _on_relogin(self, entity_id: int, oldpassword: str, newpassword: str):
        """Следит за переподлючениями."""


class IGameServerSessionMsgProxy(IClientMsgSender, IClientMsgReceiver):
    """Интерфейс для получения, отправки сообщений, их проксирования между слоями.

    Сообщения используются слоем для логина, keep alive, переподключения и т.п.
    """

    @abstractmethod
    def get_next_msg_receiver(self) -> IClientMsgReceiver:
        """Получатель сообщения следующего слоя (кому проксируется сообщение)."""

    # Методы унаследованных интерфейсов для упрощения навигации.

    @abstractmethod
    async def send_msg(self, msg: Message) -> bool:
        """Отправить сообщение компоненту KBEngine."""

    @abstractmethod
    async def send_msg_content(self, msg: Message) -> bool:
        """Отправить сообщения без id и длины на компонент, с которого запрос."""

    @abstractmethod
    def on_receive_msg(self, msg: Message) -> None:
        """Колбэк на получение сообщения."""

    @abstractmethod
    def on_end_receive_msg(self) -> None:
        """Колбэк, что сообщения больше приходить не будут."""
        # Штатная остановка приёма

    @abstractmethod
    def on_end_receive_msg_by_error(self) -> None:
        """Колбэк, что сообщения больше приходить не будут из-за ошибки."""
        # Например, разрыв соединения


class _ClientMsgReceiver(IClientMsgReceiver):

    def on_receive_msg(self, msg: Message) -> None:
        """Колбэк на получение сообщения."""
        raise NotImplementedError

    def on_end_receive_msg(self) -> None:
        """Колбэк, что сообщения больше приходить не будут."""
        raise NotImplementedError

    def on_end_receive_msg_by_error(self) -> None:
        """Колбэк, что сообщения больше приходить не будут из-за ошибки."""
        raise NotImplementedError


class _GameServerAccounManagerCallbacks(IGameServerAccounManagerCallbacks):

    def on_login(
        self, account_name: str, password: str, success: bool, reason: str
    ) -> NoReturn:
        """Ответ на попытку подключения."""
        raise NotImplementedError

    def on_create_account(self, success: bool, reason: str) -> NoReturn:
        """Ответ на создание аккаунта."""
        raise NotImplementedError

    def on_reset_password(self, success: bool, reason: str) -> NoReturn:
        """Ответ на сброс пароля."""
        raise NotImplementedError

    def on_bind_account_email(self, success: bool, reason: str) -> NoReturn:
        """Ответ на привязку email к аккаунту."""
        raise NotImplementedError

    def on_set_new_password(self, success: bool, reason: str) -> NoReturn:
        """Ответ на выставление нового пароля."""
        raise NotImplementedError

    def on_kicked(self, reason: str) -> NoReturn:
        """Уведомление на принудительное отключение сервером."""
        raise NotImplementedError

    def on_server_not_available(self, reason: str) -> NoReturn:
        """Уведомление, что сервер недоступен."""
        raise NotImplementedError

    def on_relogin(self, reason: str) -> NoReturn:
        """Уведомление о переподключении."""
        raise NotImplementedError

    def on_logout(self, reason: str) -> NoReturn:
        raise NotImplementedError


AccountName: TypeAlias = str
AccountPassword: TypeAlias = str
AccountData: TypeAlias = bytes


class GameServerSession(IGameServerAccounManager, IGameServerSessionMsgProxy):

    def __init__(self) -> None:
        self._acc_mgr_cbs: _GameServerAccounManagerCallbacks = (
            _GameServerAccounManagerCallbacks()
        )
        self._next_msg_receiver: _ClientMsgReceiver = _ClientMsgReceiver()

    def _get_user_callbacks(self) -> IGameServerAccounManagerCallbacks:
        return self._acc_mgr_cbs

    async def check_game_server_is_accessable(self) -> bool:
        # Игровой или доступен или нет. Другое пользователю и знать не нужно
        raise NotImplementedError

    def login(self) -> LoginToGameServerResult:
        # В самом конце ещё пользователю нужно сообщить в колбэк. Если логин
        # удачный, то игра началась.
        self._acc_mgr_cbs.on_login(
            success=False, account_name="", password="", reason=""
        )
        raise NotImplementedError

    def logout(self) -> NoReturn:
        raise NotImplementedError

    async def create_account(
        self,
        account_name: AccountName,
        password: AccountPassword,
        data: AccountData,
    ) -> bool:
        Message.create(
            msgspec.loginapp.reqCreateAccount,
            (KBEString, password, data),
        )

        raise NotImplementedError

    def reset_password(self, username: str) -> NoReturn:
        """Скинуть пароль."""
        raise NotImplementedError

    def bind_account_email(self, entity_id: int, password: str, email: str) -> NoReturn:
        """Привязать попробовать email к аккаунту."""
        raise NotImplementedError

    def set_new_password(
        self, entity_id: int, oldpassword: str, newpassword: str
    ) -> NoReturn:
        """Задать новый пароль."""
        raise NotImplementedError

    def _on_kicked(self, entity_id: int, oldpassword: str, newpassword: str) -> NoReturn:
        """Следит за принудительным отключением."""
        raise NotImplementedError

    def _on_relogin(self, entity_id: int, oldpassword: str, newpassword: str) -> NoReturn:
        """Следит за переподлючениями."""
        raise NotImplementedError

    def get_next_msg_receiver(self) -> IClientMsgReceiver:
        """Получатель сообщения следующего слоя (кому проксируется сообщение)."""
        return self._next_msg_receiver

    # Методы унаследованных интерфейсов для упрощения навигации.

    async def send_msg(self, msg: Message) -> bool:
        """Отправить сообщение компоненту KBEngine."""
        raise NotImplementedError

    async def send_msg_content(self, msg: Message) -> bool:
        """Отправить сообщения без id и длины на компонент, с которого запрос."""
        raise NotImplementedError

    def on_receive_msg(self, msg: Message) -> None:
        """Колбэк на получение сообщения."""
        raise NotImplementedError

    def on_end_receive_msg(self) -> None:
        """Колбэк, что сообщения больше приходить не будут."""
        # Штатная остановка приёма
        raise NotImplementedError

    def on_end_receive_msg_by_error(self) -> None:
        """Колбэк, что сообщения больше приходить не будут из-за ошибки."""
        # Например, разрыв соединения
        raise NotImplementedError
