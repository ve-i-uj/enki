# import abc

# # TODO: [2022-11-06 15:29 burov_alexey@mail.ru]:
# # Сущности не должны знать о приложении
# class PlayerMover:

#     def __init__(self, app: IApp):
#         self._app = app

#     def move(self, entity: IEntity,
#              new_position: Optional[Position] = None,
#              new_direction: Optional[Direction] = None):
#         logger.debug('[%s] %s', self, devonly.func_args_values())
#         assert entity.isPlayer(), f'The entity is not a player (entity = "{entity}")'
#         if new_position is None and new_direction is None:
#             logger.warning(f'[{self}] There is no new position nor direction')
#             return

#         if new_direction is not None:
#             raise NotImplementedError

#         position = new_position or entity.position
#         direction = new_direction or entity.direction

#         cmd = command.baseapp.OnUpdateDataFromClientForControlledEntityCommand(
#             self._app.client, entity.id, position, direction,
#             entity.is_on_ground, entity.spaceID
#         )

#         asyncio.run(self._app.send_command(cmd))
#         # TODO: [2022-09-18 09:10 burov_alexey@mail.ru]:
#         # Нужно как-то по другому придумать. Мы находимся сейчас в главном треде
#         # и пробуем обновить позицию сущности. Здесь или лок нужен или как-то
#         # по другому это делать.

#         async def _update_entity_pos_and_dir(entity: IEntity):
#             entity.__update_properties__({
#                 'position': position,
#                 'direction': direction,
#             })
#         asyncio.run(_update_entity_pos_and_dir(entity))


# class AppEntity(IUpdatableEntity):
#     """The plugin application entity.

#     It is an application layer entity (not game layer one).
#     """

#     def __init__(self, entity_id: int, entity_mgr: EntityMgr):
#         self._id = entity_id
#         self._entity_mgr = entity_mgr

#         self._cell = CellEntityRemoteCall(entity=self)
#         self._base = BaseEntityRemoteCall(entity=self)
#         self._components: dict[str, EntityComponentRemoteCall] = {}

#         self._pending_msgs: list[Message] = []

#         self._isDestroyed: bool = False
#         self._is_on_ground: bool = False

#     @property
#     def is_on_ground(self) -> bool:
#         return self._is_on_ground

#     def set_on_ground(self, value: bool):
#         self._is_on_ground = value

#     @property
#     def is_initialized(self) -> bool:
#         if self.CLS_ID == settings.NO_ENTITY_CLS_ID:
#             return False
#         return True

#     @property
#     def is_destroyed(self) -> bool:
#         return self._isDestroyed

#     def on_initialized(self):
#         assert self.is_initialized
#         for comp in self._components.values():
#             comp.onAttached(self)

#     def on_destroyed(self):
#         assert self.is_initialized
#         # TODO: [2022-11-02 21:34 burov_alexey@mail.ru]:
#         # Это тоже можно уже делать в самой игровой сущности (обновляемая, которая).
#         # Хотя можно и кучу событий сделать. Т.к. логики не особо в игровом
#         # слое должно быть на эту тему.
#         for comp in self._components.values():
#             comp.onDetached(self)

#     def on_enter_world(self):
#         assert self.is_initialized
#         for comp in self._components.values():
#             comp.onEnterWorld()

#     def on_leave_world(self):
#         assert self.is_initialized
#         for comp in self._components.values():
#             comp.onLeaveWorld()

#     def on_enter_space(self):
#         assert self.is_initialized
#         for comp in self._components.values():
#             comp.onEnterSpace()

#     def on_leave_space(self):
#         assert self.is_initialized
#         for comp in self._components.values():
#             comp.onLeaveSpace()

#     @property
#     def id(self) -> int:
#         return self._id

#     @property
#     def cell(self) -> CellEntityRemoteCall:
#         return self._cell

#     @property
#     def base(self) -> BaseEntityRemoteCall:
#         return self._base

#     def add_pending_msg(self, msg: Message):
#         self._pending_msgs.append(msg)

#     def get_pending_msgs(self) -> list[Message]:
#         return self._pending_msgs[:]

#     def clean_pending_msgs(self):
#         self._pending_msgs[:] = []

