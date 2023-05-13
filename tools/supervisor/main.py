"""
Сервер для прослушиваня 255.255.255.255:20086 и храния онлайн статистики
компонентов.
"""

import asyncio
import logging


from enki.app.clientapp.clienthandler.base import Handler
from enki.core.enkitype import AppAddr
from enki.misc import log
from enki.app.clientapp.clienthandler.machinehandler import OnBroadcastInterfaceHandler
from enki.core import msgspec
from enki.net.client.connection import IDataReceiver, UDPServerProtocol
from enki.core.message import IMsgReceiver, Message
from enki.net.serializer import MessageSerializer

from tools.supervisor import settings

logger = logging.getLogger(__name__)


class SupervisorApp(IDataReceiver, IMsgReceiver):

    def __init__(self, addr: AppAddr):
        self._addr = addr
        self._stop: bool = False
        self._serializer = MessageSerializer(msgspec.app.machine.SPEC_BY_ID)

        logger.info('[%s] The Supervisor app has been initialized', self)

    async def start(self):
        loop = asyncio.get_running_loop()
        transport, _protocol = await loop.create_datagram_endpoint(
            lambda: UDPServerProtocol(data_receiver=self),
            local_addr=(self._addr.host, self._addr.port)
        )
        while not self._stop:
            await asyncio.sleep(1)

        transport.close()

    def stop(self):
        self._stop = True

    def on_receive_data(self, data: memoryview) -> None:
        logger.debug('[%s] Received data (%s)', self, data.obj)
        while data:
            msg, data = self._serializer.deserialize(data)
            if msg is None:
                logger.debug('[%s] Got chunk of the message. Rejected', self)
                return

            logger.debug('[%s] Message "%s" fields: %s',
                         self, msg.name, msg.get_values())
            self.on_receive_msg(msg)

    def on_end_receive_data(self):
        self.stop()

    def on_receive_msg(self, msg: Message) -> bool:
        if msg.id == msgspec.app.machine.onBroadcastInterface.id:
            res = OnBroadcastInterfaceHandler().handle(msg)

    def on_end_receive_msg(self):
        pass

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(addr={self._addr})'


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    logger.info('Done')

    app = SupervisorApp(settings.SHEDU_SUPERVISOR_ADDR)
    try:
        await app.start()
        logger.info('Done')
    except Exception as err:
        logger.error(err, exc_info=True)
    finally:
        app.stop()


if __name__ == '__main__':
    asyncio.run(main())
