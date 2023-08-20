"""Интерфейсы ключевых типов данных для assets'ов."""

from __future__ import annotations
import abc

from typing import Any, Callable, Optional, Dict, List, Tuple, Union

from ._math import Vector3

from .. import IN_THE_ENGINE


class IEntityCall:
    """Родительский класс для всех удалённых вызовов к сущности.

    IEntityCall - это 1) сущность, у которой нет свойств, но можно вызывать
    удалённые методы, через обращение к свойствам base, cell, client и т.д. (mailbox, адрес)
    2) И тоже самое, что и IRemoteCall (так сделано в KBEngine).
    """

    if not IN_THE_ENGINE:

        @property
        def id(self) -> int:
            return 0


class IRemoteCall(IEntityCall):
    """Родительский класс для всех IRemoteCall.

    IRemoteCall - это класс, через который осуществляется вызов удалённых методов.
    base, cell, client и т.д. - это ссылки на экземпляры IRemoteCall.
    """


class IEntityCoponentRemoteCall:
    """Родительский класс для всех IRemoteCall компонента сущности."""


class ICellRemoteCall(IRemoteCall):
    """API удалённых вызов на cell компонент сущности."""
    pass


class IBaseRemoteCall(IRemoteCall):
    """API удалённых вызов на base компонент сущности."""
    pass


class IClientRemoteCall(IRemoteCall):
    """API удалённых вызов на client компонент сущности."""
    pass


class IAllClientRemoteCall(IClientRemoteCall):
    """Интерфейс методов для .allClients атрибута сущности.

    Интерефейс аналогичный ClientRemoteCall, т.к. теже самые методы.
    """


class IOtherClientRemoteCall(IClientRemoteCall):
    """Интерфейс методов для .otherClients атрибута сущности.

    Интерефейс аналогичный ClientRemoteCall, т.к. теже самые методы.
    """


