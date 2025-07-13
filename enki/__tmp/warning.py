import abc


class IChannel(abc.ABC):
    pass


class _SupervisorHandler(abc.ABC):

    @abc.abstractmethod
    async def handle(self, channel: IChannel):
        pass


class UDPChannel(IChannel):
    pass


class _OnFindInterfaceAddrHandler(_SupervisorHandler):

    async def handle(self, channel: UDPChannel):
        pass
