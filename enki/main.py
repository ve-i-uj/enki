"""The entry point of the project."""

import logging

from tornado import ioloop

from enki.misc import log
from enki import connection, message
from enki import datahandler
from enki import serializer

from enki.msgspec.app import loginapp

logger = logging.getLogger(__name__)


async def main():
    log.setup_root_logger('DEBUG')
    serializer_ = serializer.Serializer()
    
    msg_router = message.MessageRouter()
    incoming_handler = datahandler.IncomingDataHandler(msg_router, serializer_)
    login_app_conn = connection.LoginAppConnection(
        host='localhost',
        port=20013,
        serializer_=serializer_,
        handler=incoming_handler
    )
    await login_app_conn.connect()

    hello_msg = message.Message(
        spec=loginapp.hello,
        fields=('2.5.10', '0.1.0', b'')
    )
    await login_app_conn.send(hello_msg)


if __name__ == '__main__':
    ioloop.IOLoop.current().asyncio_loop.create_task(main())
    ioloop.IOLoop.current().start()