class ICellEntity:
    """Methods of an entity located on a cell component (on Cellapp)."""

    if not IN_THE_ENGINE:

        def accelerate(self, accelerateType: str, acceleration: float) -> float:
            """Accelerate the current movement of the entity.

            The activities that can be accelerated include:
            Entity.moveToEntity
            Entity.moveToPoint
            Entity.navigate
            Entity.addYawRotator

            parameters:
            accelerateType	string, the type of movement affected such as: "Movement", "Turn".
            velocity	float, acceleration per second, use negative to decelerate

            returns:
            The current speed of the affected entity.
            """
            return 0.0

        def addYawRotator(self, targetYaw: float, velocity: float,
                          userArg: Optional[int] = None):
            """
            The control entity rotates around yaw. Entity.onTurn is called when
            the rotation completes.

            To remove it, use Entity.cancelController with the controller ID
            or use Entity.cancelController("Movement") to remove it.

            See:
            Entity.cancelController

            parameters:
            targetYaw	float, the given target yaw radians.
            velocity	float, the arc per second when rotated.
            userArg	Optional integer that is common to all controllers. If this
            value is not 0, it is passed to the callback function. It is recommended
            to set the default value to 0 in the callback prototype.
            """
            pass

        def addProximity(self, rangeXZ: float, rangeY: float, userArg: Optional[int] = None) -> int:
            """
            Create an area trigger that will notify the Entity when other entities
            enter or leave the trigger area. This area is a square (for efficiency).

            If another entity is within a given distance on the x-axis and z-axis,
            it is considered to be within the range. This Entity is notified via
            the onEnterTrap and onLeaveTrap functions, which can be defined as follows:

                def onEnterTrap( self, entityEntering, rangeXZ, rangeY, controllerID, userArg = 0 ):
                def onLeaveTrap( self, entityLeaving, rangeXZ, rangeY, controllerID, userArg = 0 ):

            Because the scope trigger is a controller, use Entity.cancelController
            with the controller ID to delete it.

            It should be noted that the callback may be triggered immediately,
            even before the call to addProximity() returns.

            See:
                Entity.cancelController

            parameters:
                rangeXZ	float, the size of the xz axis area of the trigger, must be
                    greater than or equal to zero.
                rangeY	float, the height of the y-axis of the trigger, must be
                    greater than or equal to zero.
                    It should be noted that for this parameter to take effect
                    kbengine_defaults.xml->cellapp->coordinate_system->rangemgr_y
                    must be set to true.
                    Open y-axis management will increase CPU consumption, because
                    some games have a large number of entities at the same y-axis
                    height or all on the ground which is almost completely flat.
                    Because of this, the collision becomes very dense.
                    3D space games or small room-type games are more suitable
                    for this option.
                userArg	Optional integer that is common to all controllers. If this
                    value is not 0, it is passed to the callback function. It is
                    recommended to set the default value to 0 in the callback prototype.

            returns:
                The ID of the created controller.
            """
            return -1

        def addTimer(self, start: float, interval: float = 0.0, userData: int = 0) -> int:
            """Register a timer.

            The timer is triggered by the callback function onTimer,
            which will be executed the first time after "initialOffset" seconds,
            and then executed once every "repeatOffset" seconds. A "userArg"
            parameter can be set (integer only).

            The onTimer function must be defined in the base part of the entity
            with two parameters. The first is an integer, the timer id
            (which can be used to remove the timer's "delTimer" function),
            and the second is the user parameter "userArg".

            Example:

            # Here is an example of using addTimer
            import KBEngine

            class MyBaseEntity( KBEngine.Entity ):

                def __init__( self ):
                    KBEngine.Entity.__init__( self )

                    # Add a timer, trigger for the first time after 5 seconds,
                    # and execute once per second afterwards. The user parameter is 9.
                    self.addTimer( 5, 1, 9 )

                    # Add a timer and execute it once after 1 second. The default
                    # user parameter is 0.
                    self.addTimer( 1 )

                # Entity timer callback "onTimer" is called
                def onTimer( self, id, userArg ):
                    print "MyBaseEntity.onTimer called: id %i, userArg: %i" % ( id, userArg )
                    # If this is a repeated timer, when the timer is no longer
                    # needed, call the following function to remove it:
                    #     self.delTimer( id )

            parameters:
                initialOffset - specifies the time interval in seconds for
                    the timer to trigger the first callback.
                repeatOffset - specifies the time interval (in seconds) after
                    each execution of the first callback execution. You must remove
                    the timer with the function delTimer, otherwise it will continue
                    to repeat. Values less than or equal to 0 will be ignored.
                userArg	- specifies the value of the userArg parameter when invoking
                    the "onTimer" callback.

            returns:
                integer, the internal id of the timer. This id can be used
                to remove the timer using delTimer.
            """
            return -1

        def cancelController(self, controllerID: Union[str, int]):
            """
            The function cancelController stops the effect of a controller on Entity.
            It can only be called on a real entity.

            parameters:
                controllerID	integer, the index of the controller to cancel.
                    A special controller type string can also be used as its type.
                    For example, only one mobile/navigation controller can
                    be activated at a time. This can be cancelled with
                    entity.cancelController( "Movement" ).
            """
            pass

        def clientEntity(self, destID: int) -> Optional[ICellEntity]:
            """
            This method can access the method of an entity in its own client
            (the current entity must be bound to the client). Only the entities
            in the View scope will be synchronized to the client. It can only be
            called on a real entity.

            parameters:
                destID	integer, the ID of the target entity.
            """
            pass

        def canNavigate(self) -> bool:
            """
            This method determines whether the current entity can use the navigation
            (Entity.navigate) feature. It can only be called on a real entity.
            Usually it can use navigation when the entity's Space uses
            KBENgine.addSpaceGeometryMapping to load valid navigation collision
            data (Navmesh or 2D tile data) and the entity is available in
            the effective navigation area.

            returns:
                bool, returns True if the entity can use the Navigate function
                in the current space, otherwise it returns False.
            """
            return False

        def debugView(self):
            """
            debugView outputs the Entity's View details to the cell's debug log.
            A description of the workings of the View system can be found in
            the Entity class documentation.

            A sample of information is as follows:

            INFO cellapp [0x00001a1c] [2014-11-04 00:28:41,409] - Avatar::debugView: 100 size=4, Seen=4, Pending=0, ViewRadius=50.000, ViewHyst=5.000
            INFO cellapp [0x00001a1c] [2014-11-04 00:28:41,409] - Avatar::debugView: 100 Avatar(102), position(771.586.211.002.776.55), dist=0
            INFO cellapp [0x00001a1c] [2014-11-04 00:28:41,409] - Avatar::debugView: 100 Monster(1028), position(820.834.211.635.768.749), dist=49.8659
            INFO cellapp [0x00001a1c] [2014-11-04 00:28:41,409] - Avatar::debugView: 100 NPC(1025), position(784.024.210.95.782.273), dist=13.6915
            INFO cellapp [0x00001a1c] [2014-11-04 00:28:41,409] - Avatar::debugView: 100 Avatar(106), position(771.586.211.002.776.55), dist=0

            The first line of information tells us:

                It is entity #1000's data.
                There are 4 entities in its View area and all have been synchronized
                    to the client.
                There are 0 entities in its view Area that are waiting to be
                    synchronized to the client.
                The radius of the View is 50.000
                The lag area of the View extends 5.000 outward.
            """
            pass

        def delTimer(self, id: Union[int, str]):
            """
            The delTimer function is used to remove a registered timer. The removed
            timer is no longer executed. Single shot timers are automatically
            removed after the callback is executed, and it is not necessary to use
            the delTimer to remove it. If the delTimer function uses an invalid ID
            (for example, it has been removed), an error will be generated.

            parameters:
                id	integer, which specifies the timer ID to remove. If the
                    parameter is the string "All", all timers are removed at once.
            """
            pass

        def destroy(self):
            """
            This function destroys its local Entity instance. If the entity has
            a ghost part on other processes, it will also notify for their
            destruction. This function is best called by the entity itself, and
            throws an exception if the entity is a ghost. If the callback function
            onDestroy() is implemented, it is executed.
            """
            pass

        def destroySpace(self):
            """Destroys the space this entity is in."""
            pass

        def entitiesInView(self, pending: bool) -> List[ICellEntity]:
            """
            Get a list of entities in the View scope of this entity.

            parameters:
                pending	bool, optional parameter, the default is False, only all
                    entities visible to the client are returned, otherwise all
                    entities visible to the server but not synchronized to the
                    client are returned.
            """
            return []

        def entitiesInRange(self, range: float,
                            entityType: Optional[str] = None,
                            position: Optional[Vector3] = None):
            """
            Search for entities within a given distance. This is a spherical search.
            The distances of the three axes must be measured. This can find entities
            that are outside the View scope of this entity, but cannot find
            entities in other cells.

            Example:
                self.entitiesInRange( 100, 'Creature', (100, 0, 100) )

            Searches for a list of entities of type 'Creature' (an instantiated
            entity of a subclass of 'Creature'). The center point is (100, 0, 100)
            and the search radius is 100 meters.

            [ e for e in self.entitiesInRange( 100, None, (100,0,100) ) if isinstance( e, BaseType ) ]

            Gives a list of entities instantiated from subclasses of 'BaseType'.

            parameters:
                range	Search distance around this entity, float type
                entityType	An optional string parameter, the entity's type name,
                    used to match entities. If the entity type is a valid class
                    name (valid entities are ones listed in /scripts/entities.xml)
                    only this type of entity will be returned, otherwise all
                    entities in this range will be returned.
                position	Optional Vector3 type parameter, which is the center of the search radius is centered on the entity itself by default.

            returns:
                A list of Entityobjects in a given range.
            """
            pass

        def isReal(self) -> bool:
            """This function returns whether the Entity is real or a ghost.

            This function is rarely used but is useful for debugging.

            returns:
                bool, True if real, otherwise False.
            """
            return False

        def moveToEntity(self, destEntityID: int, velocity: float, distance: float,
                         userData: Optional[int] = None,
                         faceMovement: Optional[bool] = None,
                         moveVertically: Optional[bool] = None,
                         offsetPos: Optional[Vector3] = None) -> int:
            """Moves the Entity straight to another Entity position.

            Any Entity can only have one motion controller at any time. Repeatedly
            calling any move function will terminate the previous move controller.
            This function will return a controller ID that can be used to cancel
            this move.

            For example, Entity.cancelController( movementID ). You can also cancel
            the move using Entity.cancelController( "Movement" ). The callback
            function will not be called if the move is cancelled.

                def onMove( self, controllerID, userData ):
                def onMoveOver( self, controllerID, userData ):
                def onMoveFailure( self, controllerID, userData ):

            References:
            Entity.cancelController

            parameters:
                destEntityID	int, the ID of the target Entity
                velocity	float, speed of the Entity move, in m/s
                distance	float, distance target that when reached the entity
                    will stop moving, if the value is 0, it moves to the target
                    position.
                userData	object, optional parameter, when the callback function
                    is invoked the userData parameter will be this value.
                faceMovement	bool, optional parameter, True if the entity faces
                    the direction of the move. If it is other mechanism, it is False.
                moveVertically	bool, optional parameter, set to True to move in
                    a straight line, set to False means to move in a straight line
                    parallel to the ground.
                offsetPos	Vector3, optional parameter, Set a certain offset value,
                    such as moving the target position to the left of the entity.

            returns:
                int, newly created controller ID.
            """
            return -1

        def moveToPoint(self, destination: Vector3, velocity: float, distance: float,
                        userData: Optional[int] = None,
                        faceMovement: Optional[bool] = None,
                        moveVertically: Optional[bool] = None) -> int:
            """Move the Entity to the given coordinate point in a straight line.

            The callback function is invoked on success or failure.
            Any Entity can only have one motion controller at any time. Repeatedly
            calling any move function will terminate the previous move controller.
            Returns a controller ID that can be used to cancel this move.

            For example:
            Entity.cancelController( movementID ). You can also cancel the move
            with Entity.cancelController( "Movement" ). The callback function will
            not be called if the move is cancelled.

            The callback function is defined as follows:

                def onMove( self, controllerID, userData ):
                def onMoveOver( self, controllerID, userData ):
                def onMoveFailure( self, controllerID, userData ):

            See:
                Entity.cancelController

            parameters:
                destination	Vector3, the target point to which the Entity is to be
                    moved
                velocity	float, Entity's moving speed, in m/s
                distance	float, distance target that when reached the entity
                    will stop moving, if the value is 0, it moves to the target
                    position.
                userData	object, data passed to the callback function
                faceMovement	bool, True if the entity faces the direction of
                    the move. If it is other mechanism, it is false.
                moveVertically	bool, set to True to move in a straight line, set
                    to False means to move in a straight line parallel to the ground.

            returns:
                int, newly created controller ID.
            """
            return -1

        def getViewRadius(self) -> float:
            """This function returns the current View radius value of this Entity.

            Data can be set via Entity.setViewRadius( radius, hyst ).

            returns:
                float, View radius
            """
            return 0.0

        def getViewHystArea(self) -> float:
            """
            This function returns the current lag area value of this Entity View.

            Data can be set via Entity.setViewRadius( radius, hyst ).

            returns:
                float, The current lag area value of this Entity's View.
            """
            return 0.0

        def getRandomPoints(self, centerPos: Vector3, maxRadius: float,
                            maxPoints: int, layer: int) -> Tuple[Vector3]:
            """
            This function is used to get an array of random coordinate point
            that Entity.navigate can reach in a certain area centered on a certain
            coordinate point.

            parameters:
                centerPos	Vector3, Entity center coordinates
                maxRadius	float, the maximum search radius
                maxPoints	uint32, the maximimum number of random coordinate points returned.
                layer	int8, layer of navmesh to search.

            returns:
                tuple, an array of one or more coordinates.
            """
            return tuple()

        def navigate(self, destination: Vector3, velocity: float, distance: float,
                     maxMoveDistance: float, maxSearchDistance: float,
                     faceMovement: bool, layer: int, userData: Union[int, None]) -> int:
            """Use the navigation system to move this Entity to a target point.

            A callback will be invoked on success or failure.
            KBEngine can have several pre-generated navigation meshes with different
            mesh sizes (leading to different navigation paths).
            Any Entity can only have one motion controller at any time. Repeatedly
            calling any move function will terminate the previous move controller.
            Returns a controller ID that can be used to cancel this move.

            For example:
                Entity.cancelController( movementID )
            You can also cancel the movement controller with
            Entity.cancelController( "Movement" ). The callback function will not
            be called if the move is cancelled.

            The callback functions are defined as follows:

                def onMove( self, controllerID, userData ):
                def onMoveOver( self, controllerID, userData ):
                def onMoveFailure( self, controllerID, userData ):

            See:
                Entity.cancelController

            parameters:
                destination	Vector3, the target point where the Entity moves.
                velocity	float, Entity's move speed, in m/s
                distance	float, distance target that when reached the entity will stop moving, if the value is 0, it moves to the target position.
                maxMoveDistance	float, the maximum move distance
                maxSearchDistance	float, the maximum search distance from the navigatio ndata.
                faceMovement	bool, True if the entity faces the direction of the move (default). Otherwise False.
                layer	int8, navmesh layer to search
                userData	object, the data passed to the callback function

            returns:
                int, the newly created controller ID.
            """
            return -1

        def navigatePathPoints(self, destination: Vector3, maxSearchDistance: float,
                               layer: int):
            """
            This functions returns a list of path points from the current Entity
            location to the destination.

            parameters:
                destination	Vector3, target point where the Entity moves
                maxSearchDistance	float, the maximum search distance
                layer	int8, navmesh layer to search for a path on.
            """
            pass

        def setViewRadius(self, radius: float, hyst: float):
            """Specifies the size of the Entity's View.

            This function can only be used by Witness related entities.

            Note: You can set the default View radius by setting the kbengine.xml configuration option 'cellapp/defaultViewRadius'.

            The View radius can't be greater than 500.0 by default. For details, please see the kbengine_defaults.xml configuration option 'cellapp/entity_posdir_updates'.

            Data can be obtained with Entity.getViewRadius( ) and Entity.getViewHystArea( ).

            parameters:
                radius	float, specifies the radius of the View area
                hyst	float, specifies the size of the lag area of the View.
                    A reasonable setting of the lag area will reduce the sensitivity
                    of View collisions and reduce CPU consumption. Views where one
                    entity enters another entity must span the View radius area,
                    but entities that leave the View area need to move out of the
                    View radius area including the lag area.
            """
            pass

        def teleport(self, nearbyMBRef: ICellRemoteCall,
                     position: Tuple[float, float, float],
                     direction: Tuple[float, float, float]):
            """
            Instantly move an Entity to a specified space. This function allows
            you to specify the position and orientation of the entity after is has
            been moved.

            If you need to jump in different spaces (usually for different scene
            or room jumps), you can pass a CellRemoteCall to this function (the
            entity corresponding to the entityCall must be in the destination Space).

            This function can only be called on real entities.

            parameters:
                nearbyMBRef	A CellRemoteCall (the entity corresponding to this
                    entityCall must be in the destination Space ) that determines
                    which Space an Entity is to jump to. It is considered to be
                    the transfer destination. This can be set to None, in which
                    case it will teleport on the current cell.
                position	A sequence of 3 floats (x, y, z), the coordinates of
                    where to teleport the Entity .
                direction	A sequence of 3 floats (roll, pitch, yaw),
                    the orientation of the Entity after teleportation.
            """
            pass

        def writeToDB(self, shouldAutoLoad: bool, dbInterfaceName: str):
            """
            This function saves the data related to this entity to the database,
            including the data of the base entity. The onWriteToDB function of
            the base entity is called before the data is passed to the database.

            The data of the cell entity is also backed up in the base entity to
            ensure that the data is up-to-date when crash recovery data is encountered

            This function can only be called on real entities, and the entity must
            exist in the base section.

            parameters:
                shouldAutoLoad	bool, optional parameter, specifies whether this
                    entity needs to be loaded from the database when the service starts.

                    Note: The entity is automatically loaded when the server starts. The default is to call createEntityAnywhereFromDBID to create an entity to a minimally loaded baseapp. The entire process will be completed before the first started baseapp calls onBaseAppReady.

                    The script layer can reimplement the entity creation method in
                    a customized script (kbengine_defaults.xml->baseapp->entryScriptFile definition),
                    for example:

                        def onAutoLoadEntityCreate(entityType, dbid):
                            KBEngine.createEntityFromDBID(entityType, dbid)

                dbInterfaceName	string, optional parameter, specified by a database
                    interface, uses the interface name "default" by default.
                    The database interface is defined in kbengine_defaults.xml->dbmgr->databaseInterfaces.
            """
            pass

        def getWitnesses(self) -> Tuple[ICellEntity]:
            """This function returns all other entities(Players) that observe this Entity.

            returns:
                tuple, an array of zero or more Entity.
            """
            return tuple()

        def getComponent(self, componentName: str, all: bool) -> Union[ICellEntityComponent, tuple[ICellEntityComponent]]:
            """Gets a component instance of the specified type attached to the entity.

            parameters:
                componentName	string, The component type name.
                all	bool, if True, Returns all instances of the same type of component,
                    otherwise only returns the first or empty list.
            """
            return tuple()

        def fireEvent(self, eventName: str, *args: Any):
            """Trigger entity events.

            parameters:
                eventName	string, the name of the event to trigger.
                args	The event datas to be attached, variable parameters.
            """

        def registerEvent(self, eventName: str, callback: Callable):
            """Register entity events.

            parameters:
                eventName	string, the name of the event to be registered for listening.
                callback	The callback method used to respond to the event when the event fires.
            """

        def deregisterEvent(self, eventName: str, callback: Callable):
            """Deregister entity events.

            parameters:
                eventName	string, the name of the event to be deregister.
                callback	The callback method to deregister of the listener.
            """

        def onDestroy(self):
            """
            If this function is implemented in a script, it is called after
            Entity.destroy() destroys this entity. This function has no parameters.
            """
            pass

        def onEnterTrap(self, entity: ICellEntity, rangeXZ: float, rangeY: float,
                        controllerID: int, userArg: Optional[int] = None):
            """
            When a scope trigger is registered using Entity.addProximity and
            another entity enters the trigger, this callback function is called.

            parameters:
                entity	Entity that has entered the area
                rangeXZ	float, the size of the xz axis of the trigger, must be
                    greater than or equal to zero.
                rangeY	float, the size of the y-axis height of the trigger, must
                    be greater than or equal to zero.
                    It should be noted that for this parameter to take effect you
                    must enable kbengine_defaults.xml->cellapp->coordinate_system->rangemgr_y
                    Opening y-axis management will increase CPU consumption, because
                    some games have a large number of entities at the same y-axis
                    height or on the ground at nearly the same height. Because of
                    this, the collision becomes very dense. 3D space games or small
                    room-type games are more suitable for enabling this option.
                controllerID	 The controller id of this trigger.
                userArg	The value of the parameter given by the user when calling
                    addProximity, the user can decide how to use this parameter.
            """
            pass

        def onEnteredView(self, entity: ICellEntity):
            """
            If this function is implemented in a script, when an entity enters
            the View scope of the current entity, this callback is triggered.

            parameters:
                entity	  The entity which has entered the View scope.
            """
            pass

        def onGetWitness(self):
            """
            If this function is implemented in a script, it is called when the
            entity has a Witness bound to it.

            You can also access the entity property Entity.hasWitness to get the
            current state of the entity.
            """
            pass

        def onLeaveTrap(self, entity: ICellEntity, rangeXZ: float, rangeY: float,
                        controllerID: int, userArg: Optional[int] = None):
            """
            If this function is implemented in a script, it is triggered when an
            entity leaves the trigger area registered by the current entity. The
            scope trigger is registered with Entity.addProximity.

            parameters:
                entity	The entity that has left the trigger area.
                rangeXZ	float, the size of the xz axis of the trigger, must be
                    greater than or equal to zero.
                rangeY	float, the size of the y-axis height of the trigger, must
                    be greater than or equal to zero.
                    It should be noted that for this parameter to take effect you
                    must enable kbengine_defaults.xml->cellapp->coordinate_system->rangemgr_y
                    Opening y-axis management will increase CPU consumption, because
                    some games have a large number of entities at the same y-axis
                    height or on the ground at nearly the same height. Because of
                    this, the collision becomes very dense.
                    3D space games or small room-type games are more suitable for enabling this option.
                controllerID	  The controller ID of this trigger.
                userArg	The value of the parameter given by the user when calling addProximity, the user can decide how to use this parameter.
            """
            pass

        def onLoseControlledBy(self, id: int):
            """
            If this function is implemented in a script, this callback is triggered
            when this entity loses the Entity.controlledBy entity.

            parameters:
                id	  ID of the controlledBy entity.
            """
            pass

        def onLoseWitness(self):
            """
            If this function is implemented in a script, the callback is triggered
            whe this entity loses a Witness.

            You can also access that Entity.hasWitness property to get the current
            state.
            """
            pass

        def onMove(self, controllerID: int, userData: Optional[int] = None):
            """
            If this function is implemented in the script, the callback is invoked
            each frame when moved after a call to Entity.moveToPoint,
            Entity.moveToEntity, or Entity.navigate.

            parameters:
                controllerID	  The controller ID associated with the move.
                userData	  The parameter given by the user when requesting to
                    move the entity.
            """
            pass

        def onMoveOver(self, controllerID: int, userData: Optional[int] = None):
            """
            If this callback function is implemented in a script, it is invoked
            after a call to Entity.moveToPoint, Entity.moveToEntity, or
            Entity.navigate when this entity reaches the target point.

            parameters:
                controllerID	  The controller ID associated with the move.
                userData	  This parameter value is given by the user when requesting to move an entity.
            """
            pass

        def onMoveFailure(self, controllerID: int, userData: Optional[int] = None):
            """
            If this function is implemented in the script, this callback is invoked
            after a call to Entity.moveToPoint, Entity.moveToEntity, or
            Entity.navigate if the movement has failed.

            parameters:
                controllerID	  The controller ID associated with the move.
                userData	  This parameter value is given by the user when
                    requesting to move an entity.
            """
            pass

        def onRestore(self):
            """
            If this callback function is implemented in a script, it is invoked
            when the Cell application crashes and recreates the entity on another
            cellapp. This function has no arguments.
            """
            pass

        def onSpaceGone(self):
            """
            If this callback function is implemented in the script, it will be
            called when the current entity's Space is destroyed. This function has
            no parameters.
            """
            pass

        def onTurn(self, controllerID: int, userData: Optional[int] = None):
            """
            If this callback function is implemented in a script, it will be called
            after reaching the specified yaw. (related to Entity.addYawRotator)

            parameters:
                controllerID	  The controller ID returned by Entity.addYawRotator.
                userData	  This parameter value is given by user when requesting to move an entity.
            """
            pass

        def onTeleport(self):
            """
            If this callback function is implemented in a script, it will be called
            at the moment before the (Real) entity is transmitted in the entity
            transfer that occurs through the baseapp's Entity.teleport call.

            Note: Calling teleport on the entity's cell section does not trigger
            this callback, if you need this feature please invoke this callback
            after a call to Entity.teleport.
            """
            pass

        def onTeleportFailure(self):
            """
            If this callback function is implemented in a script, it will be called
            after a call to Entity.teleport if the teleport has failed.
            """
            pass

        def onTeleportSuccess(self, nearbyEntity: ICellEntity):
            """
            If this callback function is implemented in a script, it is invoked
            after a succesful call to Entity.teleport

            parameters:
                nearbyEntity	  This parameter is given by the user when calling
                    Entity.teleport. This is a real entity.
            """
            pass

        def onTimer(self, timerHandle: int, userData: Optional[int] = None):
            """
            This function is called when a timer associated with
            this entity is triggered.

            A timer can be added using the Entity.addTimer function.

            parameters:
                    timerHandle	The id of the timer.
                    userData	integer, User data passed in on Entity.addTimer.
            """
            pass

        def onUpdateBegin(self):
            """Invoked when a synchronization frame begins."""
            pass

        def onUpdateEnd(self):
            """Invoked after a synchronization frame has completed."""
            pass

        def onWitnessed(self, isWitnessed: bool):
            """
            If this callback function is implemented in a script, it is called when
            this entity enters the View area of another entity bound to a Witness
            (also can be understood as when this entity is observed by a client).
            This function can be used to activate the entity's AI when it is
            observed, and stopping AI execution when the entity ceases to be
            observed, thus reducing CPU consumption of the server to increase
            efficiency.

            parameters:
                isWitnessed	  bool, True if the entity is observed and False when
                    the entity is not observed. You can also access the entity
                    property Entity.isWitnessed to get the current state of the entity.
            """
            pass

        def onWriteToDB(self):
            """
            If this callback function is implemented in a script, it is called when
            the entity is about to be archived into the database.
            """
            pass

        @property
        def allClients(self) -> IAllClientRemoteCall:
            """
            By calling the entity's remote client methods through this attribute,
            the engine broadcasts the message to all other entities bound to
            a client that are within this entity's View area (including its own
            client, and the entity bound to the client is usually the player)

            Example:
                Avatar has player A, player B, and monster C in the View range.
                avatar.allClients.attack(monsterID, skillID, damage)

                At this point, the player himself, player A's, and player B's
                clients will all call the entity's attack method, and their client
                can invoke the specified skill's attack action to perform.

            Other references:
                Entity.clientEntity
                Entity.otherClients
            """
            return IAllClientRemoteCall()

        @property
        def base(self) -> Optional[IBaseRemoteCall]:
            """base is the entityCall used to contact the base Entity.

            This attribute is read-only and is None if the entity has no associated
            base Entity.

            Other references:
                Entity.clientEntity
                Entity.allClients
                Entity.otherClients

            Type:
                Read-only, ENTITYCALL
            """
            return IBaseRemoteCall()

        @property
        def className(self) -> str:
            """The class name of the entity.

            Type:
                Read-only, string
            """
            return ''

        @property
        def client(self) -> Optional[IClientRemoteCall]:
            """client is the entityCall used to contact associated client.

            This attribute is read-only, and is None if this entity does not have
            an associated client.

            Other references:
            Entity.clientEntity
            Entity.allClients
            Entity.otherClients

            Type:
            Read-only, ENTITYCALL
            """
            return IClientRemoteCall()

        @property
        def controlledBy(self) -> Optional[IBaseRemoteCall]:
            """
            If this attribute is set to the BaseRemoteCall of the server-side
            entity associated with a client, this entity is controlled by the
            corresponding client to move. If the attribute is None, the entity
            is moved by the server. When the client logs in and calls giveClientTo
            on this entity, this attribute is automatically set to its own BaseRemoteCall.

            Scripts can flexibly control the movement of the entity by the server
            or by the client (its own client or give control to other clients).

            Other references:
                Entity.onLoseControlledBy

            Type:
                BaseRemoteCall
            """
            return IBaseRemoteCall()

        @property
        def direction(self) -> Vector3:
            """This attribute describes the orientation of the Entity in world space.

            Users can change this attribute and the data will be synchronized to
            the client.

            Example: self.direction.y = 1.0 self.direction.z = 1.0

            Type:
                Vector3, which contains (roll, pitch, yaw) in radians.
            """
            return Vector3()

        @direction.setter
        def direction(self, value: Vector3):
            pass

        @property
        def hasWitness(self) -> bool:
            """
            If this read-only attribute is True, it means that the entity has
            already bound a Witness. If the entity is bound to Witness, the client
            can obtain information from the entity's view scope. Otherwise, False.

            Type:
                Read-only, bool
            """
            return False

        @property
        def id(self) -> int:
            """id is the id of the Entity object.

            This id is an integer that is the same between base, cell, and client associated entities. This attribute is read-only.

            Type:
                Read-only, int32
            """
            return -1

        @property
        def isDestroyed(self) -> bool:
            """
            If this attribute is True, this Entity has already been destroyed.

            Type:
                Read-only, bool
            """
            return False

        @property
        def isOnGround(self) -> bool:
            """
            If the value of this attribute is True, the Entity is on the ground,
            otherwise it is False.

            Type:
                Read-only, bool
            """
            return False

        @property
        def isWitnessed(self) -> bool:
            """
            If the current entity is in the View scope of another entity bound
            to Witness (can also be understood as an entity observed by a client),
            this property is True, otherwise it is False.

            Other references:
                Entity.onWitnessed

            Type:
                Read-only, bool
            """
            return False

        @property
        def layer(self) -> int:
            """
            A space can load multiple navmesh data at the same time. Different
            navmesh can be in different layers. Different layers can be abstracted
            into the ground, the water surface, and so on. This attribute determines
            which layer an entity exists in.

            Reference:
                KBEngine.addSpaceGeometryMapping

            Type:
                int8
            """
            return -1

        @layer.setter
        def layer(self, value: int):
            pass

        @property
        def otherClients(self) -> IOtherClientRemoteCall:
            """
            By calling the entity's remote client methods through this property,
            the engine broadcasts the message to all other entities bound to the
            cliend within this entity's View scope (Not including its own client.
            The entity bound to the client is usually the player.).

            Example:
                avatar has player A, player B, and monster C in the View range.
                avatar.otherClients.attack(monsterID, skillID, damage)

                At this point, player A's and player B's client will call the entity attack method, and their client can invoke the specified skill's attack action to perform.

            Other references:
                Entity.clientEntity
                Entity.otherClients
            """
            return IOtherClientRemoteCall()

        @property
        def position(self) -> Vector3:
            """The coordinates of this entity in world space (x, y, z).

            This attribute can be changed by the user and will be synchronized to
            the client after the change. It is important to note that this attribute
            should not be referenced. Referencing this attribute is likely to
            incorrectly modify the real coordinates of the entity.

            Example:
                self.position.y = 10.0

            If you want to copy this attribute value you can do the following:

                import Math
                self.copyPosition = Math.Vector3( self.position )

            Type:
                Vector3
            """
            return Vector3()

        @position.setter
        def position(self, value: Vector3):
            pass

        @property
        def spaceID(self) -> int:
            """This attribute is the ID of the space in which the entity is located.

            The cell and client ids are the same.

            Type:
                Read-only, Integer
            """
            return -1

        @property
        def topSpeed(self) -> float:
            """The maximum xz movement speed of the entity (m/s).

            This attribute is usually larger than the actualy movement speed.
            The server checks the client's movement legality through this attribute.
            If the movement distance excedes the speed limit, it is forced back
            to the previous position.

            Other references:
                Entity.topSpeedY

            Type:
                float
            """
            return 0.0

        @topSpeed.setter
        def topSpeed(self, value: float):
            pass

        @property
        def topSpeedY(self) -> float:
            """The maximum y-axis movement speed of the entity (m/s).

            This attribute is usually larger than the actualy movement speed.
            The server checks the client's movement legality through this attribute.
            If the movement distance excedes the speed limit, it is forced back to
            the previous position.

            Other references:
                Entity.topSpeed

            Type:
                float
            """
            return 0.0

        @topSpeedY.setter
        def topSpeedY(self, value: float):
            pass

        @property
        def volatileInfo(self) -> Tuple[float, float, float, float]:
            """This attribute specifies the Entity's volatile data synchronization policy.

            Volatile data includes the coordinate position of the entity and the
            orientation of the entity. Since volatile data is easily changed,
            the engine uses a set of optimized solutions to synchronize it to the
            client.

            This attribute is four floats (position, yaw, pitch, roll) that
            represents the distance value, and the server synchronizes the relevant
            data to it when an entity reaches a close distance. If the distance
            value is larger than the View radius, it means that it is always synchronized

            There is also a special bool attribute that is optimized. Its role is
            to control whether or not the server is optimized for synchronization.
            The current main optimization is the Y axis. If true, the server does
            not synchronize the y-axis coordinates of the entity when some actions
            (e.g., navigate) cause the server to determine the entity is on the
            ground. This can save a lot of bandwidth when synchronizing a large
            number of entities. The default is true.

            Users can also set the synchronization policies for different entities in .def:

            <Volatile>
                <position/>           <!-- always synchronize -->
                <yaw/>                <!-- always synchronize -->
                <pitch>20</pitch>     <!-- synchronize within 20m or less -->
                <optimized> true </optimized>
            </Volatile>               <!-- roll is always synchronized if not specified  -->

            Type:
                sequence, four floats (float, float, float, float)
            """
            return 0.0, 0.0, 0.0, 0.0


