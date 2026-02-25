"""Компонент частично повторяющий функционал KBEngine-компонента Baseapp."""

from __future__ import annotations

import abc
import asyncio
import logging
from asyncio import Future
from typing import TYPE_CHECKING, Generic, TypeVar

from enki import msgspec
from enki.kbeenum import ComponentType, ServerError
from enki.kbetype.decoders.basic_data_type_decoders import BLOB, STRING
from enki.kbetype.decoders.custom_decoders import KBEComponentType
from enki.kbetype.pytypes.basic_data_types import (
    KBEBlob,
    KBERowByteData,
    KBEString,
    KBEUInt16,
)
from enki.misc import devonly
from enki.misc.result import Result
from enki.misc.startable import IStartable
from enki.msg.imsg import IMsgBackChannel, IServerMsgReceiver
from enki.msg.message import Message
from enki.msg.msg_serializer import MessageSerializer
from enki.msg.msg_server import (
    TCPMsgBackChannel,
    TCPMsgServer,
)
from enki.msg_parser.baseapp_msg_parser import LoginBaseappMsgParser
from enki.msgspec import (
    get_comp_msg_specs,
)
from enki.net.addr import Addr

if TYPE_CHECKING:
    from enki.msg.msg_descr import (
        CompenentMsgSpecs,
        ComponentMsgSpecById,
    )

logger = logging.getLogger(__name__)


