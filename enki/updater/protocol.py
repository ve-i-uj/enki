"""Communication protocols to request available messages."""

import logging

from enki import client, message, settings
from enki.misc import devonly

logger = logging.getLogger(__name__)


class LoginAppUpdaterProtocol(client.CommunicationProtocol):
    """Communication protocol to request LoginApp messages."""

    async def get_msg_specs(self):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
        await self._client.send(message.Message(
            spec=message.spec.app.loginapp.importClientMessages,
            fields=tuple()
        ))
        resp_msg = await self._waiting_for(
            msg_id_or_ids=message.spec.app.client.onImportClientMessages.id,
            timeout=2
        )
        if resp_msg is None:
            return

        data = resp_msg.get_values()[0]
        return data

    async def login(self, account_name, password):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
        login_msg = message.Message(
            spec=message.spec.app.loginapp.login,
            fields=(0, b'', account_name, password, '')
        )
        await self._client.send(login_msg)
        resp_msg = await self._waiting_for(
            message.spec.app.client.onLoginSuccessfully.id, 5
        )
        fields = resp_msg.get_values()
        baseapp_addr = settings.AppAddr(fields[1], fields[2])
        await self._client.connect(baseapp_addr, settings.ComponentEnum.BASEAPP)


class BaseAppUpdaterProtocol(client.CommunicationProtocol):
    """Communication protocol to request BaseApp messages."""

    async def get_msg_specs(self):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
        await self._client.send(message.Message(
            spec=message.spec.app.baseapp.importClientMessages,
            fields=tuple()
        ))
        resp_msg = await self._waiting_for(
            msg_id_or_ids=message.spec.app.client.onImportClientMessages.id,
            timeout=2
        )
        if resp_msg is None:
            logger.error('No server response')
            return

        data = resp_msg.get_values()[0]
        return data

    async def get_entity_msg_specs(self):
        logger.debug('[%s]  (%s)', self, devonly.func_args_values())
        await self._client.send(message.Message(
            spec=message.spec.app.baseapp.importClientEntityDef,
            fields=tuple()
        ))
        resp_msg = await self._waiting_for(
            msg_id_or_ids=message.spec.app.client.onImportClientEntityDef.id,
            timeout=2
        )
        if resp_msg is None:
            return

        data = resp_msg.get_values()[0]
        return data