class IBaseEntity:

    if not IN_THE_ENGINE:

        def addTimer(self, initialOffset: float, repeatOffset: float = 0.0, userArg: int = 0) -> int:
            """Register a timer.

            The timer is triggered by the callback function onTimer, which will be
            executed the first time after "initialOffset" seconds, and then
            executed once every "repeatOffset" seconds. A "userArg" parameter can
            be set (integer only).

            The onTimer function must be defined in the base part of the entity
            with two parameters. The first is an integer, the timer id (which can
            be used to remove the timer's "delTimer" function), and the second is
            the user parameter "userArg".

            Example:

            ```
            # Here is an example of using addTimer
            import KBEngine

            class MyBaseEntity( KBEngine.Entity ):

                def __init__( self ):
                    KBEngine.Entity.__init__( self )

                    # Add a timer, trigger for the first time after 5 seconds, and
                    # execute once per second afterwards. The user parameter is 9.
                    self.addTimer( 5, 1, 9 )

                    # Add a timer and execute it once after 1 second. The default
                    # user parameter is 0.
                    self.addTimer( 1 )

                # Entity timer callback "onTimer" is called
                def onTimer( self, id, userArg ):
                    print "MyBaseEntity.onTimer called: id %i, userArg: %i" % ( id, userArg )
                    # If this is a repeated timer, when the timer is no longer
                    # needed, call the following function to remove it:
                    #     self.delTimer( id )

            ```

            parameters:
                    initialOffset	float, specifies the time interval in seconds
                        for the timer to trigger the first callback.
                    repeatOffset	float, specifies the time interval (in seconds)
                        after each execution of the first callback execution. You
                        must remove the timer with the function delTimer, otherwise
                        it will continue to repeat. Values less than or equal to 0
                        will be ignored.
                    userArg	integer, specifies the value of the userArg parameter
                        when invoking the "onTimer" callback.

            returns:
                    integer, the internal id of the timer. This id can be used to
                        remove the timer using delTimer.
            """
            return 0

        def createCellEntity(self, cellRemoteCall: ICellRemoteCall):
            """Requests to create an associated entity in a cell.

            The information used to create the cell entity is stored in the entity's
            cellData attribute. The cellData attribute is a dictionary that
            corresponds to the default value in the entity's .def file, as well
            as the "position", "direction", and "spaceID" used to represent the
            entity's position and orientation (roll, pitch, yaw).

            parameters:
                cellRemoteCall	CellRemoteCall parameter that specifies which space
                to create this cell entity in.

            Only a direct CellRemoteCall may be used. If you have an entity's
            BaseRemoteCall, you cannot pass its baseRemoteCall.cell to this function.
            Instead, you must create a new function on the current entity's base
            that accepts a direct CellRemoteCall as a parameter and then calls
            this function using it.

            E.g.

            baseRemoteCallOfNearbyEntity.createCellNearSelf( self )

            On the nearby entity's base:

            def createCellNearSelf( self, baseRemoteCall ):
                baseRemoteCall.createCellNearHere( self.cell )

            On the current entity's base:

            def createCellNearHere( self, cellRemoteCall ):
                self.createCellEntity( cellRemoteCall )

            """
            pass

        def createCellEntityInNewSpace(self, cellappIndex: Optional[int] = None):
            """
            Create a space on the cellapp and create the cell of this entity into
            the new space. It requests to complete through cellappmgr.

            The information used to create the cell entity is stored in
            the entity's cellData attribute. This property is a dictionary.
            The default values in the corresponding entity's .def file
            also include "position", "direction", and "spaceID" for representing
            the entity's position and orientation (roll, pitch, yaw).

            parameters:
                cellappIndex	integer, if it is either None or 0, a cellapp
                    is dynamically selected by the engine load balancer. If it is
                    greater than 0, a space is created in the specified cellapp
                    Example: If you expect to open four cellapps, then the
                    cellappIndex needs to specify the index can be 1, 2, 3, 4,
                    if the actual running cellapp is less than 4, for example,
                    only 3, then the cellappIndex input 4 due to the number
                    of overflow 4 1, 5 2.

            Tip: This feature can be used in conjunction with KBEngine.setAppFlags
            (KBEngine.APP_FLAGS_NOT_PARTCIPATING_LOAD_BALANCING),
            for example: placing large map spaces in several fixed cellapps
            and setting these cellapps to not participate in load balancing,
            and other cellapps to place copy space. When the copyspace is created
            and the cellappIndex is set to 0 or None, the consumption of
            the copy map will not affect the large map process, thus ensuring
            the smoothness of the main scene.
            """
            pass

        def delTimer(self, id: Union[int, str]):
            """The function delTimer is used to remove a registered timer.

            The removed timer is no longer executed. Single-shot timers are
            automatically removed after the callback is executed, and it is not
            necessary to use the delTimer to remove it. If the delTimer function
            uses an invalid id (for example, has been removed), it will generate
            an error.

            A usage example is with the Entity.addTimer function.

            parameters:
                id	integer, which specifies the timer id to remove. If the
                    parameter is the string "All", all timers are removed at once.
            """
            pass

        def destroy(self, deleteFromDB: bool = False, writeToDB: bool = True):
            """This function destroys the base parts of the entity.

            If the entity has a cell part, then the user must first destroy the
            cell part, otherwise it will generate an error. To destroy the cell
            part of the entity, call a Entity.destroyCellEntity.

            It may be more appropriate to call self.destroy in the onLoseCell
            callback. This ensures that the base part of the entity is destroyed.

            parameters:
                deleteFromDB	If True, the entry associated with this entity in
                    the database will be deleted. This parameter defaults to False.
                writeToDB	If True, the archived attributes associated with this
                    entity will be written to the database. Only if this entity is
                    read for the database or uses Entity.writeToDB will it be
                    written to the database. This parameter is True by default,
                    but will be ignore when deleteFromDB is True.
            """
            if self.cell is not None:
                # эмуляция поведения движка в аналогичном случае
                msg = f'Avatar::destroy: id:{self.id} has cell, please destroyCellEntity() first!'
                raise Exception(msg)

        def destroyCellEntity(self):
            """destroyCellEntity requests destruction of the associated cell entity.

            This method will generate an error if there is no associated cell entity.
            """
            pass

        _WriteToDBCBType = Callable[[bool, Any], None]

        def writeToDB(self, callback: Optional[_WriteToDBCBType] = None,
                      shouldAutoLoad: Optional[bool] = None,
                      dbInterfaceName: Optional[bool] = None):
            """
            This function saves the entity's archive attributes to the database
            so that it can be loaded again when needed.

            Entities can also be marked as automatically loaded so that the entity will be re-created when the service is started.

            parameters:
            callback	This optional parameter is a callback function when the
                database operation is complete. It has two parameters. The first is
                a success or failure boolean flag, and the second is the base entity.
            shouldAutoLoad	This optional parameter specifies whether this entity
                needs to be loaded from the database when the service is started.
                Note: The entity is automatically loaded when the server starts.
                The default is to call createEntityAnywhereFromDBID to create an
                entity to a minimally loaded baseapp. The entire process will be
                completed before the first started baseapp calls onBaseAppReady.

                The script layer can reimplement the entity creation method in the
                personalization script (kbengine_defaults.xml->baseapp->entryScriptFile definition),
                for example:
                    def onAutoLoadEntityCreate(entityType, dbid):
                        KBEngine.createEntityFromDBID(entityType, dbid)
            dbInterfaceName	string, optional parameter, specified by a database
                interface, default is to use the "default" interface. Database
                interfaces are defined in kbengine_defaults.xml->dbmgr->databaseInterfaces.
            """
            pass

        def getComponent(self, componentName: str, all: bool) -> Union[IBaseEntityComponent, tuple[IBaseEntityComponent]]:
            """
            Gets a component instance of the specified type attached to the entity.

            parameters:
                componentName	string, The component type name.
                all	bool, if True, Returns all instances of the same type of component,
                    otherwise only returns the first or empty list.
            """
            return tuple()

        def fireEvent(self, eventName: str, *args: Any):
            """Trigger entity events.

            parameters:
                eventName	string, the name of the event to trigger.
                args	The event datas to be attached, variable parameters.
            """

        def registerEvent(self, eventName: str, callback: Callable):
            """Register entity events.

            parameters:
                eventName	string, the name of the event to be registered for listening.
                callback	The callback method used to respond to the event when the event fires.
            """

        def deregisterEvent(self, eventName: str, callback: Callable):
            """Deregister entity events.

            parameters:
                eventName	string, the name of the event to be deregister.
                callback	The callback method to deregister of the listener.
            """

        def onCreateCellFailure(self):
            """
            If this function is implemented in the script, this function is called
            when the cell entity fails to create. This function has no parameters.
            """
            pass

        def onDestroy(self):
            """
            If this callback function is implemented in a script, it is called
            after Entity.destroy() actually destroys the entity. This function has
            no parameters.
            """
            pass

        def onGetCell(self):
            """
            If this function is implemented in the script, this function is called
            when it gets a cell entity. This function has no parameters.
            """
            pass

        def onLoseCell(self):
            """
            If this function is implemented in the script, this function is called
            after its associated cell entity is destroyed. This function has no
            parameters.
            """
            pass

        def onPreArchive(self):
            """
            If this function is implemented in a script, it is called before the
            entity is automatically written to the database. This callback is
            called before the Entity.onWriteToDB callback. If the callback returns
            False, the archive operation is aborted. This callback should return
            True to continue the operation. If this callback does not exist, the
            archiving operation continues.
            """
            pass

        def onRestore(self):
            """
            If this function is implemented in a script, it is called when this
            Entity's application crashes and the Entity is recreated on other
            applications. This function has no parameters.
            """
            pass

        def onTimer(self, timerHandle: int, userData: int = 0):
            """This function is called when a timer associated with this entity is triggered.

            A timer can be added using the Entity.addTimer function.

            parameters:
                timerHandle	The id of the timer.
                userData	integer, User data passed in on Entity.addTimer.
            """
            pass

        def onWriteToDB(self, cellData: Dict[str, Any]):
            """
            If this function is implemented in the script, this function is called
            when the entity data is to be written into the database.

            Note that calling writeToDB in this callback will result in an infinite loop.

            parameters:
                cellData	Contains the cell properties that will be stored in
                    the database. cellData is a dictionary.
            """
            pass

        @property
        def cell(self) -> Optional[ICellRemoteCall]:
            """cell is the ENTITYCALL used to contact the cell entity.

            This property is read-only, and the property is set to None if this
            base entity has no associated cell.

            Type:
                Read-only ENTITYCALL
            """
            pass

        @property
        def cellData(self) -> Dict[str, Any]:
            """cellData is a dictionary property.

            Whenever the base entity does not create its cell entity,
            the properties of the cell entity are stored here.

            If the cell entity is created, these used values and cellData
            properties will be deleted. In addition to the attributes specified
            by the cell entity in the entity definition file, it also contains
            position, direction and spaceID.
            """
            return {}

        @property
        def className(self) -> str:
            """The class name of the entity.

            Type:
                Read-only string
            """
            return ''

        @property
        def client(self) -> Optional[IClientRemoteCall]:
            """client is the IRemoteCall used to contact the client.

            This attribute is read-only and is set to None if this base entity
            as no associated client.

            Type:
                Read-only ENTITYCALL
            """
            pass

        @property
        def databaseID(self) -> int:
            """databaseID is the entity's permanent ID (database id).

            This id is of type uint64 and is greater than 0. If it is 0 then the
            entity is not permanent.

            Type:
                Read-only int64
            """
            return -1

        @property
        def databaseInterfaceName(self) -> str:
            """
            databaseInterfaceName is the database interface name where the entity
            persists. The interface name is configured in kbengine_defaults->dbmgr.
            The entity must be persistent (databaseID>0) for this attribute to be
            available, otherwise an empty string is returned.

            Type:
                Read-only string
            """
            return ''

        @property
        def id(self) -> int:
            """id is the object id of the entity.

            This id is an integer that is the same between base, cell, and client
            associated entities. This attribute is read-only.

            Type:
                Read-only int32
            """
            return -1

        @property
        def isDestroyed(self) -> bool:
            """This attribute is True if the Entity has been destroyed.

            Type:
                bool
            """
            return True

        @property
        def shouldAutoArchive(self) -> bool:
            """This attribute determines the automatic archiving strategy.

            If set to True, AutoArchive will be available, if set to False
            AutoArchive will not be available. If set to KBEngine.NEXT_ONLY,
            automatic archiving will be available at the next scheduled time.
            This attribute will be set to false after the next archiving.

            Type:
                True, False or KBEngine.NEXT_ONLY
            """
            return False

        @shouldAutoArchive.setter
        def shouldAutoArchive(self, value: bool):
            pass

        @property
        def shouldAutoBackup(self) -> bool:
            """This attribute determines the automatic bacup strategy.

            If set to True, automatic backup will be available, if set to False,
            automatic backup will not be available. If set to KBEngine.NEXT_ONLY,
            automatic backup will be done at the next available predetermined time.
            After the next backup, this attribute will be set to False.

            Type:
                True, False or KBEngine.NEXT_ONLY
            """
            return False

        @shouldAutoBackup.setter
        def shouldAutoBackup(self, value: bool):
            pass