class BaseappMock(IStartable, IServerMsgReceiver):
    """Компонент частично повторяющий функционал KBEngine-компонента Baseapp."""

    def __init__(
        self,
        tcp_addr: Addr,
        kbe_version: str,
        account_name: str,
        password: str,
        protocol_md5: str,
        entity_def_md5: str,
    ) -> None:
        """Конструктор KBEngine-компонента Baseapp.

        Args:
            tcp_addr (ComponentAddr): адрес приёма TCP-подключений

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        self._server_is_running: Future[None] | None = None

        self._tcp_addr = Addr(tcp_addr.ip_addr, tcp_addr.port)

        msg_spec_by_id: ComponentMsgSpecById = get_comp_msg_specs(
            ComponentType.BASEAPP
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
        self._handlers: dict[int, _BaseappHandler] = {
            msgspec.baseapp.loginBaseapp.id: _BaseappLoginBaseappHandler(self),
            msgspec.baseapp.importClientEntityDef.id: _BaseappImportClientEntityDefHandler(
                self
            ),
        }

        logger.info("[%s] Initialized", self)

        self._kbe_version = KBEString(kbe_version)
        self._assets_version = KBEString("0.1.0")
        self._protocol_md5 = KBEString(protocol_md5)
        self._entity_def_md5 = KBEString(entity_def_md5)
        self._componentType = KBEComponentType(ComponentType.BASEAPP.value)

        self._account_name = account_name
        self._password = password

    @property
    def account_name(self) -> str:
        """Получить версию ассетов."""
        return self._account_name

    @property
    def password(self) -> str:
        """Получить версию ассетов."""
        return self._password

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
        """Запустить компонент Baseapp.

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
        """Флаг запущен ли Baseapp.

        Returns:
            bool: Флаг запущен ли Baseapp

        """
        return (
            self._server_is_running is not None
            and not self._server_is_running.done()
        )

    def on_receive_msg(
        self, msg: Message, back_channel: IMsgBackChannel
    ) -> None:
        """Колбэк на полученное сообщение.

        Args:
            msg (Message): полученное сервером сообщение
            back_channel (IMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        handler = self._handlers.get(msg.id)
        if handler is None:
            logger.warning(
                "[%s] There is no handler for the message %s", self, msg.id
            )
            return

        asyncio.create_task(handler.handle(msg, back_channel))  # noqa: RUF006

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"


_T_IMsgBackChannel = TypeVar("_T_IMsgBackChannel", bound=IMsgBackChannel)


class _BaseappHandler(abc.ABC, Generic[_T_IMsgBackChannel]):
    """Абстрактный класс для обработчика сообщения компонента Baseapp."""

    def __init__(self, app: BaseappMock) -> None:
        self._app = app

    @abc.abstractmethod
    async def handle(
        self, msg: Message, back_channel: _T_IMsgBackChannel
    ) -> None:
        """Обработать сообщение."""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    __repr__ = __str__


class _BaseappLoginBaseappHandler(_BaseappHandler[TCPMsgBackChannel]):
    """Обработчик для сообщения Baseapp::loginBaseapp."""

    def __init__(self, app: BaseappMock) -> None:
        self._app = app

    async def handle(
        self, msg: Message, back_channel: TCPMsgBackChannel
    ) -> None:
        """Обработать сообщение Baseapp::loginBaseapp.

        Args:
            msg (Message): сообщение Baseapp::loginBaseapp
            back_channel (TCPMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        # Парсим входящее сообщение
        req_res = LoginBaseappMsgParser().parse(msg)
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

        # Валидация данных
        if not req_pd.account_name:
            logger.debug(
                "[%s] Account name cannot be empty (client = %s)",
                self,
                back_channel.conn_info.client_addr,
            )

            # Формируем данные для ответа
            data = b""
            data += STRING.encode(KBEString(""))
            data += BLOB.encode(KBEBlob(b""))

            resp_msg = Message.create(
                msgspec.client.onLoginBaseappFailed,
                (
                    KBEUInt16(ServerError.NAME.value),  # Код ошибки
                    KBEBlob(data),  # Данные ответа
                ),
            )
            await back_channel.send_msg(resp_msg)
            return

        # Успешный логин
        logger.info(
            "[%s] Account '%s' logged in successfully to Baseapp",
            self,
            req_pd.account_name,
        )

        serializer = MessageSerializer.get_serializer(ComponentType.CLIENT)

        # Дальше посыпятся onUpdatePropertys и onCreatedProxies (и другие, если
        # сразу в мире появляется)

        # В KBEngine сперва отправляется onUpdatePropertys
        data = b"\xff\x01\x0e\x00\xf3\x00\x00\x00\x00\x04\x02\x00\x00\x00\x00\x00\x00\x00\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00"
        onUpdatePropertys_msg = serializer.deserialize(memoryview(data))[0]
        assert onUpdatePropertys_msg is not None

        await back_channel.send_msg(onUpdatePropertys_msg)

        data = b"\xf8\x01\x14\x00\x00\x00\x07\x00\xf98\xfeb\xf3\x00\x00\x00Account\x00"
        onCreatedProxies_msg = serializer.deserialize(memoryview(data))[0]
        assert onCreatedProxies_msg is not None

        await back_channel.send_msg(onCreatedProxies_msg)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    __repr__ = __str__


class _BaseappImportClientEntityDefHandler(_BaseappHandler[TCPMsgBackChannel]):
    """Обработчик для сообщения Baseapp::importClientEntityDef."""

    def __init__(self, app: BaseappMock) -> None:
        self._app = app

    async def handle(
        self, msg: Message, back_channel: TCPMsgBackChannel
    ) -> None:
        """Обработать сообщение Baseapp::importClientEntityDef.

        Args:
            msg (Message): сообщение Baseapp::importClientEntityDef
            back_channel (TCPMsgBackChannel): канал обратной связи

        """
        logger.debug("[%s] %s", self, devonly.func_args_values())

        # Данные ответного сообщения Client::onImportClientEntityDef
        response_data = b"\x07\x02\xae\x0b#\x00\x01\x00UINT8\x00ENTITY_SUBSTATE\x00\x02\x00UINT16\x00UINT16\x00\x03\x00UINT64\x00UID\x00\x04\x00UINT32\x00ENTITY_UTYPE\x00\x05\x00INT8\x00ENTITY_STATE\x00\x06\x00INT16\x00INT16\x00\x07\x00INT32\x00ENTITY_FORBIDS\x00\x08\x00INT64\x00INT64\x00\t\x00STRING\x00STRING\x00\n\x00UNICODE\x00UNICODE\x00\x0b\x00FLOAT\x00FLOAT\x00\x0c\x00DOUBLE\x00DOUBLE\x00\r\x00PYTHON\x00UID1\x00\x0e\x00PY_DICT\x00PY_DICT\x00\x0f\x00PY_TUPLE\x00PY_TUPLE\x00\x10\x00PY_LIST\x00PY_LIST\x00\x11\x00ENTITYCALL\x00ENTITYCALL\x00\x12\x00BLOB\x00BLOB\x00\x13\x00VECTOR2\x00VECTOR2\x00\x14\x00VECTOR3\x00DIRECTION3D\x00\x15\x00VECTOR4\x00VECTOR4\x00\x16\x00ARRAY\x00ENTITY_FORBID_COUNTER\x00\x05\x00\x17\x00ARRAY\x00ENTITYID_LIST\x00\x07\x00\x18\x00FIXED_DICT\x00AVATAR_DATA\x00\x02AVATAR_DATA.AVATAR_DATA_PICKLER\x00param1\x00\x05\x00param2\x00\x12\x00\x19\x00FIXED_DICT\x00AVATAR_INFOS\x00\x05AVATAR_INFOS.avatar_info_inst\x00dbid\x00\x03\x00name\x00\n\x00roleType\x00\x01\x00level\x00\x02\x00data\x00\x18\x00\x1a\x00FIXED_DICT\x00AVATAR_INFOS_LIST\x00\x01AVATAR_INFOS.AVATAR_INFOS_LIST_PICKLER\x00values\x00\x1b\x00\x1b\x00ARRAY\x00_AVATAR_INFOS_LIST_values_ArrayType\x00\x19\x00\x1c\x00FIXED_DICT\x00BAG\x00\x01\x00values22\x00\x1d\x00\x1d\x00ARRAY\x00_BAG_values22_ArrayType\x00\x1e\x00\x1e\x00ARRAY\x00__BAG_values22_ArrayType_ArrayType\x00\x08\x00\x1f\x00FIXED_DICT\x00EXAMPLES\x00\x02\x00k1\x00\x08\x00k2\x00\x08\x00 \x00ARRAY\x00\x00\x07\x00!\x00ENTITY_COMPONENT\x00\x00\"\x00ENTITY_COMPONENT\x00\x00#\x00ENTITY_COMPONENT\x00\x00Account\x00\x01\x00\x04\x00\x03\x00\x05\x00\x00\x00@\x9c\x04\x00\x00\x00\xff\xffposition\x00\x00\x14\x00A\x9c\x04\x00\x00\x00\xff\xffdirection\x00\x00\x14\x00B\x9c\x02\x00\x00\x00\xff\xffspaceID\x00\x00\x04\x00\x02\x00 \x00\x00\x00\xff\xfflastSelCharacter\x000\x00\x03\x00\x15'\xff\xffonCreateAvatarResult\x00\x02\x01\x00\x19\x00\x03\x00\xff\xffonRemoveAvatar\x00\x01\x03\x00\x13'\xff\xffonReqAvatarList\x00\x01\x1a\x00\x11'\xff\xffreqAvatarList\x00\x00\x12'\xff\xffreqCreateAvatar\x00\x02\x01\x00\n\x00\x01\x00\xff\xffreqRemoveAvatar\x00\x01\n\x00\x02\x00\xff\xffreqRemoveAvatarDBID\x00\x01\x03\x00\x14'\xff\xffselectAvatarGame\x00\x01\x03\x00Avatar\x00\x02\x00\x16\x00\x07\x00\x00\x00\x05\x00@\x9c\x04\x00\x00\x00\xff\xffposition\x00\x00\x14\x00A\x9c\x04\x00\x00\x00\xff\xffdirection\x00\x00\x14\x00B\x9c\x02\x00\x00\x00\xff\xffspaceID\x00\x00\x04\x00\x99\xb7\x04\x00\x00\x00\xff\xffHP\x000\x00\x07\x00\x9a\xb7\x04\x00\x00\x00\xff\xffHP_Max\x000\x00\x07\x00\x9b\xb7\x04\x00\x00\x00\xff\xffMP\x000\x00\x07\x00\x9c\xb7\x04\x00\x00\x00\xff\xffMP_Max\x000\x00\x07\x00\x10\x00\xfd\x00\x00\x00\xff\xffcomponent1\x00\x00!\x00\x15\x00a\x00\x00\x00\xff\xffcomponent2\x00\x00\"\x00\x16\x00\x9d\x00\x00\x00\xff\xffcomponent3\x00\x00#\x00\x9d\xb7\x04\x00\x00\x00\xff\xffforbids\x000\x00\x07\x00*\xa0\x08\x00\x00\x00\xff\xfflevel\x00\x00\x02\x00.\xa0\x04\x00\x00\x00\xff\xffmodelID\x000\x00\x04\x00/\xa0\x04\x00\x00\x00\xff\xffmodelScale\x0030\x00\x01\x00\x0b\x00\x04\x00\x00\x00\xff\xffmoveSpeed\x0050\x00\x01\x00+\xa0\x04\x00\x00\x00\xff\xffname\x00\x00\n\x00\x06\x00\x10\x00\x00\x00\xff\xffown_val\x00\x00\x02\x00)\xa0\x08\x00\x00\x00\xff\xffspaceUType\x00\x00\x04\x00\x9e\xb7\x04\x00\x00\x00\xff\xffstate\x000\x00\x05\x00\x9f\xb7\x04\x00\x00\x00\xff\xffsubState\x00\x00\x01\x00,\xa0\x04\x00\x00\x00\xff\xffuid\x000\x00\x04\x00-\xa0\x04\x00\x00\x00\xff\xffutype\x000\x00\x04\x00u'\xff\xffdialog_addOption\x00\x04\x01\x00\x04\x00\n\x00\x07\x00x'\xff\xffdialog_close\x00\x00v'\xff\xffdialog_setText\x00\x04\n\x00\x01\x00\x04\x00\n\x00\x0c\x00\xff\xffonAddSkill\x00\x01\x07\x00\x07\x00\xff\xffonJump\x00\x00\r\x00\xff\xffonRemoveSkill\x00\x01\x07\x00\x10\x00\xff\xffrecvDamage\x00\x04\x07\x00\x07\x00\x07\x00\x07\x00\xfb*\xff\xffdialog\x00\x02\x07\x00\x04\x00\x05\x00\xff\xffjump\x00\x00\x04\x00\xff\xffrelive\x00\x01\x01\x00\x0b\x00\xff\xffrequestPull\x00\x00\xf9*\xff\xffuseTargetSkill\x00\x02\x07\x00\x07\x00Test\x00\x03\x00\x05\x00\x01\x00\x01\x00\x01\x00@\x9c\x04\x00\x00\x00\xff\xffposition\x00\x00\x14\x00A\x9c\x04\x00\x00\x00\xff\xffdirection\x00\x00\x14\x00B\x9c\x02\x00\x00\x00\xff\xffspaceID\x00\x00\x04\x00\x12\x00\x08\x00\x00\x00\xff\xffown\x001001\x00\x07\x00\x11\x00\x04\x00\x00\x00\xff\xffstate\x00100\x00\x07\x00\x1c\x00\xff\xffhelloCB\x00\x01\x07\x00\x1b\x00\xff\xffsay\x00\x01\x07\x00\x1a\x00\xff\xffhello\x00\x01\x07\x00TestNoBase\x00\x04\x00\x05\x00\x01\x00\x00\x00\x01\x00@\x9c\x04\x00\x00\x00\xff\xffposition\x00\x00\x14\x00A\x9c\x04\x00\x00\x00\xff\xffdirection\x00\x00\x14\x00B\x9c\x02\x00\x00\x00\xff\xffspaceID\x00\x00\x04\x00\x18\x00\x08\x00\x00\x00\xff\xffown\x001001\x00\x07\x00\x17\x00\x04\x00\x00\x00\xff\xffstate\x00100\x00\x07\x00\x1e\x00\xff\xffhelloCB\x00\x01\x07\x00\x1d\x00\xff\xffhello\x00\x01\x07\x00Monster\x00\x05\x00\x11\x00\x01\x00\x00\x00\x00\x00@\x9c\x04\x00\x00\x00\xff\xffposition\x00\x00\x14\x00A\x9c\x04\x00\x00\x00\xff\xffdirection\x00\x00\x14\x00B\x9c\x02\x00\x00\x00\xff\xffspaceID\x00\x00\x04\x00\x99\xb7\x04\x00\x00\x00\xff\xffHP\x000\x00\x07\x00\x9a\xb7\x04\x00\x00\x00\xff\xffHP_Max\x000\x00\x07\x00\x9b\xb7\x04\x00\x00\x00\xff\xffMP\x000\x00\x07\x00\x9c\xb7\x04\x00\x00\x00\xff\xffMP_Max\x000\x00\x07\x00?\xc7\x04\x00\x00\x00\xff\xffentityNO\x000\x00\x04\x00\x9d\xb7\x04\x00\x00\x00\xff\xffforbids\x000\x00\x07\x00.\xa0\x04\x00\x00\x00\xff\xffmodelID\x000\x00\x04\x00/\xa0\x04\x00\x00\x00\xff\xffmodelScale\x0030\x00\x01\x00 \x00\x04\x00\x00\x00\xff\xffmoveSpeed\x0050\x00\x01\x00+\xa0\x04\x00\x00\x00\xff\xffname\x00\x00\n\x00\x9e\xb7\x04\x00\x00\x00\xff\xffstate\x000\x00\x05\x00\x9f\xb7\x04\x00\x00\x00\xff\xffsubState\x00\x00\x01\x00,\xa0\x04\x00\x00\x00\xff\xffuid\x000\x00\x04\x00-\xa0\x04\x00\x00\x00\xff\xffutype\x000\x00\x04\x00\"\x00\xff\xffrecvDamage\x00\x04\x07\x00\x07\x00\x07\x00\x07\x00NPC\x00\x06\x00\n\x00\x00\x00\x00\x00\x00\x00@\x9c\x04\x00\x00\x00\xff\xffposition\x00\x00\x14\x00A\x9c\x04\x00\x00\x00\xff\xffdirection\x00\x00\x14\x00B\x9c\x02\x00\x00\x00\xff\xffspaceID\x00\x00\x04\x00?\xc7\x04\x00\x00\x00\xff\xffentityNO\x000\x00\x04\x00.\xa0\x04\x00\x00\x00\xff\xffmodelID\x000\x00\x04\x00/\xa0\x04\x00\x00\x00\xff\xffmodelScale\x0030\x00\x01\x00+\x00\x04\x00\x00\x00\xff\xffmoveSpeed\x0050\x00\x01\x00+\xa0\x04\x00\x00\x00\xff\xffname\x00\x00\n\x00,\xa0\x04\x00\x00\x00\xff\xffuid\x000\x00\x04\x00-\xa0\x04\x00\x00\x00\xff\xffutype\x000\x00\x04\x00Gate\x00\x07\x00\t\x00\x00\x00\x00\x00\x00\x00@\x9c\x04\x00\x00\x00\xff\xffposition\x00\x00\x14\x00A\x9c\x04\x00\x00\x00\xff\xffdirection\x00\x00\x14\x00B\x9c\x02\x00\x00\x00\xff\xffspaceID\x00\x00\x04\x00?\xc7\x04\x00\x00\x00\xff\xffentityNO\x000\x00\x04\x00.\xa0\x04\x00\x00\x00\xff\xffmodelID\x000\x00\x04\x00/\xa0\x04\x00\x00\x00\xff\xffmodelScale\x0030\x00\x01\x00+\xa0\x04\x00\x00\x00\xff\xffname\x00\x00\n\x00,\xa0\x04\x00\x00\x00\xff\xffuid\x000\x00\x04\x00-\xa0\x04\x00\x00\x00\xff\xffutype\x000\x00\x04\x00"

        # Создаем сообщение Client::onImportClientEntityDef
        # Предполагается, что ID этого сообщения определен в msgspec.client
        resp_msg = Message.create(
            msgspec.client.onImportClientEntityDef,
            (KBERowByteData(response_data),),
        )

        # Отправляем ответ
        await back_channel.send_msg_content(resp_msg)

        logger.info(
            "[%s] Sent Client::onImportClientEntityDef to client %s",
            self,
            back_channel.conn_info.client_addr,
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    __repr__ = __str__
