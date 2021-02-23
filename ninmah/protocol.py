"""Communication protocols to request available messages."""

import logging

from enki import settings
from enki.kbeclient import client
from enki import message
from enki.misc import devonly

logger = logging.getLogger(__name__)


class LoginAppUpdaterProtocol(client.CommunicationProtocol):
    """Communication protocol to request LoginApp messages."""

    async def get_loginapp_msg_specs(self):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
        await self._client.send(message.Message(
            spec=message.app.loginapp.importClientMessages,
            fields=tuple()
        ))
        resp_msg = await self._waiting_for(message.app.client.onImportClientMessages)
        if resp_msg is None:
            return

        data = resp_msg.get_values()[0]
        return data

    async def login(self, account_name: str, password: str):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
        login_msg = message.Message(
            spec=message.app.loginapp.login,
            fields=(0, b'', account_name, password, '')
        )
        await self._client.send(login_msg)
        resp_msg = await self._waiting_for(message.app.client.onLoginSuccessfully)
        fields = resp_msg.get_values()
        baseapp_addr = settings.AppAddr(fields[1], fields[2])
        await self._client.connect(baseapp_addr, settings.ComponentEnum.BASEAPP)

    async def get_server_error_specs(self):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
        await self._client.send(message.Message(
            spec=message.app.loginapp.importServerErrorsDescr,
            fields=tuple()
        ))
        resp_msg = await self._waiting_for(message.app.client.onImportServerErrorsDescr)
        if resp_msg is None:
            return

        data = resp_msg.get_values()[0]
        return data


class BaseAppUpdaterProtocol(client.CommunicationProtocol):
    """Communication protocol to request BaseApp messages."""

    async def get_baseapp_msg_specs(self) -> bytes:
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
        await self._client.send(message.Message(
            spec=message.app.baseapp.importClientMessages,
            fields=tuple()
        ))
        resp_msg = await self._waiting_for(message.app.client.onImportClientMessages)
        if resp_msg is None:
            logger.error('No server response')
            return

        data = resp_msg.get_values()[0]
        return data

    async def get_entity_def_specs(self) -> bytes:
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
        await self._client.send(message.Message(
            spec=message.app.baseapp.importClientEntityDef,
            fields=tuple()
        ))
        resp_msg = await self._waiting_for(message.app.client.onImportClientEntityDef)
        if resp_msg is None:
            return

        data = resp_msg.get_values()[0]
        return data