class IProxyEntity(IBaseEntity):

    if not IN_THE_ENGINE:

        def disconnect(self):
            """ Disconnect the client."""
            pass

        def getClientType(self) -> int:
            """This function returns the client type.

            returns:
                UNKNOWN_CLIENT_COMPONENT_TYPE = 0,
                CLIENT_TYPE_MOBILE = 1, // Mobile phone
                CLIENT_TYPE_WIN = 2, // PC, typically EXE clients
                CLIENT_TYPE_LINUX = 3 // Linux Application program
                CLIENT_TYPE_MAC = 4 // Mac Application program
                CLIENT_TYPE_BROWSER = 5, // Web applications, HTML5, Flash
                CLIENT_TYPE_BOTS = 6, // bots
                CLIENT_TYPE_MINI = 7, // Mini-Client
                CLIENT_TYPE_END = 8 // end
            """
            return 0

        def getClientDatas(self) -> Tuple[bytes, bytes]:
            """
            This function returns the data attached to the client when logging
            in and registering. This data can be used to expand the operating system.
            If a third-party account service is connected, this data is sent to
            the third-party service system through the interfaces process.

            returns:
                tuple, a tuple of 2 elements (login data bytes, registration data
                    bytes), the first element is the datas parameter passed in when
                    the client invokes the login, and the second element is passed
                    in when the client registers. Since they can store arbitrary
                    binary data, they all exist as bytes.
            """
            return b'', b''

        def giveClientTo(self, proxy: IProxyEntity):
            """
            The client's controller is transferred to another Proxy, the current
            Proxy must have a client and the target Proxy must have no associated
            client, otherwise it will cause an error.

            See also:
                Proxy.onGiveClientToFailure

            parameters:
                proxy	Control will be transferred to this entity.
            """
            pass

        def streamFileToClient(self, resourceName: str, desc: Optional[str] = None,
                               id: int = -1) -> int:
            """
            This function is similar to streamStringToClient() and sends a resource
            file to the client. The sending process operates on different threads
            so it does not compromise the main thread.

            See also:
                Proxy.onStreamComplete

            parameters:
                resourceName	The name of the resource to send, including the path.
                desc	An optional string that describes the resource sent to the client.
                id	A 16-bit id whose value depends entirely on the caller. If the
                    incoming -1 system will select an unused id in the queue. The
                    client can make resource judgments based on this id.

            returns:
                The id associated with this download.
            """
            return -1

        def streamStringToClient(self, data: str, desc: Optional[str] = None,
                                 id: int = -1) -> int:
            """Sends some data to the client bound to the current entity.

            If the client port data is cleared, this function can only be called
            when the client binds to the entity again. The 16-bit id is entirely
            up to the caller. If the caller does not specify this ID then the
            system will allocate an unused id. The client can make resource
            judgments based on this id.

            You can define a callback function (onStreamComplete) in a Proxy-derived
            class. This callback function is called when all data is successfully
            sent to the client or when the download fails.

            See also:
                Proxy.onStreamComplete
                client Entity.onStreamDataStarted
                Entity.onStreamDataRecv
                Entity.onStreamDataCompleted

            parameters:
                data	The string to send
                desc	An optional description string sent.
                id	A 16-bit id whose value depends entirely on the caller. If the incoming -1 system will select an unused id in the queue.

            returns:
                The id associated with this download.
            """
            return -1

        def onClientDeath(self):
            """
            If this callback is implemented in a script, this method will be
            called when the client disconnects. This method has no parameters.
            """
            pass

        def onClientGetCell(self):
            """
            If this callback is implemented in a script, the callback is called
            when the client can call the entity's cell attribute
            """
            pass

        def onClientEnabled(self):
            """
            If this callback is implemented in the script, it is invoked when the
            entity is available (various initializations and communication with
            the client). This method has no parameters.
            Note: giveClientTo also assigns control to the entity and causes the
            callback to be called.

            Внимание! Этот колбэк также срабатывает и на giveClientTo.
            """
            pass

        def onGiveClientToFailure(self):
            """
            If this callback is implemented in a script, it is called when the
            entity fails to call giveClientTo. This method has no parameters.
            """
            pass

        def onLogOnAttempt(self, ip: str, port: int, password: str):
            """
            If this callback is implemented in a script, it is invoked when a
            client attempts to log in using the current account entity.
            This situation usually happens when the entity that exists in memory
            is in a valid state, the most obvious example is user A logs in with
            this account, and user B tries to use the same account to log in,
            triggering this callback.

            This callback function can return the following constant values:
            KBEngine.LOG_ON_ACCEPT: Allows the new client to bind to the entity.
            If the entity has bound a client, the previous client will be kicked out.
            KBEngine.LOG_ON_REJECT: Reject new client entity binding.

            KBEngine.LOG_ON_WAIT_FOR_DESTROY: Wait for the entity to be destroyed
            before the client binds.

            parameters:
            ip	  The IP address of the client trying to log in.
            port	  The port to which the client attempted to log in.
            password	  The MD5 password used when the user logs in.
            """
            pass

        def onStreamComplete(self, id: int, success: bool):
            """
            If you implement this callback in a script, when a user uses
            Proxy.streamStringToClient() or Proxy.streamFileToClient() and is
            completed, this callback is invoked.

            parameters:
                id	  The id associated with the download.
                success	  Success or failure
            """
            pass

        @property
        def __ACCOUNT_NAME__(self) -> str:
            """
            If the proxy is an account, you can access __ACCOUNT_NAME__ to get
            the account name.
            """
            return ''

        @property
        def __ACCOUNT_PASSWORD__(self):
            """
            If the proxy is an account, you can access __ACCOUNT_PASSWORD__ to get
            the MD5 password.
            """
            return ''

        @property
        def clientAddr(self) -> Tuple[str, int]:
            """This is a tuple object that contains the client's ip and port."""
            return ('', -1)

        @property
        def clientEnabled(self) -> bool:
            """Whether the entity is already available.

            The script cannot communicate with the client until the entity is available.
            """
            return False

        @property
        def hasClient(self) -> bool:
            """Proxy is bound to a client connection."""
            return False

        @property
        def roundTripTime(self) -> int:
            """
            The average round-trip time for client communication between the server
            and this Proxy over a period of time. This property only takes effect
            under Linux.
            """
            return -1

        @property
        def timeSinceHeardFromClient(self) -> int:
            """
            The time (in seconds) that has passed since the client packet was
            last received.
            """
            return -1


