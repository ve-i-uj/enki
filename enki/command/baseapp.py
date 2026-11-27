"""Commands for sending messages to BaseApp."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from enki import msgspec
from enki.kbetype.pytypes.basic_data_types import KBEBlob, KBEString
from enki.msg.message import Message
from enki.msg.msg_client import TcpMsgClient
from enki.msg_parser.client_msg_parser import (
    OnHelloCBMsgParser,
    OnScriptVersionNotMatchMsgParser,
    OnVersionNotMatchMsgParser,
)
from enki.settings import SECOND

from .icommand import CommandResult, ICommand

if TYPE_CHECKING:
    from enki.kbeenum import ComponentType
    from enki.msg.msg_client import TcpMsgClient

logger = logging.getLogger(__name__)


@dataclass
class BaseappHelloCommandResultData:
    """Данные при удачном ответе на Baseapp::hello."""

    kbe_version: str
    assets_version: str
    protocol_md5: str
    entity_def_md5: str
    component_type: ComponentType


@dataclass(frozen=True)
class BaseappHelloCommandResult(CommandResult):
    """Результат выполнения команды Baseapp::hello."""

    success: bool
    result: BaseappHelloCommandResultData | None = None
    text: str = ""


class BaseappHelloCommand(ICommand[BaseappHelloCommandResult]):
    """BaseApp command 'hello'."""

    def __init__(
        self,
        kbe_version: str,
        script_version: str,
        encrypted_key: bytes,
        started_client: TcpMsgClient,
        resp_timeout: float,
    ) -> None:
        """Конструктор команды.

        Args:
            kbe_version (str): версия KBEngine
            script_version (str): версия скриптов (кода на питоне / assets'ов)
            encrypted_key (bytes): зашифрованный ключ
            started_client (bytes): запущенный клиент к Baseapp
            resp_timeout (float): время ожидания ответа от Baseapp

        """
        self._msg: Message = Message.create(
            msgspec.baseapp.hello,
            (
                KBEString(kbe_version),
                KBEString(script_version),
                KBEBlob(encrypted_key),
            ),
        )

        assert started_client.is_started
        self._client: TcpMsgClient = started_client
        self._resp_timeout: float = resp_timeout

    @override
    async def execute(self) -> BaseappHelloCommandResult:
        """Execute the hello command.

        Returns:
            BaseappHelloCommandResult: The result of the command execution.

        """
        if not self._client.is_started:
            text = (
                f"[{self}] The client is not alive (client = '{self._client}', "
                f"msg = '{self._msg}')"
            )
            logger.warning(text)
            return BaseappHelloCommandResult(success=False, result=None, text=text)

        success = await self._client.send_msg(self._msg)
        if not success:
            text = (
                f"[{self}] The message is not sent (client = '{self._client}', "
                f"msg = '{self._msg}')"
            )
            logger.warning(text)
            return BaseappHelloCommandResult(success=False, text=text)

        resp_msg = await self._client.wait_only_first_resp_msg(5 * SECOND)
        if resp_msg is None:
            text = (
                f"[{self}] There is no response. Waiting stopped by timeout "
                f"(client = '{self._client}', msg = '{self._msg}')"
            )
            logger.warning(text)
            return BaseappHelloCommandResult(success=False, text=text)

        if resp_msg.id == msgspec.client.onVersionNotMatch.id:
            onVersionNotMatch_res = OnVersionNotMatchMsgParser().parse(  # noqa: N806
                resp_msg
            )
            assert onVersionNotMatch_res.result is not None
            onVersionNotMatch_pd = onVersionNotMatch_res.result  # noqa: N806

            plugin_kbe_version = self._msg.get_values()[0]
            server_kbe_version = onVersionNotMatch_pd.kbe_version
            msg = (
                f'Plugin designed for KBEngine version "{plugin_kbe_version}". '
                f'But actual KBEngine version is "{server_kbe_version}"'
            )
            return BaseappHelloCommandResult(success=False, text=msg)

        if resp_msg.id == msgspec.client.onScriptVersionNotMatch.id:
            onScriptVersionNotMatch_res = (  # noqa: N806
                OnScriptVersionNotMatchMsgParser().parse(resp_msg)
            )
            assert onScriptVersionNotMatch_res.result is not None
            onScriptVersionNotMatch_pd = (  # noqa: N806
                onScriptVersionNotMatch_res.result
            )

            plugin_assets_version = self._msg.get_values()[1]
            server_assets_version = onScriptVersionNotMatch_pd.assets_version
            msg = (
                f'Plugin designed for assets version "{plugin_assets_version}". '
                f'But actual script version is "{server_assets_version}"'
            )
            return BaseappHelloCommandResult(success=False, text=msg)

        onHelloCB_res = OnHelloCBMsgParser().parse(resp_msg)  # noqa: N806
        assert onHelloCB_res.result is not None

        onHelloCB_pd = onHelloCB_res.result  # noqa: N806

        return BaseappHelloCommandResult(
            success=True,
            result=BaseappHelloCommandResultData(
                onHelloCB_pd.kbe_version,
                onHelloCB_pd.assets_version,
                onHelloCB_pd.protocol_md5,
                onHelloCB_pd.entity_def_md5,
                onHelloCB_pd.component_type,
            ),
        )
