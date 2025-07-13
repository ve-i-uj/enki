"""TCP-клиент для отправки и получения KBEngine-сообщений."""

from __future__ import annotations

from enki.misc.startable import IStartable



from .imessage import IMsgProxyForwarder, IClientMsgReceiver, IClientMsgSender


class MsgTCPClient(IStartable, IMsgProxyForwarder, IClientMsgSender):
    """TCP-клиент для KBEngine-сообщений.

    Подключение, отправка сообщения, получение ответа.
    """

    def __init__(self, addr: AppAddr, msg_spec_by_id: MsgSpecById) -> None:
        """Конструктор для tcp-клиента KBEngine-сообщений.

        Args:
            addr (AppAddr): адрес компонента, к которому будет подключение
            msg_spec_by_id (dict[int, MsgDescr]): описание сообщения по id

        """
        self._tcp_client = TCPClient(
            addr=addr,
            # Колбэки для вызовов от транспортного клиента
            on_receive_data_cb=self._on_receive_data,
            on_end_receive_data_cb=self._on_end_receive_data,
        )
        self._serializer = MessageSerializer(msg_spec_by_id)
        self._msg_receiver: IClientMsgReceiver = _DefaultMsgReceiver()
        self._in_buffer = b""

    @property
    def is_alive(self) -> bool:
        """Флаг запущен ли экземпляр класса."""
        return self._tcp_client.is_alive

    async def start(self) -> Result:
        """Запустить объект."""
        return await self._tcp_client.start()

    def stop(self) -> None:
        """Остановить объект."""
        return self._tcp_client.stop()

    def set_msg_receiver(self, receiver: IClientMsgReceiver) -> None:
        """Прописать получателя сообщений."""
        self._msg_receiver = receiver

    def _get_msg_receiver(self) -> IClientMsgReceiver:
        return self._msg_receiver

    def _on_receive_data(self, received_data: bytes):
        logger.debug("[%s] Received data (%s)", self, received_data)
        if self._in_buffer:
            # Waiting for next chunks of the message
            data = memoryview(self._in_buffer + received_data)
        else:
            data = memoryview(received_data)

        while data:
            msg, data = self._serializer.deserialize(data)
            if msg is None:
                logger.debug("[%s] Got chunk of the message", self)
                self._in_buffer += data
                return

            logger.debug(
                '[%s] Message "%s" fields: %s',
                self,
                msg.name,
                msg.get_values(),
            )
            self._get_msg_receiver().on_receive_msg(msg)
            self._in_buffer = b""

    def _on_end_receive_data(self):
        """Оповестить приёмник соощений, что передача закончилась."""
        self._get_msg_receiver().on_end_receive_msg()

    async def send_msg(self, msg: Message) -> bool:
        """Отправить сообщение компоненту KBEngine."""
        logger.debug("[%s] (%s)", self, devonly.func_args_values())
        data = self._serializer.serialize(msg)
        return await self._tcp_client.send_data(data)
