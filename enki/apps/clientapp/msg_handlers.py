from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from enki.apps.clientapp.entity_sub_system.entity_msg_parsers import (
    OnUpdatePropertysMsgParser,
)
from enki.kbetype.decoders.custom_decoders import ENTITY_ID
from enki.misc import devonly

if TYPE_CHECKING:
    from enki.apps.clientapp.app import ClientApp
    from enki.apps.clientapp.entity_sub_system.ehelper import EntityHelper
    from enki.msg.message import Message


from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)


class Handler:

    def handle(self, msg: Message) -> None:
        """Handle a message."""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    __repr__ = __str__


class _ClientAppHandler(Handler):
    _SAVE_MSG_TEMPL = (
        'There is NO entity "{entity_id}". Save the message '
        "to handle it in the future."
    )

    def __init__(self, entity_helper: EntityHelper, app: ClientApp) -> None:
        self._app = app
        self._entity_helper = entity_helper


class OnUpdatePropertysClientAppHandler(_ClientAppHandler):
    _SAVE_MSG_TEMPL = 'There is NO entity "{entity_id}". Save the message to handle it in the future.'

    def handle(self, msg: Message) -> None:
        logger.debug(f"[{self}] ({devonly.func_args_values()})")
        values: tuple[Any, ...] = msg.get_values()
        data = memoryview(values[0])
        entity_id, _offset = ENTITY_ID.decode(data)

        if self._entity_helper.get_entity_cls_name_by_eid(entity_id) is None:
            self._app.add_pending_msg(entity_id, msg)
            return

        parser = OnUpdatePropertysMsgParser(self._entity_helper)
        res = parser.parse(msg)
        assert res.result is not None

        pd = res.result
        entity_id = pd.entity_id

        for prop_name, ec_property_data in pd.ec_properties.items():
            for properties in ec_property_data.values():
                self._app.game.update_component_properties(
                    entity_id, prop_name, properties
                )

        self._app.game.update_entity_properties(entity_id, pd.e_properties)


class OnUpdatePropertysOptimizedClientAppHandler(_ClientAppHandler):

    def handle(self, msg: Message) -> OnUpdatePropertysHandlerResult:
        logger.debug(f"[{self}] ({devonly.func_args_values()})")
        OnUpdatePropertysOptimizedHandler(self._entity_helper)
        data: memoryview = msg.get_values()[0]
        entity_id, data = handler.get_entity_id(data)

        if not self._entity_helper.get_entity_cls_name_by_eid(entity_id):
            self._app.add_pending_msg(entity_id, msg)
            return OnUpdatePropertysHandlerResult(
                success=False,
                result=OnUpdatePropertysParsedData(NoValue.NO_ENTITY_ID, {}),
                text=self._SAVE_MSG_TEMPL.format(entity_id=entity_id),
            )

        return handler.handle(msg)


class OnCreatedProxiesClientAppHandler(_ClientAppHandler):

    def handle(self, msg: Message) -> OnCreatedProxiesHandlerResult:
        logger.debug(f"[{self}] ({devonly.func_args_values()})")
        res = OnCreatedProxiesHandler(self._entity_helper).handle(msg)
        self._app.resend_pending_msgs(res.result.entity_id)
        self._app.set_relogin_data(res.result.rnd_uuid, res.result.entity_id)
        return res


class OnEntityEnterWorldClientAppHandler(_ClientAppHandler):

    def handle(self, msg: Message) -> OnEntityEnterWorldHandlerResult:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        OnEntityEnterWorldHandler(self._entity_helper)
        data = msg.get_values()[0]
        entity_id, data = handler.get_entity_id(data)

        if not self._entity_helper.is_player(entity_id):
            # The proxy entity (aka player) is initialized in the onCreatedProxies
            self._app.resend_pending_msgs(entity_id)

        return handler.handle(msg)


# [2026-02-21 19:03 burov_alexey@mail.ru]:
# Это в клиент Baseapp нужно.
# @dataclass
# class OnKickedHandlerParsedData(ParsedMsgData):
#     ret_code: ServerError


# @dataclass
# class OnKickedHandlerResult(HandlerResult):
#     success: bool
#     result: OnKickedHandlerParsedData
#     msg_id: int = msgspec.app.client.onKicked.id
#     text: str = ""


# class OnKickedHandler(Handler):

#     def __init__(self, app: ClientApp) -> None:
#         super().__init__()
#         self._app = app

#     def handle(self, msg: Message) -> OnKickedHandlerResult:
#         code: int = msg.get_values()[0]
#         server_error = ServerError(code)
#         return OnKickedHandlerResult(
#             True, OnKickedHandlerParsedData(server_error)
#         )