#     # TODO: [2022-11-02 11:33 burov_alexey@mail.ru]:
#     # Можно общий декоратор создать "is_not_destroyed"
#     # Декоратор сразу в модуль поместить с реализацией
#     def __update_properties__(self, properties: dict):
#         logger.debug('[%s] %s', self, devonly.func_args_values())
#         if self.is_destroyed:
#             logger.warning(f'[{self}] The entity properties cannot be updated '
#                            f'because the entity has been destroyed '
#                            f'(properties={properties})')
#             return

#         for name, value in properties.items():
#             old_value = getattr(self, f'_{name}')
#             if name in self._components:
#                 value: kbetype.EntityComponentData
#                 old_value.__update_properties__(value.properties)
#                 return

#             setattr(self, f'_{name}', value)

#             set_method = getattr(self, f'set_{name}', None)
#             if set_method is not None:
#                 set_method(old_value)

#     def __remote_call__(self, msg: Message):
#         logger.debug('[%s] %s', self, devonly.func_args_values())
#         # TODO: [2022-11-02 11:21 burov_alexey@mail.ru]:
#         # Скорее нужно переименовать методо, чтобы он в заблуждение не приводил.
#         # Это действительно удалённый вызов, но сообщение у него в аргументах не к месту.
#         if self.is_destroyed:
#             logger.warning(f'[{self}] The entity cannot send the message {msg.id} '
#                            f'because the entity has been destroyed')
#             return
#         self._entity_mgr.send_remote_call(msg)

#     def __on_remote_call__(self, method_name: str, arguments: list) -> None:
#         logger.debug('[%s] %s', self, devonly.func_args_values())
#         if self.is_destroyed:
#             logger.warning(f'[{self}] The entity cannot handle the remote '
#                            f'call because the entity has been destroyed')
#             return
#         method = getattr(self, method_name)
#         method(*arguments)

#     def __str__(self):
#         return f'{self.__class__.__name__}(id={self._id})'

#     @property
#     def direction(self) -> kbetype.Direction:
#         raise NotImplementedError

#     @property
#     def position(self) -> kbetype.Position:
#         raise NotImplementedError

#     @property
#     def spaceID(self) -> int:
#         raise NotImplementedError

#     @property
#     def isDestroyed(self) -> bool:
#         return self._isDestroyed

#     @property
#     def isOnGround(self) -> bool:
#         return self._is_on_ground

#     @property
#     def inWorld(self) -> bool:
#         raise NotImplementedError

#     def className(self) -> str:
#         return self.__class__.__name__

#     def baseCall(self, methodName: str, methodArgs: list[Any]) -> None:
#         method: Optional[Callable] = getattr(self._base, methodName, None)
#         if method is None:
#             logger.warning(f'[{self}] The "base" attribute has no method "{methodName}"')
#             return

#         method(*methodArgs)

#     def cellCall(self, methodName: str, methodArgs: list[Any]) -> None:
#         method: Optional[Callable] = getattr(self._cell, methodName, None)
#         if method is None:
#             logger.warning(f'[{self}] The "cell" attribute has no method "{methodName}"')
#             return

#         method(*methodArgs)

#     def isPlayer(self) -> bool:
#         return self._entity_mgr.is_player(self.id)

#     def getComponent(self, componentName: str, all: bool):
#         raise NotImplementedError

#     def fireEvent(self, eventName: str, *args):
#         raise NotImplementedError

#     def registerEvent(self, eventName: str, callback: Callable):
#         raise NotImplementedError

#     def deregisterEvent(self, eventName: str, callback: Callable):
#         raise NotImplementedError

#     def onDestroy(self):
#         logger.info('[%s] %s', self, devonly.func_args_values())

#     def onEnterWorld(self):
#         logger.info('[%s] %s', self, devonly.func_args_values())

#     def onLeaveWorld(self):
#         logger.info('[%s] %s', self, devonly.func_args_values())

#     def onEnterSpace(self):
#         logger.info('[%s] %s', self, devonly.func_args_values())

#     def onLeaveSpace(self):
#         logger.info('[%s] %s', self, devonly.func_args_values())


# class EntityComponent(_EntityRemoteCall, IKBEClientEntityComponent):
#     CLS_ID: int = settings.NO_ENTITY_CLS_ID
#     DESCR: EntityDesc = gedescr.NO_ENTITY_DESCR