class ICellEntityCoponentRemoteCall(IEntityCoponentRemoteCall):
    """API удалённых вызов на cell компонент компонента-сущности."""
    pass


class IBaseEntityCoponentRemoteCall(IEntityCoponentRemoteCall):
    """API удалённых вызов на base компонент компонента-сущности."""
    pass


class IClientEntityCoponentRemoteCall(IEntityCoponentRemoteCall):
    """API удалённых вызов на client компонент компонента-сущности."""
    pass


class IAllClientEntityCoponentRemoteCall(IClientEntityCoponentRemoteCall):
    """Интерфейс методов для .allClients атрибута компонента-сущности.

    Интерефейс аналогичный IClientEntityCoponentRemoteCall, т.к. теже самые методы.
    """


class IOtherClientsEntityCoponentCall(IClientEntityCoponentRemoteCall):
    pass


class IBaseEntityComponent:

    if not IN_THE_ENGINE:

        @property
        def client(self) -> Optional[IClientEntityCoponentRemoteCall]:
            pass

        @property
        def cell(self) -> Optional[ICellEntityCoponentRemoteCall]:
            return ICellEntityCoponentRemoteCall()

        @property
        def className(self) -> str:
            return ''

        @property
        def ownerID(self) -> int:
            """The object id of the component owner entity."""
            return 0

        @property
        def owner(self) -> IBaseEntity:
            """The entity object of the component owner."""
            return IBaseEntity()

        @property
        def name(self) -> str:
            "The name of entiry property points to this component."
            return ''

        def onTimer(self, tid: int, userArg: int):
            """
            KBEngine method.
            Engine callback timer triggered
            """

        def addTimer(self, start: float, interval: float = 0.0, userData: int = 0) -> int:
            return -1

        def delTimer(self, id: Union[int, str]):
            pass

        def onAttached(self, owner: IBaseEntity):
            """Called when attaching to the owner entity."""
            pass

        def onDetached(self, owner: IBaseEntity):
            """Called when removed from the owning entity."""
            pass

        def onClientEnabled(self):
            """
            KBEngine method.
            The entity is officially activated and available for use. At this
            time, the entity has already established the corresponding entity
            of the client, and its entity can be created here.
            cell part.
            """
            pass

        def onClientDeath(self):
            """
            KBEngine method.
            The client corresponding entity has been destroyed
            """


