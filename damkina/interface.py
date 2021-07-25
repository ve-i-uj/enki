"""Application interfaces."""

import abc

from enki import kbeclient


# TODO: [25.07.2021 burov_alexey@mail.ru]:
# Возможно, наследование интерфейса - дикое дело
class IApp(kbeclient.IMsgReceiver):
    """Application interface."""

    @abc.abstractmethod
    def send_message(self, msg: kbeclient.Message):
        """Send the message to the server."""
        pass