#     def __init__(self, entity: IEntity, own_attr_id: int):
#         # TODO: [2022-08-22 13:37 burov_alexey@mail.ru]:
#         # Use weakref
#         # self._entity_ref: ProxyType[IEntity] = weakref.proxy(entity)
#         self._entity: IEntity = entity
#         self._owner_attr_id: int = own_attr_id

#     @property
#     def ownerID(self) -> int:
#         return self._entity.id

#     @property
#     def owner(self) -> IEntity:
#         return self._entity

#     @property
#     def name(self) -> str:
#         return self.DESCR.property_desc_by_id[10].name

#     def className(self) -> str:
#         return self.__class__.__name__

#     @property
#     def isDestroyed(self) -> bool:
#         return self._entity.isDestroyed

#     def onAttached(self, owner: IKBEClientEntity):
#         logger.info('[%s] %s', self, devonly.func_args_values())

#     def onDetached(self, owner: IKBEClientEntity):
#         logger.info('[%s] %s', self, devonly.func_args_values())

#     def onEnterWorld(self):
#         logger.info('[%s] %s', self, devonly.func_args_values())

#     def onLeaveWorld(self):
#         logger.info('[%s] %s', self, devonly.func_args_values())

#     def onEnterSpace(self):
#         logger.info('[%s] %s', self, devonly.func_args_values())

#     def onLeaveSpace(self):
#         logger.info('[%s] %s', self, devonly.func_args_values())

#     def __update_properties__(self, properties: dict):
#         for name, value in properties.items():
#             old_value = getattr(self, f'_{name}')
#             setattr(self, f'_{name}', value)

#             set_method = getattr(self, f'set_{name}', None)
#             if set_method is not None:
#                 set_method(old_value)

#     def __on_remote_call__(self, method_name: str, arguments: list) -> None:
#         """The callback fires when method has been called on the server."""
#         logger.debug('[%s] %s', self, devonly.func_args_values())
#         method = getattr(self, method_name)
#         method(*arguments)

#     def __str__(self):
#         return f'{self.__class__.__name__}(owner={self._entity})'



# class IKBEClientGameEntity(abc.ABC):
#     """The kbengine entity interface.

#     By the official kbe documentation
#     <https://github.com/kbengine/kbengine/blob/master/docs/api/kbengine_api(en).chm>
#     """

#     @property
#     @abc.abstractmethod
#     def direction(self) -> Direction:
#         """This attribute describes the orientation of the Entity in world space.

#         Data is synchronized from the server to the client.

#         Type:
#             Vector3, which contains (roll, pitch, yaw) in radians.
#         """
#         pass

#     @property
#     @abc.abstractmethod
#     def id(self) -> int:
#         """The entity id."""
#         pass

#     @property
#     @abc.abstractmethod
#     def position(self) -> Position:
#         """The coordinates (x,y,z) of this entity in world space.

#         The data is synchronized from the server to the client.
#         """
#         pass

#     @property
#     @abc.abstractmethod
#     def spaceID(self) -> int:
#         """
#         The ID of the Space where the entity controlled by the current
#         client is located (also can be understood as the corresponding scene,
#         room, and copy).
#         """
#         pass

#     @property
#     @abc.abstractmethod
#     def isOnGround(self) -> bool:
#         """
#         If the value of this attribute is True, the Entity is on the ground,
#         otherwise it is False.

#         If it is a client-controlled entity, this attribute will be synchronized
#         to the server when changed, and other entities will be synchronized
#         to the client by the server. The client can determine
#         this value to avoid the overhead of accuracy.
#         """
#         pass

#     @property
#     @abc.abstractmethod
#     def inWorld(self) -> bool:
#         pass

#     @property
#     @abc.abstractmethod
#     def className(self) -> str:
#         """The class name of the entity."""
#         pass

#     @property
#     @abc.abstractmethod
#     def isDestroyed(self) -> bool:
#         pass

#     @abc.abstractmethod
#     def baseCall(self, methodName: str, methodArgs: list[Any]) -> None:
#         """The method to call the base part of the entity.

#         Note:
#             The entity must have a base part on the server side.
#             Only client entities controlled by the client can access this method.