class ICellEntityComponent:

    # Похоже они не пробросили onTimer для cell (в атрибутах компонента на
    # cell я его не нашёл). Скорей всего onTimer уходит в сущность.
    #
    # [cellapp@python ~] >>> a.component1.onTimer
    # Traceback (most recent call last):
    # File "<string>", line 1, in <module>
    # AttributeError: 'Test' object has no attribute 'onTimer'
    #
    # def onTimer(self, tid, userArg):
    #     pass

    if not IN_THE_ENGINE:

        @property
        def client(self) -> Optional[IClientEntityCoponentRemoteCall]:
            pass

        @property
        def allClients(self) -> Optional[IAllClientEntityCoponentRemoteCall]:
            pass

        @property
        def otherClients(self) -> Optional[IOtherClientsEntityCoponentCall]:
            pass

        @property
        def base(self) -> Optional[IBaseEntityCoponentRemoteCall]:
            return IBaseEntityCoponentRemoteCall()

        def clientEntity(self, destID: int) -> Optional[ICellEntity]:
            """
            This method can access the method of an entity in its own client
            (the current entity must be bound to the client). Only the entities
            in the View scope will be synchronized to the client. It can only be
            called on a real entity.

            parameters:
                destID	integer, the ID of the target entity.
            """
            pass

        @property
        def name(self) -> str:
            return ''

        @property
        def isDestroyed(self) -> bool:
            return False

        @property
        def className(self) -> str:
            return ''

        @property
        def ownerID(self) -> int:
            """The object id of the component owner entity."""
            return 0

        @property
        def owner(self) -> ICellEntity:
            """The entity object of the component owner."""
            return ICellEntity()

        def addTimer(self, start: float, interval: float = 0.0, userData: int = 0) -> int:
            return -1

        def delTimer(self, id: Union[int, str]):
            pass

        def onAttached(self, owner: IBaseEntity):
            """Called when attaching to the owner entity."""
            pass

        def onDetached(self, owner: IBaseEntity):
            """Called when removed from the owning entity."""
            pass

        def onClientEnabled(self):
            """
            KBEngine method.
            The entity is officially activated and available for use. At this
            time, the entity has already established the corresponding entity
            of the client, and its entity can be created here.
            cell part.
            """
            pass

        def onClientDeath(self):
            """
            KBEngine method.
            The client corresponding entity has been destroyed
            """