#         Example:
#             entity.baseCall("reqCreateAvatar", roleType, name);

#         parameters:
#             methodName	string, method name.
#             methodArgs	objects, method parameter list.
#         """
#         pass

#     @abc.abstractmethod
#     def cellCall(self, methodName: str, methodArgs: list[Any]) -> None:
#         """The method to call the cell part of this entity.

#         Note:
#             The entity must have a cell part on the server.
#             Only client entities controlled by the client can access this method.

#         Example:
#             entity.cellCall("xxx", roleType, name);

#         parameters:
#             methodName	string, method name.
#             methodArgs	objects, method parameter list.

#         return:
#             Because it is a remote call, it is not possible to block
#             waiting for a return, so there is no return value.
#         """
#         pass

#     @abc.abstractmethod
#     def onDestroy(self):
#         """
#         Called when the entity is destroyed
#         """
#         pass

#     @abc.abstractmethod
#     def onEnterWorld(self):
#         """
#         If the entity is not client-controlled, it indicates that
#         the entity has entered the view scope of the client-controlled entity
#         on the server, at which point the client can see the entity.

#         If the entity is client controlled, it indicates that
#         the entity has created a cell on the server and entered the Space.
#         """
#         pass

#     @abc.abstractmethod
#     def onLeaveWorld(self):
#         """
#         If the entity is not client-controlled, it indicates that
#         the entity has left the view scope of the client-controlled entity
#         on the server side, and the client cannot see this entity at this time.

#         If the entity is client controlled, it indicates that
#         the entity has already destroyed the cell on the server and left the Space.
#         """
#         pass

#     @abc.abstractmethod
#     def onEnterSpace(self):
#         """The client-controlled entity enters a new space."""
#         pass

#     @abc.abstractmethod
#     def onLeaveSpace(self):
#         """The client-controlled entity leaves the current space."""
#         pass

#     @abc.abstractmethod
#     def isPlayer(self) -> bool:
#         """Is the entity is the player controlled by the current client."""
#         return False

#     @abc.abstractmethod
#     def getComponent(self, componentName: str, all: bool
#                         ) -> list[EntityComponent]:
#         """Gets a component instance of the specified type attached to the entity.

#         parameters:
#             componentName	string, The component type name.
#             all	bool, if True, Returns all instances of the same type
#                 of component, otherwise only returns the first or empty list.
#         """
#         return []

#     @abc.abstractmethod
#     def fireEvent(self, eventName: str, *args):
#         """Trigger entity events.

#         parameters:
#             eventName	string, the name of the event to trigger.
#             args	The event datas to be attached, variable parameters.
#         """
#         pass

#     @abc.abstractmethod
#     def registerEvent(self, eventName: str, callback: Callable):
#         """Register entity events.

#         parameters:
#             eventName	string, the name of the event to be registered
#                 for listening.
#             callback	The callback method used to respond to the event
#                 when the event fires.
#         """
#         pass

#     @abc.abstractmethod
#     def deregisterEvent(self, eventName: str, callback: Callable):
#         """Deregister entity events.

#         parameters:
#             eventName	string, the name of the event to be deregister.
#             callback	The callback method to deregister of the listener.
#         """
#         pass


# class IKBEClientEntityComponent(abc.ABC):
#     """KBEngine client entity component API."""

#     @property
#     @abc.abstractmethod
#     def owner(self) -> IKBEClientEntity:
#         pass

#     @property
#     @abc.abstractmethod
#     def ownerID(self) -> int:
#         pass

#     @property
#     @abc.abstractmethod
#     def name(self) -> str:
#         pass

#     @property
#     @abc.abstractmethod
#     def isDestroyed(self) -> bool:
#         pass

#     @abc.abstractmethod
#     def onAttached(self, owner: IKBEClientEntity):
#         pass

#     @abc.abstractmethod
#     def onDetached(self, owner: IKBEClientEntity):
#         pass

#     @abc.abstractmethod
#     def onEnterWorld(self):
#         pass

#     @abc.abstractmethod
#     def onLeaveWorld(self):
#         pass

#     @abc.abstractmethod
#     def onEnterSpace(self):
#         pass

#     @abc.abstractmethod
#     def onLeaveSpace(self):
#         pass
