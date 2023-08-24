"""API модулей KBEngine для разных компонентов."""

import socket
from typing import Any, Callable, Dict, Optional, Type, Union, List, Tuple

from ._entityapi import IBaseEntity, ICellEntity, IProxyEntity, \
    IBaseRemoteCall, IBaseEntityComponent, ICellEntityComponent, IEntityCall


DBCallback = Callable[[List[List[str]], Optional[int], int, Optional[str]], None]
EntityOrMB = Union[IEntityCall, IBaseEntity]
CreateEntityFromDBIDCB = Callable[[Optional[EntityOrMB], int, bool], None]


class IKBEngineBaseModule:

    Entity = IBaseEntity
    Proxy = IProxyEntity
    EntityComponent = IBaseEntityComponent

    @staticmethod
    def addWatcher(path: str, dataType: str, getFunction: Callable):
        """
        Interacts with the debug monitoring system, allowing the user to
        register a monitoring variable with the monitoring system.

        Example:

        >>> def countPlayers( ):
        >>>     i = 0
        >>>     for e in KBEngine.entities.values():
        >>>     	if e.__class__.__name__ == "Avatar":
        >>>     		i += 1
        >>>     return i
        >>>
        >>> KBEngine.addWatcher( "players", "UINT32", countPlayers )

        This function adds a watch variable under the "scripts/players" watch
        path. The function countPlayers is called when the watcher observes.

        parameters:
            path	Create a monitored path.
            dataType	The value type of the monitor variable. Reference:
                Basic data types
            getFunction	This function is called when the observer retrieves
                the variable. This function returns a value representing a
                watch variable without arguments.
        """
        pass

    @staticmethod
    def address() -> str:
        """Returns the address of the internal network interface."""
        return ''

    @staticmethod
    def MemoryStream():
        """Returns a new MemoryStream object.

        The MemoryStreamobject stores binary information. This type is provided
        to allow the user to easily serialize and deserialize the Python base
        types following KBEngine underlying serialization rules.

        For example, you can use this object to construct a network packet
        that KBEngine can parse.

        Usage:

        >>> s = KBEngine.MemoryStream()
        >>> s
        >>> b''
        >>> s.append("UINT32", 1)
        >>> s.pop("UINT32")
        >>> 1

        The types that MemoryStream currently supports are only basic data types.
        Reference: Basic data types
        """
        pass

    @staticmethod
    def charge(ordersID: str, dbID: int, byteDatas: bytes, pycallback: Callable):
        """
        Billing interface.

        parameters:
            ordersID	string, order ID.
            dbID	uint64, the databaseID of the entity.
            byteDatas	bytes, with data, which is parsed and defined by the developer.
            pycallback	Billing callback.

        Billing callback prototype: (When calling KBEngine.chargeResponse in
        interfaces, the callback is called if an order is set to callback)
            def on*ChargeCB(self, orderID, dbID, success, datas):

        ordersID: string, OrderID
        dbID: uint64, usually the databaseID of the entity.
        success: bool, whether the order succeeded    datas: bytes, with data,
            parsed and defined by the developer.
        """
        pass

    @staticmethod
    def createEntityAnywhere(entityType: str, params: dict,
                             callback: Optional[Callable[[Optional[IBaseRemoteCall]], None]] = None):
        """Create a new base Entity.

        The server can choose any Baseapp to create an Entity. This method
        should be preferred over KBEngine.createEntityLocally so the server
        has the flexibility to choose a suitable Baseapp to create an entity.

        The function parameters need to provide the type of entity created,
        and there is also a Python dictionary as a parameter to initialize
        the entities value.

        The Python dictionary does not require the user to provide all of
        the properties, and the default values provided by the entity
        definition file ".def" are defaults.

        Example:

        params = {
            "name" : "kbe", # base, BASE_AND_CLIENT
            "HP" : 100,	# cell, ALL_CLIENT, in cellData
            "tmp" : "tmp"	# baseEntity.tmp
        }

        def onCreateRemoteCallback(entity)
            print(entity)

        createEntityAnywhere("Avatar", params, onCreateRemoteCallback)

        parameters:
            entityType	string, specifies the type of Entity to create. Valid
                entity types are listed in /scripts/entities.xml.
            params	optional parameter, a Python dictionary object. If a
                specified key is an Entity attribute, its value will be used
                to initialize the properties of this Entity. If the key is a
                Cell attribute, it will be added to the 'cellData' attribute
                of the Entity. This cellData' attribute is a Python dictionary
                and will be used later to initialize the attributes of the cell
                entity.
            callback	An optional callback function that is called when the
                entity is created. The callback function takes one argument,
                when the Entity is created successfully it is the entity's
                entityCall, on failure it is None.

        returns:
            Returns the entityCallof the Entity through the callback.
        """
        pass

    @staticmethod
    def createEntity():
        """KBEngine.createEntityLocally alias."""

    @staticmethod
    def createEntityRemotely(entityType: str, baseMB: IBaseRemoteCall,
                             params: Optional[Dict[str, Any]] = None,
                             callback: Optional[Callable[[IBaseRemoteCall], None]] = None):
        """Create a new Entity on the specified baseapp through the baseMB parameter.

        KBEngine.createEntityAnywhere should be preferred over this method to
        allow the server to decide which is the most suitable Baseapp to create
        the entity on for load balancing purposes.

        The function parameters need to provide the type of the created entity,
        and there is also a Python dictionary as a parameter to initialize
        the entity's value.

        This Python dictionary does not require the user to provide all of
        the properties, and the default values provided by the entity
        definition file ". def" are defaults.

        Example:

        params = {
            "name" : "kbe", # base, BASE_AND_CLIENT
            "HP" : 100,	# cell, ALL_CLIENT, in cellData
            "tmp" : "tmp"	# baseEntity.tmp
        }

        def onCreateRemoteCallback(entity)
            print(entity)

        createEntityRemotely("Avatar", baseRemoteCall, params, onCreateRemoteCallback)

        parameters:
            entityType	string, specifies the type of Entity to create. Valid
                entity types are listed in /scripts/entities.xml.
            baseMB	BaseRemoteCall which is a base Entity IRemoteCall. The
                entity will be created on the baseapp process corresponding
                to this entity.
            params	Optional parameters, a Python dictionary object. If a
                specified key is an Entity attribute, its value will be used
                to initialize the properties of this Entity. If this key is a
                Cell attribute, it will be added to the Entity's 'cellData'
                attribute. This 'cellData' attribute is a Python dictionary
                and will be used later to initialize the attributes of the
                cell entity.
            callback	An optional callback function that is called when
                the entity is created. The callback takes one argument, on success
                it is an Entity entityCall, on failure it is None.

        returns:
            Returns the Entity's entityCallthrough the callback.

        """
        pass

    @staticmethod
    def createEntityFromDBID(entityType: str,
                             dbID: int,
                             callback: Optional[CreateEntityFromDBIDCB] = None,
                             dbInterfaceName: Optional[str] = None):
        """
        Create an Entity by loading data from the database. The new Entity
        will be created on the Baseapp that called this function. If the Entity
        has been checked out from the database, a reference to this existing
        entity will be returned.

        parameters:
            entityType	string, specifies the Entity type to load. Valid entity
                types are listed in /scripts/entities.xml.
            dbID	Specifies the database ID of the entity to create. The
                database ID of this entity is stored in the entity's
                databaseID attribute.
            callback	An optional callback function that is called when the
                operation is complete. The callback function has three parameters:
                baseRef, databaseID, and wasActive. If the operation is
                successful, baseRef will be an entityCall or a direct reference
                to the newly created Entity. The databaseID will be the database
                ID of the entity. wasActive will be True if baseRef is a
                reference to an already existing entity (checked out from the
                database). If the operation fails the three parameters will be
                baseRef - None, databaseID - 0, wasActive - False.

                The most common reason for failure is that the entity does not
                exist in the database, but occasionally other errors such as
                timeouts or ID allocation failure.
            dbInterfaceName	string, optional parameter, specified by a database
                interface, and the "default" interface is used by default.
                Database interfaces are defined in
                kbengine_defaults.xml->dbmgr->databaseInterfaces.
        """
        pass

    @staticmethod
    def createEntityAnywhereFromDBID(entityType: str, dbID: int,
                                     callback: Optional[CreateEntityFromDBIDCB] = None,
                                     dbInterfaceName: Optional[str] = None):
        """Create an Entity by loading data from the database.

        The server may choose any Baseapp to create the Entity.

        Using this function will help BaseApps load balance.

        If the entity has been checked out from the database, a reference to
        the existing Entity will be returned.

        parameters:
            entityType	string, specifies the Entity type to load. Valid entity
                types are listed in /scripts/entities.xml.
            dbID	Specifies the database ID of the entity to create. The
                database ID of this entity is stored in the entity's databaseID
                attribute.
            callback	An optional callback function that is called when
                the operation is complete. The callback function has three
                parameters: baseRef, databaseID, and wasActive. If the
                operation is successful, baseRef will be an entityCall or a
                direct reference to the newly created Entity. The databaseID
                will be the database ID of the entity. wasActive will be True
                if baseRef is a reference to an already existing entity
                (checked out from the database). If the operation fails the
                three parameters will be baseRef - None, databaseID - 0, wasActive - False.

                The most common reason for failure is that the entity does not
                exist in the database, but occasionally other errors such as
                timeouts or ID allocation failure.
            dbInterfaceName	string, optional parameter, specified by a
                database interface, and the "default" interface is used by
                default. Database interfaces are defined in
                kbengine_defaults.xml->dbmgr->databaseInterfaces.

        returns:
        The Entity's entityCallthrough the callback.

        """
        pass

    @staticmethod
    def createEntityRemotelyFromDBID(entityType: str,
                                     dbID: int,
                                     baseMB: IBaseRemoteCall,
                                     callback: Optional[CreateEntityFromDBIDCB] = None,
                                     dbInterfaceName: Optional[str] = None):
        """
        Load data from the database and create an Entity on the baseapp
        specified via the baseMB parameter.

        If the entity has been checked out from the database, a reference to
        the existing Entity will be returned.

        parameters:
        entityType	string, specifies the Entity type to load. Valid entity
            types are listed in /scripts/entities.xml.
        dbID	Specifies the database ID of the entity to create. The database
            ID of this entity is stored in the entity's databaseID attribute.
        callback	An optional callback function that is called when the
            operation is complete. The callback function has three parameters:
            baseRef, databaseID, and wasActive. If the operation is successful,
            baseRef will be an entityCall or a direct reference to the newly
            created Entity. The databaseID will be the database ID of the
            entity. wasActive will be True if baseRef is a reference to an
            already existing entity (checked out from the database). If the
            operation fails the three parameters will be baseRef - None,
            databaseID - 0, wasActive - False.

            The most common reason for failure is that the entity does not
            exist in the database, but occasionally other errors such as
            timeouts or ID allocation failure.
        dbInterfaceName	string, optional parameter, specified by a database
            interface, and the "default" interface is used by default. Database
            interfaces are defined in kbengine_defaults.xml->dbmgr->databaseInterfaces.

        returns:
            Returns the Entity's entityCallthrough the callback.
        """
        pass

    @staticmethod
    def createEntityLocally(entityType: str, params: Dict[str, Any]) -> IBaseEntity:
        """Create a new Entity.

        The function parameters need to provide the type of the created entity,
        and there is also an optional Python dictionary as paramater to
        initialize the entity's values.

        The Python dictionary does not require the user to provide all of the
        properties, and the default values provided by the entity definition
        file ".def" are defaults.

        KBEngine.createEntityAnywhere should be preferred over this method
        to allow the server to decide which is the most suitable Baseapp to
        create the entity on for load balancing purposes.

        It should be noted that this method returns the entity instantly
        without a callback, and is also guaranteed to return a direct reference
        to the Entity object, rather than its IRemoteCall. It is suitable to
        use this method over KBEngine.createEntityAnywhere when you need to
        manage the entities life cycle (such as control when destroy is called
        on the entity) or access the entities attributes from the creating
        entity, because as described in the IRemoteCall documentation, it is
        not possible to access attributes or call methods not listed in the
        entity's def file using the IRemoteCall. This method is also necessary
        to use when you need a direct reference to an entity (as it's not
        possible to get one on a different baseapp). Many functions take an
        IRemoteCall as a parameter, but some require a direct reference to the
        entity (such as Proxy.giveClientTo).

        Example:

        params = {
            "name" : "kbe", # base, BASE_AND_CLIENT
            "HP" : 100,	# cell, ALL_CLIENT, in cellData
            "tmp" : "tmp"	# baseEntity.tmp
        }

        baseEntity = createEntityLocally("Avatar", params)

        parameters:
            entityType	string, specifies the type of entity to create. Valid
                entity types are listed in /scripts/entities.xml.
            params	optional parameter, a Python dictionary object. If a
                specified key is an Entity attribute, its value will be used
                to initialize the properties of this Entity. If the key is a
                Cell attribute, it will be added to the 'cellData' attribute
                of the Entity. This cellData' attribute is a Python dictionary
                and will be used later to initialize the attributes of the cell
                entity.

        returns:
            The newly created Entity.
        """
        return IBaseEntity()

    @staticmethod
    def debugTracing():
        """Outputs the Python extended object counter currently tracked by KBEngine.

        Extended objects include: fixed dictionary, fixed array, Entity, IRemoteCall...
        If the counter is not zero when the server is shut down normally, it
        means that the leak already exists and the log will output an error message.

        ERROR cellapp [0x0000cd64] [2014-11-12 00:38:07,300] - PyGC::debugTracing(): FixedArray : leaked(128)
        ERROR cellapp [0x0000cd64] [2014-11-12 00:38:07,300] - PyGC::debugTracing(): IRemoteCall : leaked(8)
        """
        pass

    @staticmethod
    def delWatcher(path):
        """
        Interacts with the debug monitoring system, allowing users to delete
        monitored variables in the script.

        parameters:
            path	The path to the variable to delete.
        """
        pass

    @staticmethod
    def deleteEntityByDBID(entityType: str, dbID: int,
                           callback: Optional[Callable[[Union[bool, IBaseRemoteCall]], None]] = None,
                           dbInterfaceName: Optional[str] = None):
        """
        Deletes the specified entity (including the child table data generated
        by the attribute) from the database. If the entity is not checked out
        from the database, the deletion is successful. If the entity has been
        checked out from the database, KBEngine will fail to delete and return
        the Entity's entityCall in the callback.

        parameters:
            entityType	string, specifies the type of Entity to delete. Valid
                entity types are listed in /scripts/entities.xml.
            dbID	Specifies the database ID of the entity to delete. The database
                ID of the entity is stored in the entity's databaseID
                attribute.databaseID
            callback	An optional callback, with only one parameter. When the
                entity has not been checked out from the database it will be
                deleted successfully and the parameter will be True. If the entity
                has been checked out from the database then the parameter is the
                Entity's entityCall.
            dbInterfaceName	String, optional parameter, specifies a database
                interface. By default it uses the "default" interface. Database
                interfaces are defined by kbengine_defaults.xml->dbmgr->databaseInterfaces.
        """
        pass

    @staticmethod
    def deregisterReadFileDescriptor(fileDescriptor: socket.socket):
        """
        Unregisters the callback registered with KBEngine.registerReadFileDescriptor.

        Example:
            http://www.kbengine.org/assets/other/py/Poller.py

        parameters:
            fileDescriptor	socket descriptor/file descriptor
        """
        pass

    @staticmethod
    def deregisterWriteFileDescriptor(fileDescriptor: socket.socket):
        """
        Unregisters the callback registered with KBEngine.registerWriteFileDescriptor.

        Example:
            http://www.kbengine.org/assets/other/py/Poller.py

        parameters:
            fileDescriptor	socket descriptor/file descriptor.
        """
        pass

    @staticmethod
    def executeRawDatabaseCommand(command: str,
                                  callback: Optional[DBCallback] = None,
                                  threadID: Optional[int] = None,
                                  dbInterfaceName: Optional[str] = None):
        """
        This script function executes a database command on the database,
        which is directly parsed by the relevant database.

        Please note that using this function to modify entity data may not be
        effective because if the entity has been checked out, the modified data
        will still be archived by the entity and cause overwriting.

        This function is strongly not recommended for reading or modifying entity data.

        parameters:
            command	This database command will be different for different
                database configuration scenarios. For a MySQL database it is
                an SQL query.
            callback

        Optional parameter, callback object (for example, a function) called
        back with the command execution result.
        This callback has 4 parameters: result set, number of rows affected,
        auto value, error message.

        Example:
            def sqlcallback(result, rows, insertid, error):
                print(result, rows, insertid, error)

            As the above example shows, the result parameter corresponds to the
            "result set", and the result set parameter is a row List. Each line
            is a list of strings containing field values. If the command execution
            does not return a result set (for example, a DELETE command), or the
            command execution encounters an error, the result set is None.

            The rows parameter is the "number of rows affected", which is an
            integer indicating the number of rows affected by the command execution.
            This parameter is only relevant for commands that do not return results
            (such as DELETE).
            This parameter is None if there is a result set return or if there is
            an error in the command execution.

            The insertid is a long value, similar to an entity's databaseID. When
            successfully inserting data int a table with an auto long type field,
            it returns the data at the time of insertion.
            More information can be found in mysql's mysql_insert_id() method. In
            addition, this parameter is only meaningful when the database type is
            mysql.

            Error corresponds to the "error message", when the command execution
            encounters an error, this parameter is a string describing the error.
            This parameter is None when the command execution has not occurred.

        threadID	int32, optional parameter, specifies a thread to process
            this command. Users can use this parameter to control the execution
            order of certain commands (dbmgr is multi-threaded). The default is
            not specified. If threadId is the ID of an entity, it will be added
            to the entity's archive queue and written by the thread one by one.
        dbInterfaceName	string, optional parameter, specifies a database
            interface. By default it uses the "default" interface. Database
            interfaces are defined by kbengine_defaults.xml->dbmgr->databaseInterfaces.
        """
        pass

    @staticmethod
    def genUUID64():
        """This function generates a 64-bit unique ID.

        Note: This function depends on the baseapp server process startup
        parameter 'gus'. Please set the startup parameters to be unique.
        In addition, if gus exceeds 65535, this function can only remain
        unique for the current process.

        Usage:
        Unique IDs can be generated on multiple service processes and do not conflict.
        A room ID can be generated on multiple service processes and no
            uniqueness verification is required.

        returns:
            Returns a 64-bit integer.
        """
        pass

    @staticmethod
    def getResFullPath(res: str) -> str:
        """Get the absolute path of a resource.

        Note: Resource must be accessible under KBE_RES_PATH.

        parameters:
            res	string, the relative path of the resource

        returns:
            string, if there is an absolute path to the given resource,
                otherwise returns null.
        """
        return ''

    @staticmethod
    def getWatcher(path: str) -> Any:
        """Gets the value of a watch variable from the KBEngine debugging system.

        Example: In the Python console of baseapp1:
        >>>KBEngine.getWatcher("/root/stats/runningTime")
        12673648533

        >>>KBEngine.getWatcher("/root/scripts/players")
        32133

        parameters:
            path	string, the absolute path of the variable including the
            variable name (can be viewed on the GUIConsole watcher page).

        returns:
            The value of the variable.
        """
        pass

    @staticmethod
    def getWatcherDir(path: str) -> Tuple[str, ...]:
        """
        Get a list of elements (directories, variable names) under the watch
        directory from the KBEngine debugging system.

        Example: In the Python console of baseapp1 enter:
        >>>KBEngine.getWatcher("/root")
        ('stats', 'objectPools', 'network', 'syspaths', 'ThreadPool', 'cprofiles', 'scripts', 'numProxices', 'componentID',
         'componentType', 'uid', 'numClients', 'globalOrder', 'username', 'load', 'gametime', 'entitiesSize', 'groupOrder')

        parameters:
            path	string, the absolute path to this variable (can be viewd
                on the GUIConsole watcher page).

        returns:
            Monitors the list of elements in the directory (directory, variable
            name).
        """
        return tuple()

    @staticmethod
    def getAppFlags():
        """Get the flags of the current engine APP, Reference: KBEngine.setAppFlags.

        returns:
            KBEngine.APP_FLAGS_*
        """
        pass

    @staticmethod
    def hasRes(res: str) -> bool:
        """Use this interface to determine if a relative path exists.

        Note: Resource must be accessible under KBE_RES_PATH.

        Example:

        >>>KBEngine.hasRes("scripts/entities.xml")
        True

        parameters:
            res	string, the relative path of the resource

        returns:
            bool, True if relative path exists, otherwise False.
        """
        return False

    @staticmethod
    def isShuttingDown() -> bool:
        """Returns whether the server is shutting down.

        After the onBaseAppShutDown(state=0) is called, this function returns True.

        returns:
            True if the server is shutting down, otherwise False.
        """
        return False

    @staticmethod
    def listPathRes(path: str, extension: Optional[str] = None) -> Tuple[str, ...]:
        """Get a list of resources in a resource directory.

        Note: Resources must be accessible under KBE_RES_PATH.

        Example:

        >>>KBEngine.listPathRes("scripts/cell/interfaces")
        ('/home/kbe/kbengine/demo/res/scripts/cell/interfaces/AI.py',
         '/home/kbe/kbengine/demo/res/scripts/cell/interfaces/New Text Document.txt')

        >>>KBEngine.listPathRes("scripts/cell/interfaces", "txt")
        ('/home/kbe/kbengine/demo/res/scripts/cell/interfaces/New Text Document.txt')

        >>>KBEngine.listPathRes("scripts/cell/interfaces", "txt|py")
        ('/home/kbe/kbengine/demo/res/scripts/cell/interfaces/AI.py',
         '/home/kbe/kbengine/demo/res/scripts/cell/interfaces/New Text Document.txt')

        >>>KBEngine.listPathRes("scripts/cell/interfaces", ("txt", "py"))
        ('/home/kbe/kbengine/demo/res/scripts/cell/interfaces/AI.py',
         '/home/kbe/kbengine/demo/res/scripts/cell/interfaces/New Text Document.txt')

        parameters:
            res	string, the relative path of the resource directory
            extension	string, optional parameter, file extension to filter by

        returns:
            Tuple, resource list.
        """
        return tuple()

    @staticmethod
    def lookUpEntityByDBID(entityType: str, dbID: int,
                           callback: Union[bool, IBaseRemoteCall],
                           dbInterfaceName: Optional[str] = None):
        """
        Queries whether an entity is checked out of the database, and if the
        entity has been checked out of the database, KBEngine will return the
        Entity's entityCall in the callback.

        parameters:
            entityType	string, specifies the type of Entity to query. Valid
                entity types are listed in /scripts/entities.xml.
            dbID	Specifies the database ID of the Entity to be queried. The
                database ID is stored in the entity's databaseID attribute.
            callback	A callback with one parameter, True when the entity is
                not checked out from the database, if it is checked out then
                it is the Entity's entityCall. False in any other case.
            dbInterfaceName	string, optional parameter, specifies a database
                interface. Uses the "default" interface by default. Database
                interfaces are defined in kbengine_defaults.xml->dbmgr->databaseInterfaces.
        """
        pass

    @staticmethod
    def matchPath(res: str) -> str:
        """Get the absolute path of a resource from its relative path.

        Note: Resources must be accessible under KBE_RES_PATH.

        Examples:

        >>>KBEngine.matchPath("scripts/entities.xml")
        '/home/kbe/kbengine/demo/res/scripts/entities.xml'

        parameters:
            res	string, the relative path of the resource (including its name).

        returns:
            string, the absolute path of the resource.
        """
        return ''

    @staticmethod
    def open(res: str, mode: str, encoding: Optional[str] = None):
        """Use this function to open resources with their relative paths.

        Note: Resource must be accessible under KBE_RES_PATH.

        parameters:
            res	string, the relative path of the resource.
        mode	string, optional parameter, the default is 'r', file operation mode:
            r Open in only read mode,
            w Open in write mode,
            a Open in append mode (Start from EOF, create new file if necessary)
            r+ Open
            w+ in read/write mode Open in read/write mode (see w)
            a+ Open in read/write mode (See a)
            rb Opens
            wb in binary read mode Opens in binary write mode (see w)
            ab Opens in binary append mode (see a)
            rb+ Opens in binary read and write mode (see r+)
            wb+ Opens in binary read and write mode (see w+ )
            ab+ opens in binary read/write mode (see a+)
        encoding	string, optional parameter, the name of the encoding used
            to decode or encode the file, the default encoding is platform
            dependent.
        """
        pass

    @staticmethod
    def publish() -> int:
        """This function returns the server's current release mode.

        returns:
            int8, 0: debug, 1: release, others can be customized.        """
        return 0

    @staticmethod
    def quantumPassedPercent() -> float:
        """Returns the percentage of the current tick that takes one clock cycle.

        returns:
            Returns the percentage of the current tick that takes one clock cycle.
        """
        return 0.0

    @staticmethod
    def registerReadFileDescriptor(fileDescriptor: socket.socket,
                                   callback: Callable[[socket.socket], None]):
        """Registers a callback function that is called when the file descriptor is readable.

        Example:
            http://www.kbengine.org/assets/other/py/Poller.py

        parameters:
            fileDescriptor	socket descriptor/file descriptor.
            callback	A callback function with the socket descriptor/file
                descriptor as its only parameter.
        """
        pass

    @staticmethod
    def registerWriteFileDescriptor(fileDescriptor: socket.socket,
                                    callback: Callable[[socket.socket], None]):
        """
        Registers a callback function that is called when the socket
        descriptor/file descriptor is writable.

        Example:
            http://www.kbengine.org/assets/other/py/Poller.py

        parameters:
            fileDescriptor	socket descriptor/file descriptor
            callback	A callback function with the socket descriptor/file
                descriptor as its only parameter.
        """

    @staticmethod
    def reloadScript(fullReload: bool):
        """Reloads Python modules related to entity and custom data types.

        The current entity's class is set to the newly loaded class. This
        method should only be used for development mode and not for product
        mode. The following points should be noted:

        1) The overloaded script can only be executed on Baseapp, and the user
        should ensure that all server components are loaded.

        2) The custom type should ensure that the objects already instantiated
        in memory are updated after the script is reloaded. Here is an example:

        for e in KBEngine.entities.values():
            if type( e ) is Avatar.Avatar:
                e.customData.__class__ = CustomClass

        When this mehod completes, KBEngine.onInit( True ) is called.

        parameters:
            fullReload	bool, optional parameter that specifies whether to
            reload entity definitions at the same time. If this parameter
            is False, the entity definition will not be reloaded. The default is True.

        returns:
            True if the reload succeeds, otherwise False.

        """
        pass

    @staticmethod
    def scriptLogType(logType: int):
        """
        Set the type of information output by the current Python.print
        (Reference: KBEngine.LOG_TYPE_*).
        """
        pass

    @staticmethod
    def setAppFlags(flags: int):
        """Set the flags of the current engine APP.

        KBEngine.APP_FLAGS_NONE // Default (not set)
        KBEngine.APP_FLAGS_NOT_PARTCIPATING_LOAD_BALANCING //Do not participate in load balancing

        Example:
            KBEngine.setAppFlags(KBEngine.APP_FLAGS_NOT_PARTCIPATING_LOAD_BALANCING | KBEngine.APP_FLAGS_*)
        """
        pass

    @staticmethod
    def time() -> int:
        """This method returns the current game time (number of cycles).

        returns:
            uint32, the time of the current game. This refers to the number of
                cycles. The period is affected by the frequency. The frequency is
                determined by the configuration file kbengine.xml or
                kbengine_defaults.xml->gameUpdateHertz.
        """
        return -1

    _urlopen_callback_type = \
        Callable[
            [int, str, Dict[str, str], bool, str],
            None
        ]

    @staticmethod
    def urlopen(url: str,
                callback: Optional[_urlopen_callback_type] = None,
                postData: Optional[bytes] = None,
                headers: Optional[Dict[str, str]] = None):
        """This script function is providing an external HTTP/HTTPS asynchronous request.

        parameters:
            url	A valid HTTP/HTTPS URL.
            callback
                Optional parameter with a callback object (for example, a
                function) that requests execution results. This callback takes
                five parameters: the HTTP request return code (eg: 200),
                the returned content, the returned HTTP protocol header,
                whether it succeeded, and the requested URL.

                Example:

                    def onHttpCallback(httpcode, data, headers, success, url):
                        print(httpcode, data, headers, success, url)

                As the above example shows:
                    httpcode: The parameter corresponds to the "HTTP request
                        return code", is an integer.
                    data: The parameter is “returned content &rdquo;, it is a string.
                    headers: The parameter is the HTTP protocol header returned
                        by the server, such as: {"Content-Type": "application/x-www-form-urlencoded"},
                        is an dict.
                    success: Whether the execution is successful or not, when
                        the request execution has an error, it is False, and
                        the error information can be further judged by httpcode.
                    url: Is the URL used by the request.

            postData	Optional parameter, the default is GET mode request
                server. If you need POST mode, please provide the content that
                needs POST. The engine will automatically request the server
                using POST, is an bytes.
            headers	Optional parameter, HTTP header used when requesting,
                such as: {"Content-Type": "application/x-www-form-urlencoded"}, is an dict.
        """

    @staticmethod
    def onBaseAppReady(isBootstrap: bool):
        """This callback function is called when the current Baseapp process is ready.

        Note: This callback function must be implemented in the portal module
        (kbengine_defaults.xml->entryScriptFile).

        parameters:
            isBootstrap	bool, True if this is the first Baseapp started
        """
        pass

    @staticmethod
    def onBaseAppShutDown(state: int):
        """The Baseapp shutdown procedure will call this function.

        Note: This callback function must be implemented in the portal module
        (kbengine_defaults.xml->entryScriptFile).

        parameters:
            state	If state is 0, it means that it is before all clients are
                disconnected, if state is 1, it means that it is before all entities
                are written to the database, if state is 2, it mean all entities have
                been written to the database.
        """
        pass

    @staticmethod
    def onCellAppDeath(addr: Tuple[str, int]):
        """This callback function will be called on the death of a cellapp.

        Note: This callback function must be implemented in the portal module
        (kbengine_defaults.xml->entryScriptFile).

        parameters:
            addr	Dead cellapp address.
            tuple:(ip, port) Network byte order
        """
        pass

    @staticmethod
    def onFini():
        """This callback function is called after the engine is officially shut down.

        Note: This callback function must be implemented in the portal module
        (kbengine_defaults.xml->entryScriptFile).
        """
        pass

    @staticmethod
    def onBaseAppData(key: str, value: Any):
        """This function is called back when KBEngine.baseAppData changes.

        Note: This callback function must be implemented in the portal module
        (kbengine_defaults.xml->entryScriptFile).

        parameters:
            key	The key of the changed data.
            value	The value of the changed data.
        """
        pass

    @staticmethod
    def onBaseAppDataDel(key: str):
        """This function is called back when KBEngine.baseAppData is deleted.

        Note: This callback function must be implemented in the portal module
        (kbengine_defaults.xml->entryScriptFile).

        parameters:
            key	Deleted data key
        """
        pass

    @staticmethod
    def onGlobalData(key: str, value: Any):
        """This function is called back when KBEngine.globalData changes.

        Note: This callback function must be implemented in the portal module
        (kbengine_defaults.xml->entryScriptFile).

        parameters:
            key	The key of the changed data
            value	The value of the changed data
        """
        pass

    @staticmethod
    def onGlobalDataDel(key: str):
        """This function is called back when KBEngine.globalData is deleted.

        Note: This callback function must be implemented in the portal module
        (kbengine_defaults.xml->entryScriptFile).

        parameters:
            key	Deleted data key.
        """
        pass

    @staticmethod
    def onInit(isReload: bool):
        """
        This function is called back after all scripts have been initialized
        after the engine started.

        Note: This callback function must be implemented in the portal module
        (kbengine_defaults.xml->entryScriptFile).

        parameters:
            isReload	bool, whether it was triggered after rewriting the
                loading script.
        """
        pass

    @staticmethod
    def onLoseChargeCB(ordersID: str, dbID: int, success: bool, datas: bytes):
        """
        This function is called back when KBEngine.chargeResponse is called
        in and the order is lost or unknown.

        Note: This callback function must be implemented in the portal module
        (kbengine_defaults.xml->entryScriptFile).

        parameters:
            ordersID	string, order ID.
            dbID	uint64, the database ID of the entity, see: Entity.databaseID.
            success	bool, is it successful?
            datas	bytes, with information
        """
        pass

    @staticmethod
    def onReadyForLogin(isBootstrap: bool) -> float:
        """
        When the engine is started and initialized, it will always call this
        function to ask whether the script layer is ready. If the script layer
        is ready, loginapp allows the client to log in.

        Note: This callback function must be implemented in the portal module
        (kbengine_defaults.xml->entryScriptFile).

        parameters:
            isBootstrap	bool, True if this is the first Baseapp started.

        returns:
           If the return value is greater than or equal to 1.0, the script
           layer is ready; otherwise, return a value from 0 to less than 1.0.
        """
        return 0.0

    @staticmethod
    def onReadyForShutDown() -> bool:
        """
        If this callback function is implemented in the script, it is called
        when the process is ready to exit.

        You can use this callback to control when the process exits.

        Note: This callback function must be implemented in the portal module
        (kbengine_defaults.xml->entryScriptFile).

        returns:
            bool if it returns True, it allows the process to exit. Returning
            other values will cause the process to ask again after a period
            of time.
        """
        return False

    @staticmethod
    def onAutoLoadEntityCreate(entityType: str, dbID: int):
        """Called when an automatically loaded entity is created.

        If the script layer implements this callback, the entity is created by
        the script layer, otherwise the engine defaults to create the entity
        using createEntityAnywhereFromDBID.

        This callback is envoked because Entity.writeToDB was set to automatically load the entity.

        Note: this callback takes precedence over onBaseAppReady execution and can be checked for onBaseAppReady when the entity is loaded.

        parameters:
            entityType	string, specifies the type of entity to query. Valid
                entity types are listed in /scripts/entities.xml.
            dbID	specifies the database ID of the Entity to be queried. The
                database ID of this entity is stored in the entity's databaseID
                attribute.
        """
        pass

    LOG_ON_ACCEPT = 1  # type: int
    """
    This constant is returned by Proxy.onLogOnAttempt, and means that the
    new client is allowed to bind to a Proxy entity. If the Proxy entity
    already has a client binding, the previous client will be kicked out.
    """

    LOG_ON_REJECT = 0  # type: int
    """
    This constant is returned by Proxy.onLogOnAttempt, which means that
    the current client is bound to the Proxy entity.
    """

    LOG_ON_WAIT_FOR_DESTROY = 2  # type: int
    """
    This constant is returned by Proxy.onLogOnAttempt. The current
    requesting client will wait until the Proxy entity is completely
    destroyed and the underlying layer will complete the subsequent
    binding process. Before this returns, Proxy.destroy or
    Proxy.destroyCellEntity should be invoked.
    """

    LOG_TYPE_DBG = -1  # type: int
    """
    The log output type is debug.
    Set by scriptLogType.
    """

    LOG_TYPE_ERR = -1  # type: int
    """
    The log output type is error.
    Set byscriptLogType.
    """

    LOG_TYPE_INFO = -1  # type: int
    """
    The log output type is general information.
    Set by scriptLogType.
    """

    LOG_TYPE_NORMAL = -1  # type: int
    """
    The log output type is normal.
    Set by scriptLogType.
    """

    LOG_TYPE_WAR = -1  # type: int
    """
    The log output type is warning.
    Set by scriptLogType.
    """

    NEXT_ONLY = -1  # type: int
    """
    This constant is used for the Entity.shouldAutoBackup and
    Entity.shouldAutoArchive attributes and means that the entity is backed
    up automatically next time it is deemed acceptable, and then the
    attribute is automatically set to false (0).
    """

    component = ''  # type: str
    """This is the component that is running in the current Python environment.

    (So far) Possible values are 'cellapp', 'baseapp', 'client', 'dbmgr',
    'bots', and 'editor'.
    """

    entities = {}  # type: Dict[int, Union[IBaseEntity, IProxyEntity]]
    """
    entities is a dictionary object that contains all the entities in the
    current process.

    Debugging leaked entities (instances that call destroy without
    releasing memory, usually due to being referenced):

    >>> KBEngine.entities.garbages.items()
    [(1025, Avatar object at 0x7f92431ceae8.)]


    >>> e = _[0][1]
    >>> import gc
    >>> gc.get_referents(e)
    [{'spacesIsOk': True, 'bootstrapIdx': 1}, ]


    Debugging a leaked KBEngine-encapsulated Python object:
        KBEngine.debugTracing

    Types:
        Entities
    """

    baseAppData = {}  # type: Dict[Any, Any]
    """
    This attribute contains a dictionary-like object that is automatically
    synchronized across all BaseApps. When a value in the dictionary is
    modified, the change is broadcast to all BaseApps.

    Example:
        KBEngine.baseAppData[ "hello" ] = "there"

    The rest of the BaseApps can access the following:
        print KBEngine.baseAppData[ "hello" ]

    Keys and values can be of any type, but these types must be encapsulated
    and unpacked on all target components.

    When a value is changed or deleted, a callback function is called on
    all components. See: KBEngine.onBaseAppData and KBEngine.onDelBaseAppData.

    Note: Only top-level value changes will be broadcast. If you have a
    value (such as a list) that changes an internal value (such as just
    changing a number), this information will not be broadcast.

    Do not do the following:
        KBEngine.baseAppData[ "list" ] = [1, 2, 3]
        KBEngine.baseAppData[ "list" ][1] = 7

    The local access is [1, 7, 3] and the remote access is [1, 2, 3].
    """

    globalData = {}  # type: Dict[Any, Any]
    """
    This attribute contains a dictionary-like object that is automatically
    synchronized across all BaseApps and CellApps. When a value in the
    dictionary is modified, the change is broadcast to all BaseApps and
    CellApps.

    example:

        KBEngine.globalData[ "hello" ] = "there"

    The other Baseapps and Cellapps can access the following:

        print KBEngine.globalData[ "hello" ]

    Keys and values can be of any type, but these types must be encapsulated
    and unpacked on all target components. When a value is changed or
    deleted, a callback function is called on all components.
    See: KBEngine.onGlobalData and KBEngine.onGlobalDataDel.

    Note: Only top-level value changes will be broadcast. If you have a
    value (such as a list) that changes an internal value (such as just
    changing a number), this information will not be broadcast.

    Do not do the following:

    KBEngine.globalData[ "list" ] = [1, 2, 3]
    KBEngine.globalData[ "list" ][1] = 7

    The local access is [1, 7, 3] and the remote access is [1, 2, 3].
    """


class IKBEngineCellModule:
    Entity = ICellEntity
    EntityComponent = ICellEntityComponent

    @staticmethod
    def addSpaceGeometryMapping(spaceID: int, mapper: Any, path: str,
                                shouldLoadOnServer: Optional[bool],
                                params: Dict[int, str]):
        """
        Associate a geometric mapping of a given space. After the function is
        called, the server and client will load the corresponding geometry data.

        On the server, all geometry data is loaded from the given directory
        into the specified space. These data may be divided into many blocks.
        Different blocks are loaded asynchronously. The following callback
        methods are called when all the geometry data is loaded:

            def onAllSpaceGeometryLoaded( self, spaceID, mappingName ):

        The server only loads the geometric data of the scene for use by the
        navigation and collision functions. In addition to the geometric data,
        the client also loads data such as textures. 3D scenes currently use
        the data exported by the recastnavigation plugin-in by default. 2D
        scenes currently use the data exported by MapEditor by default.

        There is a possibility that onAllSpaceGeometryLoaded() will not be
        invoked, that is, if multiple Cellapps call this method at the same
        time to add geometry to the same space, cellappmgr crashes.

        parameters:
            spaceID	uint32, ID of the space, specifies in which space to operate
            mapper	Not yet implemented
            path	Directory path containing geometry data
            shouldLoadOnServer	Optional boolean parameter that specifies
                whether to load geometry on the server. Default is True.
            params	Optional PyDict parameter, specifies the navmesh used by
                different layers, for example:

        KBEngine.addSpaceGeometryMapping(self.spaceID, None, resPath, True, {0 : "srv_xinshoucun_1.navmesh", 1 : "srv_xinshoucun.navmesh"})
        """
        pass

    @staticmethod
    def addWatcher(path: str, dataType: str, getFunction: Callable):
        """
        Interacts with the debug monitoring system to allow users to register
        a monitoring variable with the monitoring system.

        Example:

        >>> def countPlayers( ):
        >>>     i = 0
        >>>     for e in KBEngine.entities.values():
        >>>     	if e.__class__.__name__ == "Avatar":
        >>>     		i += 1
        >>>     return i
        >>>
        >>> KBEngine.addWatcher( "players", "UINT32", countPlayers )

        This function adds a watch variable under the "scripts/players" watch
        path. The function countPlayers is called when the watcher observes a
        change.

        parameters:
            path	The path to create a watcher.
            dataType	The value type of the monitored variable. Reference:
                Basic data types
            getFunction	This function is called when the observer retrieves the
                variable. This function returns a value representing a watch
                variable without arguments.
        """
        pass

    @staticmethod
    def address() -> str:
        """Returns the address of the internal network interface."""
        return ''

    @staticmethod
    def MemoryStream():
        """Returns a new MemoryStream object.

        The MemoryStreamobject stores binary information. This type is provided
        to allow the user to easily serialize and deserialize the Python base
        types following KBEngine underlying serialization rules.

        For example, you can use this object to construct a network packet
        that KBEngine can parse.

        Usage:

        >>> s = KBEngine.MemoryStream()
        >>> s
        >>> b''
        >>> s.append("UINT32", 1)
        >>> s.pop("UINT32")
        >>> 1

        The types that MemoryStream currently supports are only basic data types.
        Reference: Basic data types
        """
        pass

    @staticmethod
    def createEntity(entityType: str, spaceID: int,
                     position: Tuple[float, float, float],
                     direction: Tuple[float, float, float],
                     params: Optional[Dict[str, Any]] = None) -> ICellEntity:
        """
        When calling this function you must specifiy the type, location, and
        direction of the entity to be created. Optionally, any attribute of
        the entity can be set with the params Python dictionary parameter.
        (the attributes are described in the entity's .def file).

        Example:

            # Create an open Door entity in the same space as the "thing" entity
            direction = ( 0, 0, thing.yaw )
            properties = { "open":1 }
            KBEngine.createEntity( "Door", thing.space, thing.position, direction,
                                properties )

        parameters:
        entityType	string, the name of the entity to create, declared in
            the /scripts/entities.xml file.
        spaceID	int32, the ID of the space to place the entity
        position	A sequence of 3 floats that specify the creation point of
            the new entity, in world coordinates.
        direction	A sequence of 3 floats that specify the initial orientation
            (roll, pitch, yaw) of the new entity in world coordinates.
        params	Optional parameters, a Python dictionary object. If a
            specified key is an Entity attribute, its value will be used to
            initialize the properties of the new Entity.

        returns:
            The new Entity.
        """
        return ICellEntity()

    @staticmethod
    def debugTracing():
        """Outputs the Python extended object counter currently tracked by KBEngine.

        Extended objects include: fixed dictionary, fixed array, Entity, IRemoteCall...
        If the counter is not zero when the server is shut down normally, it
        means that the leak already exists and the log will output an error message.

        ERROR cellapp [0x0000cd64] [2014-11-12 00:38:07,300] - PyGC::debugTracing(): FixedArray : leaked(128)
        ERROR cellapp [0x0000cd64] [2014-11-12 00:38:07,300] - PyGC::debugTracing(): IRemoteCall : leaked(8)
        """
        pass

    @staticmethod
    def delSpaceData(spaceID: int, key: str):
        """
        Deletes the space data of the specified key (if space is divided into
        multiple parts, it will be deleted synchronously).

        The space data is set by the user via setSpaceData.

        parameters:
            spaceID	int32, the ID of the space
            key	string, a string keyword
        """
        pass

    @staticmethod
    def delWatcher(path: str):
        """
        Interacts with the debug monitoring system, allowing users to delete
        monitored variables in the script.

        parameters:
            path	The path to the variable to delete.
        """
        pass

    @staticmethod
    def deregisterReadFileDescriptor(fileDescriptor: socket.socket):
        """
        Unregisters the callback registered with KBEngine.registerReadFileDescriptor.

        Example:
            http://www.kbengine.org/assets/other/py/Poller.py

        parameters:
            fileDescriptor	socket descriptor/file descriptor
        """
        pass

    @staticmethod
    def deregisterWriteFileDescriptor(fileDescriptor: socket.socket):
        """
        Unregisters the callback registered with KBEngine.registerWriteFileDescriptor.

        Example:
            http://www.kbengine.org/assets/other/py/Poller.py

        parameters:
            fileDescriptor	socket descriptor/file descriptor.
        """
        pass

    @staticmethod
    def executeRawDatabaseCommand(command: str,
                                  callback: Optional[DBCallback] = None,
                                  threadID: Optional[int] = None,
                                  dbInterfaceName: Optional[str] = None):
        """
        This script function executes a database command on the database,
        which is directly parsed by the relevant database.

        Please note that using this function to modify entity data may not be
        effective because if the entity has been checked out, the modified data
        will still be archived by the entity and cause overwriting.

        This function is strongly not recommended for reading or modifying entity data.

        parameters:
            command	This database command will be different for different
                database configuration scenarios. For a MySQL database it is
                an SQL query.
            callback

        Optional parameter, callback object (for example, a function) called
        back with the command execution result.
        This callback has 4 parameters: result set, number of rows affected,
        auto value, error message.

        Example:
            def sqlcallback(result, rows, insertid, error):
                print(result, rows, insertid, error)

            As the above example shows, the result parameter corresponds to the
            "result set", and the result set parameter is a row List. Each line
            is a list of strings containing field values. If the command execution
            does not return a result set (for example, a DELETE command), or the
            command execution encounters an error, the result set is None.

            The rows parameter is the "number of rows affected", which is an
            integer indicating the number of rows affected by the command execution.
            This parameter is only relevant for commands that do not return results
            (such as DELETE).
            This parameter is None if there is a result set return or if there is
            an error in the command execution.

            The insertid is a long value, similar to an entity's databaseID. When
            successfully inserting data int a table with an auto long type field,
            it returns the data at the time of insertion.
            More information can be found in mysql's mysql_insert_id() method. In
            addition, this parameter is only meaningful when the database type is
            mysql.

            Error corresponds to the "error message", when the command execution
            encounters an error, this parameter is a string describing the error.
            This parameter is None when the command execution has not occurred.

        threadID	int32, optional parameter, specifies a thread to process
            this command. Users can use this parameter to control the execution
            order of certain commands (dbmgr is multi-threaded). The default is
            not specified. If threadId is the ID of an entity, it will be added
            to the entity's archive queue and written by the thread one by one.
        dbInterfaceName	string, optional parameter, specifies a database
            interface. By default it uses the "default" interface. Database
            interfaces are defined by kbengine_defaults.xml->dbmgr->databaseInterfaces.
        """
        pass

    @staticmethod
    def genUUID64():
        """This function generates a 64-bit unique ID.

        Note: This function depends on the baseapp server process startup
        parameter 'gus'. Please set the startup parameters to be unique.
        In addition, if gus exceeds 65535, this function can only remain
        unique for the current process.

        Usage:
        Unique IDs can be generated on multiple service processes and do not conflict.
        A room ID can be generated on multiple service processes and no
            uniqueness verification is required.

        returns:
            Returns a 64-bit integer.
        """
        pass

    @staticmethod
    def getResFullPath(res: str) -> str:
        """Get the absolute path of a resource.

        Note: Resource must be accessible under KBE_RES_PATH.

        parameters:
            res	string, the relative path of the resource

        returns:
            string, if there is an absolute path to the given resource,
                otherwise returns null.
        """
        return ''

    @staticmethod
    def getSpaceData(spaceID: int, key: str) -> str:
        """Get the space data of the specified key.

        The space data is set by the user via setSpaceData.

        parameters:
            spaceID	int32, the ID of the space
            key	string, a string keyword

        returns:
            string, string data for the given key
        """
        return ''

    @staticmethod
    def getSpaceGeometryMapping(spaceID: int) -> str:
        """Returns the geometry map name of a specified space.

        parameters:
            spaceID	The ID of the space to be queried

        returns:
            string, the name of the geometry map.
        """
        return ''

    @staticmethod
    def getWatcher(path: str) -> Any:
        """Gets the value of a watch variable from the KBEngine debugging system.

        Example: In the Python console of baseapp1:
        >>>KBEngine.getWatcher("/root/stats/runningTime")
        12673648533

        >>>KBEngine.getWatcher("/root/scripts/players")
        32133

        parameters:
            path	string, the absolute path of the variable including the
            variable name (can be viewed on the GUIConsole watcher page).

        returns:
            The value of the variable.
        """
        pass

    @staticmethod
    def getAppFlags():
        """Get the flags of the current engine APP, Reference: KBEngine.setAppFlags.

        returns:
            KBEngine.APP_FLAGS_*
        """
        pass

    @staticmethod
    def hasRes(res: str) -> bool:
        """Use this interface to determine if a relative path exists.

        Note: Resource must be accessible under KBE_RES_PATH.

        Example:

        >>>KBEngine.hasRes("scripts/entities.xml")
        True

        parameters:
            res	string, the relative path of the resource

        returns:
            bool, True if relative path exists, otherwise False.
        """
        return False

    @staticmethod
    def isShuttingDown() -> bool:
        """Returns whether the server is shutting down.

        After the onBaseAppShutDown(state=0) is called, this function returns True.

        returns:
            True if the server is shutting down, otherwise False.
        """
        return False

    @staticmethod
    def listPathRes(path: str, extension: Optional[str] = None) -> Tuple[str, ...]:
        """Get a list of resources in a resource directory.

        Note: Resources must be accessible under KBE_RES_PATH.

        Example:

        >>>KBEngine.listPathRes("scripts/cell/interfaces")
        ('/home/kbe/kbengine/demo/res/scripts/cell/interfaces/AI.py',
         '/home/kbe/kbengine/demo/res/scripts/cell/interfaces/New Text Document.txt')

        >>>KBEngine.listPathRes("scripts/cell/interfaces", "txt")
        ('/home/kbe/kbengine/demo/res/scripts/cell/interfaces/New Text Document.txt')

        >>>KBEngine.listPathRes("scripts/cell/interfaces", "txt|py")
        ('/home/kbe/kbengine/demo/res/scripts/cell/interfaces/AI.py',
         '/home/kbe/kbengine/demo/res/scripts/cell/interfaces/New Text Document.txt')

        >>>KBEngine.listPathRes("scripts/cell/interfaces", ("txt", "py"))
        ('/home/kbe/kbengine/demo/res/scripts/cell/interfaces/AI.py',
         '/home/kbe/kbengine/demo/res/scripts/cell/interfaces/New Text Document.txt')

        parameters:
            res	string, the relative path of the resource directory
            extension	string, optional parameter, file extension to filter by

        returns:
            Tuple, resource list.
        """
        return tuple()

    @staticmethod
    def matchPath(res: str) -> str:
        """Get the absolute path of a resource from its relative path.

        Note: Resources must be accessible under KBE_RES_PATH.

        Examples:

        >>>KBEngine.matchPath("scripts/entities.xml")
        '/home/kbe/kbengine/demo/res/scripts/entities.xml'

        parameters:
            res	string, the relative path of the resource (including its name).

        returns:
            string, the absolute path of the resource.
        """
        return ''

    @staticmethod
    def open(res: str, mode: str, encoding: Optional[str] = None):
        """Use this function to open resources with their relative paths.

        Note: Resource must be accessible under KBE_RES_PATH.

        parameters:
            res	string, the relative path of the resource.
        mode	string, optional parameter, the default is 'r', file operation mode:
            r Open in only read mode,
            w Open in write mode,
            a Open in append mode (Start from EOF, create new file if necessary)
            r+ Open
            w+ in read/write mode Open in read/write mode (see w)
            a+ Open in read/write mode (See a)
            rb Opens
            wb in binary read mode Opens in binary write mode (see w)
            ab Opens in binary append mode (see a)
            rb+ Opens in binary read and write mode (see r+)
            wb+ Opens in binary read and write mode (see w+ )
            ab+ opens in binary read/write mode (see a+)
        encoding	string, optional parameter, the name of the encoding used
            to decode or encode the file, the default encoding is platform
            dependent.
        """
        pass

    @staticmethod
    def publish() -> int:
        """This function returns the server's current release mode.

        returns:
            int8, 0: debug, 1: release, others can be customized.        """
        return 0

    @staticmethod
    def raycast(spaceID: int, layer: int, src: Tuple[float, float, float],
                dst: Tuple[float, float, float]) -> List[Tuple[float, float, float]]:
        """
        In the specified layer of the specified space, a ray is emitted from
        the source coordinates to the destination coordinates, and the collided
        coordinate point is returned.

        Note: Space must load geometry using addSpaceGeometryMapping.

        Below is an example:

            >>> KBEngine.raycast( spaceID, entity.layer, (0, 10, 0), (0,-10,0) )
            ((0.0000, 0.0000, 0.0000), ( (0.0000, 0.0000, 0.0000),
            (4.0000, 0.0000, 0.0000), (4.0000, 0.0000, 4.0000)), 0)

        parameters:
            spaceID	int32, space ID
            layer	int8, geometric layer. A space can load multiple navmesh
                data at the same time. Different navmesh can be in different
                layers. Different layers can be abstracted into the ground,
                the water surface and so on.

        returns:
            list, list of coordinate points collided
        """
        return []

    @staticmethod
    def registerReadFileDescriptor(fileDescriptor: socket.socket,
                                   callback: Callable[[socket.socket], None]):
        """Registers a callback function that is called when the file descriptor is readable.

        Example:
            http://www.kbengine.org/assets/other/py/Poller.py

        parameters:
            fileDescriptor	socket descriptor/file descriptor.
            callback	A callback function with the socket descriptor/file
                descriptor as its only parameter.
        """
        pass

    @staticmethod
    def registerWriteFileDescriptor(fileDescriptor: socket.socket,
                                    callback: Callable[[socket.socket], None]):
        """
        Registers a callback function that is called when the socket
        descriptor/file descriptor is writable.

        Example:
            http://www.kbengine.org/assets/other/py/Poller.py

        parameters:
            fileDescriptor	socket descriptor/file descriptor
            callback	A callback function with the socket descriptor/file
                descriptor as its only parameter.
        """

    @staticmethod
    def reloadScript(fullReload: bool):
        """Reloads Python modules related to entity and custom data types.

        The current entity's class is set to the newly loaded class. This
        method should only be used for development mode and not for product
        mode. The following points should be noted:

        1) The overloaded script can only be executed on Baseapp, and the user
        should ensure that all server components are loaded.

        2) The custom type should ensure that the objects already instantiated
        in memory are updated after the script is reloaded. Here is an example:

        for e in KBEngine.entities.values():
            if type( e ) is Avatar.Avatar:
                e.customData.__class__ = CustomClass

        When this mehod completes, KBEngine.onInit( True ) is called.

        parameters:
            fullReload	bool, optional parameter that specifies whether to
            reload entity definitions at the same time. If this parameter
            is False, the entity definition will not be reloaded. The default is True.

        returns:
            True if the reload succeeds, otherwise False.

        """
        pass

    @staticmethod
    def scriptLogType(logType: int):
        """
        Set the type of information output by the current Python.print
        (Reference: KBEngine.LOG_TYPE_*).
        """
        pass

    @staticmethod
    def setAppFlags(flags: int):
        """Set the flags of the current engine APP.

        KBEngine.APP_FLAGS_NONE // Default (not set)
        KBEngine.APP_FLAGS_NOT_PARTCIPATING_LOAD_BALANCING //Do not participate in load balancing

        Example:
            KBEngine.setAppFlags(KBEngine.APP_FLAGS_NOT_PARTCIPATING_LOAD_BALANCING | KBEngine.APP_FLAGS_*)
        """
        pass

    @staticmethod
    def setSpaceData(spaceID: int, key: str, value: str):
        """Sets the space data for the specified key.

        The space data can be obtained via getSpaceData.

        parameters:
            spaceID	int32, the ID of the space.
            key	string, a string keyword
            value	string, the string value.
        """
        pass

    @staticmethod
    def time() -> int:
        """This method returns the current game time (number of cycles).

        returns:
            uint32, the time of the current game. This refers to the number of
                cycles. The period is affected by the frequency. The frequency is
                determined by the configuration file kbengine.xml or
                kbengine_defaults.xml->gameUpdateHertz.
        """
        return -1

    @staticmethod
    def onCellAppData(key, value):
        """This function is called back when KBEngine.cellAppData changes.

        Note: This callback interface must be implemented in the portal module
        ( kbengine_defaults.xml->entryScriptFile ).

        parameters:
            key	The key of the changed data.
            value	The value of the changed data.
        """
        pass

    @staticmethod
    def onCellAppDataDel(key):
        """This function is called back when KBEngine.cellAppData is deleted.

        Note: This callback interface must be implemented in the portal module (kbengine_defaults.xml->entryScriptFile).

        parameters:
            key	Deleted data key.
        """
        pass

    @staticmethod
    def onGlobalData(key: str, value: Any):
        """This function is called back when KBEngine.globalData changes.

        Note: This callback function must be implemented in the portal module
        (kbengine_defaults.xml->entryScriptFile).

        parameters:
            key	The key of the changed data
            value	The value of the changed data
        """
        pass

    @staticmethod
    def onGlobalDataDel(key: str):
        """This function is called back when KBEngine.globalData is deleted.

        Note: This callback function must be implemented in the portal module
        (kbengine_defaults.xml->entryScriptFile).

        parameters:
            key	Deleted data key.
        """
        pass

    @staticmethod
    def onInit(isReload: bool):
        """
        This function is called back after all scripts have been initialized
        after the engine started.

        Note: This callback function must be implemented in the portal module
        (kbengine_defaults.xml->entryScriptFile).

        parameters:
            isReload	bool, whether it was triggered after rewriting the
                loading script.
        """
        pass

    @staticmethod
    def onSpaceData(spaceID: int, key: str, value: str):
        """Called when there is a change in the space data.

        The space data is set by the user via setSpaceData.

        parameters:
            spaceID	The ID of the space.
            key	The key of the changed data.
            value	The value of the changed data.
        """
        pass

    @staticmethod
    def onSpaceGeometryLoaded(spaceID, mapping):
        """The space required by the grid collision data is loaded.

        Set by user through addSpaceGeometryMapping.

        parameters:
            spaceID	The ID of the space.
            mapping	The map value of the grid collision data.
        """
        pass

    @staticmethod
    def onAllSpaceGeometryLoaded(spaceID: int, isBootstrap: bool, mapping: dict):
        """The space required for grid collision and other data is completely loaded.

        Set by user through addSpaceGeometryMapping.

        parameters:
            spaceID	The ID of the space.
            isBootstrap	If a space is partitioned by multiple cells,
                isBootstrap describes whether it is the originating cell of
                the loading request.
            mapping	The map value of grid collision data.
        """
        pass

    @staticmethod
    def onReadyForLogin(isBootstrap: bool) -> float:
        """
        When the engine is started and initialized, it will always call this
        function to ask whether the script layer is ready. If the script layer
        is ready, loginapp allows the client to log in.

        Note: This callback function must be implemented in the portal module
        (kbengine_defaults.xml->entryScriptFile).

        parameters:
            isBootstrap	bool, True if this is the first Baseapp started.

        returns:
           If the return value is greater than or equal to 1.0, the script
           layer is ready; otherwise, return a value from 0 to less than 1.0.
        """
        return 0.0

    LOG_TYPE_DBG = -1  # type: int
    """
    The log output type is debug.
    Set by scriptLogType.
    """

    LOG_TYPE_ERR = -1  # type: int
    """
    The log output type is error.
    Set byscriptLogType.
    """

    LOG_TYPE_INFO = -1  # type: int
    """
    The log output type is general information.
    Set by scriptLogType.
    """

    LOG_TYPE_NORMAL = -1  # type: int
    """
    The log output type is normal.
    Set by scriptLogType.
    """

    LOG_TYPE_WAR = -1  # type: int
    """
    The log output type is warning.
    Set by scriptLogType.
    """

    NEXT_ONLY = -1  # type: int
    """This constant is currently unused in Cellapp."""

    cellAppData = {}  # type: Dict[Any, Any]
    """
    This property contains a dictionary-like object that is automatically
    synchronized across all CellApps. When a value in the dictionary is
    modified, this change is broadcast to all Cellapps.

    Example:

        KBEngine.cellAppData[ "hello" ] = "there"

    The rest of Cellap can access the following:

        print KBEngine.cellAppData[ "hello" ]

    Keys and values can be of any type, but these types must be
    encapsulated and unpacked on all target components.

    When a value is changed or deleted, a callback function is called on
    all components. See: KBEngine.onCellAppData and KBEngine.onDelCellAppData.

    Note: Only the top-level value will be broadcast. If you have a value
    (such as a list) that changes the internal value (such as just
    changing a number), this information will not be broadcast.

    Do not do the following:

        KBEngine.cellAppData[ "list" ] = [1, 2, 3]
        KBEngine.cellAppData[ "list" ][1] = 7

    This will cause the local access to read [1, 7, 3] and the remote [1, 2, 3]
    """

    component = ''  # type: str
    """This is the component that is running in the current Python environment.

    (So far) Possible values are 'cellapp', 'baseapp', 'client', 'dbmgr',
    'bots', and 'editor'.
    """

    entities = {}  # type: Dict[int, ICellEntity]
    """
    entities is a dictionary object that contains all the entities in the
    current process.

    Debugging leaked entities (instances that call destroy without
    releasing memory, usually due to being referenced):

    >>> KBEngine.entities.garbages.items()
    [(1025, Avatar object at 0x7f92431ceae8.)]


    >>> e = _[0][1]
    >>> import gc
    >>> gc.get_referents(e)
    [{'spacesIsOk': True, 'bootstrapIdx': 1}, ]


    Debugging a leaked KBEngine-encapsulated Python object:
        KBEngine.debugTracing

    Types:
        Entities
    """

    globalData = {}  # type: Dict[Any, Any]
    """
    This attribute contains a dictionary-like object that is automatically
    synchronized across all BaseApps and CellApps. When a value in the
    dictionary is modified, the change is broadcast to all BaseApps and
    CellApps.

    example:

        KBEngine.globalData[ "hello" ] = "there"

    The other Baseapps and Cellapps can access the following:

        print KBEngine.globalData[ "hello" ]

    Keys and values can be of any type, but these types must be encapsulated
    and unpacked on all target components. When a value is changed or
    deleted, a callback function is called on all components.
    See: KBEngine.onGlobalData and KBEngine.onGlobalDataDel.

    Note: Only top-level value changes will be broadcast. If you have a
    value (such as a list) that changes an internal value (such as just
    changing a number), this information will not be broadcast.

    Do not do the following:

    KBEngine.globalData[ "list" ] = [1, 2, 3]
    KBEngine.globalData[ "list" ][1] = 7

    The local access is [1, 7, 3] and the remote access is [1, 2, 3].
    """


_UrlType = str
_HeadersType = Dict[str, str]
_HttpCBType = Callable[[int, str, _HeadersType, bool, _UrlType], None]

_TimerID = int
_AddTimerCBType = Callable[[_TimerID], None]


class IKBEngineLoginModule:
    """
    This KBEngine module provides Python scripts control over the loginapp
    process to handle entity login registration.
    """

    @staticmethod
    def addTimer(initialOffset: float,
                 repeatOffset: Union[float, _AddTimerCBType] = -1.0,
                 callbackObj: Optional[_AddTimerCBType] = None) -> _TimerID:
        """Register a timer.

        The timer is triggered by the callback function callbackObj. The callback function will be executed the first time after "initialOffset" seconds, and then will be executed once every "repeatOffset" seconds.

        Example:

        Here is an example of using addTimer
            ```
            import KBEngine

            # Add a timer, perform the first time after 5 seconds, and execute once every 1 second. The user parameter is 9
            KBEngine.addTimer( 5, 1, onTimer_Callbackfun )

            # Add a timer and execute it after 1 second. The default user parameter is 0.
            KBEngine.addTimer( 1, onTimer_Callbackfun )

            def onTimer_Callbackfun( id ):
                print "onTimer_Callbackfun called: id %i" % ( id )
                # If this is a repeated timer, it is no longer needed, call the following function to remove:
                #     KBEngine.delTimer( id )
            ```

        parameters:
            initialOffset	float, specifies the time interval in seconds for
                the timer to register from the first callback.
            repeatOffset	float, specifies the time interval (in seconds)
                between each execution after the first callback execution. You
                must remove the timer with the function delTimer, otherwise it
                will continue to repeat. Values less than or equal to 0 will
                be ignored.
            callbackObj	function, the specified callback function object

        returns:
            integer, the internal id of the timer. This id can be used toremove
                the timer using delTimer
        """
        return -1

    @staticmethod
    def delTimer(id: _TimerID):
        """
        The function delTimer is used to remove a registered timer. The removed
        timer is no longer executed. Single-shot timers are automatically
        removed after the callback is executed, and it is not necessary to use
        delTimer to remove it. If the delTimer function uses an invalid id
        (for example, has been removed), it will generate an error

        A use case for the KBEngine.addTimer reference timer.

        parameters:
            id	integer, timer id to remove
        """

    @staticmethod
    def urlopen(url: _UrlType, callback: _HttpCBType, postData: bytes,
                headers: _HeadersType):
        """This script function is providing an external HTTP/HTTPS asynchronous request.

        parameters:
            url	A valid HTTP/HTTPS URL.
        callback
            Optional parameter with a callback object (for example, a function)
            that requests execution results. This callback takes five parameters:
                the HTTP request return code (eg: 200),
                the returned content,
                the returned HTTP protocol header,
                whether it succeeded,
                and the requested URL.

            Example:
            def onHttpCallback(httpcode, data, headers, success, url):
                print(httpcode, data, headers, success, url)

            As the above example shows:

                httpcode: The parameter corresponds to the "HTTP request return code",
                    is an integer.
                data: The parameter is “returned content &rdquo;, it is a string.
                headers: The parameter is the HTTP protocol header returned by the
                    server, such as:{"Content-Type": "application/x-www-form-urlencoded"},
                    is an dict.
                success: Whether the execution is successful or not, when the
                    request execution has an error, it is False, and the error '
                    information can be further judged by httpcode.
                url: Is the URL used by the request.

        postData	Optional parameter, the default is GET mode request server.
            If you need POST mode, please provide the content that needs POST.
            The engine will automatically request the server using POST, is an
            bytes.
        headers	Optional parameter, HTTP header used when requesting, such
            as：{"Content-Type": "application/x-www-form-urlencoded"}, is an dict.
        """

    @staticmethod
    def onLoginAppReady():
        """This function is called back when the current process is ready.

        Note: This callback interface must be implemented in the portal module
        ( kbengine_defaults.xml ->entryScriptFile).
        """

    @staticmethod
    def onLoginAppShutDown():
        """Process shutdown calls this function back.

        Note: This callback interface must be implemented in the portal module
        (kbengine_defaults.xml ->entryScriptFile).
        """

    @staticmethod
    def onRequestLogin(loginName: str, password: str, clientType: int,
                       datas: bytes) -> Tuple[int, str, str, int, bytes]:
        """Called back when the client requests the server login account.

        Here you can do some administrative control on user login. For example:
        Use this interface to truncate the user's login here, record the
        request and queue it, and return an error code to tell the client
        the queue status.

        Note: This callback interface must be implemented in the portal module
        ( kbengine_defaults.xml ->entryScriptFile).

        parameters:
            loginName	string, the name of the account submitted when logging in.
            password	string, MD5 password.
            clientType	integer, client type, given when the client logs in.
            datas	bytes, the data attached to the client request, can forward
                data to a third-party platform.

        returns:
            Tuple, the return value is
                error code,
                real account name,
                password,
                client type,
                data - data submitted by the client

            if there is no need to extend the modification, the return value is usually to
            destroy the incoming value (KBEngine.SERVER_SUCCESS , loginName,
            password, clientType, datas).
        """
        return (0, '', '', 0, b'')

    @staticmethod
    def onLoginCallbackFromDB(loginName: str, accountName: str, errorno: int,
                              datas: bytes):
        """The callback returned by dbmgr after the client requests the server login account.

        Note: This callback interface must be implemented in the portal module
        ( kbengine_defaults.xml ->entryScriptFile).

        parameters:
            loginName	string, the name of the account submitted when logging in.
            accountName	string, the real account name (obtained from the the
                query at dbmgr)
            errorno	integer, error code, if it is not KBEngine.SERVER_SUCCESS,
                login failed.
            datas	bytes, which may be any data, such as data returned by
                a third-party platform or data returned by dbmgr and interfaces
                when processing the login.
        """

    @staticmethod
    def onRequestCreateAccount(accountName: str, password: str, data: bytes
                               ) -> Tuple[int, str, int, bytes]:
        """Callback when the client requests the server to create an account.


        Note: This callback interface must be implemented in the portal module
        (kbengine_defaults.xml ->entryScriptFile).

        parameters:
            accountName	string, the name of the account submitted by the client.
            password	string, MD5 password.
            datas	bytes, the data attached to the client request, can forward
                data to a third-party platform.

        returns:
            Tuple, the return value is
                error code,
                real account name,
                password,
                data - data submitted by the client,

        if there is no need to extend the modified value is usually returned
        to destroy the incoming value (KBEngine.SERVER_SUCCESS, loginName,
        password , datas).
        """
        return (0, '', 0, b'')

    @staticmethod
    def onCreateAccountCallbackFromDB(accountName: str, errorno: int, datas: bytes):
        """
        The callback returned by dbmgr after the client requests the server
        to create an account.


        Note: This callback interface must be implemented in the portal module
        ( kbengine_defaults.xml ->entryScriptFile).

        parameters:
            accountName	string, the name of the account submitted by the client.
            errorno	integer - error code, if it is not KBEngine.SERVER_SUCCESS, login failed.
            datas	bytes, which may be any data, such as data returned by
                a third-party platform or data returned by dbmgr and interfaces
                when processing the login.
        """


class IKBEngineDBMgrModule:
    """
    The Dbmgr process is mainly responsible for handling the storage of
    entity data and loading/querying of entity data.
    """

    @staticmethod
    def addTimer(initialOffset: float,
                 repeatOffset: Union[float, _AddTimerCBType] = -1.0,
                 callbackObj: Optional[_AddTimerCBType] = None) -> _TimerID:
        """Register a timer.

        The timer is triggered by the callback function callbackObj. The callback function will be executed the first time after "initialOffset" seconds, and then will be executed once every "repeatOffset" seconds.

        Example:

        Here is an example of using addTimer
            ```
            import KBEngine

            # Add a timer, perform the first time after 5 seconds, and execute once every 1 second. The user parameter is 9
            KBEngine.addTimer( 5, 1, onTimer_Callbackfun )

            # Add a timer and execute it after 1 second. The default user parameter is 0.
            KBEngine.addTimer( 1, onTimer_Callbackfun )

            def onTimer_Callbackfun( id ):
                print "onTimer_Callbackfun called: id %i" % ( id )
                # If this is a repeated timer, it is no longer needed, call the following function to remove:
                #     KBEngine.delTimer( id )
            ```

        parameters:
            initialOffset	float, specifies the time interval in seconds for
                the timer to register from the first callback.
            repeatOffset	float, specifies the time interval (in seconds)
                between each execution after the first callback execution. You
                must remove the timer with the function delTimer, otherwise it
                will continue to repeat. Values less than or equal to 0 will
                be ignored.
            callbackObj	function, the specified callback function object

        returns:
            integer, the internal id of the timer. This id can be used toremove
                the timer using delTimer
        """
        return -1

    @staticmethod
    def delTimer(id: _TimerID):
        """
        The function delTimer is used to remove a registered timer. The removed
        timer is no longer executed. Single-shot timers are automatically
        removed after the callback is executed, and it is not necessary to use
        delTimer to remove it. If the delTimer function uses an invalid id
        (for example, has been removed), it will generate an error

        A use case for the KBEngine.addTimer reference timer.

        parameters:
            id	integer, timer id to remove
        """

    @staticmethod
    def executeRawDatabaseCommand(command: str, callback: DBCallback,
                                  threadID: int, dbInterfaceName: str):
        """
        This script function executes a database command on the database,
        which is directly parsed by the relevant database.

        Please note that using this function to modify entity data may not be
        effective because if the entity has been checked out, the modified data
        will still be archived by the entity and cause overwriting.

        This function is strongly not recommended for reading or modifying entity data.

        parameters:
            command	This database command will be different for different
                database configuration scenarios. For a MySQL database it is
                an SQL query.
            callback
                Optional parameter, callback object (for example, a function)
                called back with the command execution result.

                This callback has 4 parameters:
                    result set,
                    number of rows affected,
                    auto value,
                    error message.

                Example:
                    def sqlcallback(result, rows, insertid, error):
                        print(result, rows, insertid, error)

                As the above example shows, the result parameter corresponds to the
                "result set", and the result set parameter is a row List. Each
                line is a list of strings containing field values. If the command
                execution does not return a result set (for example, a DELETE command),
                or the command execution encounters an error, the result set is None.

                The rows parameter is the "number of rows affected", which is an
                integer indicating the number of rows affected by the command
                execution. This parameter is only relevant for commands that do
                not return results (such as DELETE).
                This parameter is None if there is a result set return or if there
                is an error in the command execution.

                The insertid is a long value, similar to an entity's databaseID.
                When successfully inserting data int a table with an auto long type
                field, it returns the data at the time of insertion.
                More information can be found in mysql's mysql_insert_id() method.
                In addition, this parameter is only meaningful when the database
                type is mysql.

                Error corresponds to the "error message", when the command execution
                encounters an error, this parameter is a string describing the error.
                This parameter is None when the command execution has not occurred.

            threadID	int32, optional parameter, specifies a thread to process
                this command. Users can use this parameter to control the execution
                order of certain commands (dbmgr is multi-threaded). The default
                is not specified. If threadId is the ID of an entity, it will be
                added to the entity's archive queue and written by the thread one
                by one.

            dbInterfaceName	string, optional parameter, specifies a database
                interface. By default it uses the "default" interface. Database
                interfaces are defined by kbengine_defaults.xml->dbmgr->databaseInterfaces.
        """

    @staticmethod
    def urlopen(url: _UrlType, callback: _HttpCBType, postData: bytes,
                headers: _HeadersType):
        """This script function is providing an external HTTP/HTTPS asynchronous request.

        parameters:
            url	A valid HTTP/HTTPS URL.
        callback
            Optional parameter with a callback object (for example, a function)
            that requests execution results. This callback takes five parameters:
                the HTTP request return code (eg: 200),
                the returned content,
                the returned HTTP protocol header,
                whether it succeeded,
                and the requested URL.

            Example:
            def onHttpCallback(httpcode, data, headers, success, url):
                print(httpcode, data, headers, success, url)

            As the above example shows:

                httpcode: The parameter corresponds to the "HTTP request return code",
                    is an integer.
                data: The parameter is “returned content &rdquo;, it is a string.
                headers: The parameter is the HTTP protocol header returned by the
                    server, such as:{"Content-Type": "application/x-www-form-urlencoded"},
                    is an dict.
                success: Whether the execution is successful or not, when the
                    request execution has an error, it is False, and the error '
                    information can be further judged by httpcode.
                url: Is the URL used by the request.

        postData	Optional parameter, the default is GET mode request server.
            If you need POST mode, please provide the content that needs POST.
            The engine will automatically request the server using POST, is an
            bytes.
        headers	Optional parameter, HTTP header used when requesting, such
            as: {"Content-Type": "application/x-www-form-urlencoded"}, is an dict.
        """

    @staticmethod
    def onDBMgrReady():
        """This function is called back when the current process is ready.

        Note: This callback interface must be implemented in the portal module
        ( kbengine_defaults.xml ->entryScriptFile).
        """

    @staticmethod
    def onDBMgrShutDown():
        """This function is called when the process shuts down.

        Note: This callback interface must be implemented in the portal module
        ( kbengine_defaults.xml ->entryScriptFile).
        """

    @staticmethod
    def onReadyForShutDown() -> Union[bool, int]:
        """
        If this function is implemented in a script, the callback function is
        called when the process is ready to exit.

        You can use this callback to control when the process exits.

        Note: This callback interface must be implemented in the portal module
        ( kbengine_defaults.xml ->entryScriptFile).

        returns:
            bool, if it returns True, it allows the process to exit. Returning
                other values will cause the process to ask again after
                a period of time.
        """
        return True

    @staticmethod
    def onSelectAccountDBInterface(accountName: str) -> str:
        """
        When implemented in a script, this callback returns the database
        interface corresponding to an account. After the interface is selected,
        the dbmgr operations related to this account are completed by the
        corresponding database interface.

        Database interfaces are defined in kbengine_defaults.xml->dbmgr->databaseInterfaces.
        Use this function to determine which database the account should be
        stored in based on accountName.

        Note: This callback interface must be implemented in the portal module
        ( kbengine_defaults.xml ->entryScriptFile).

        parameters:
            accountName	string, the name of the account.

        returns:
            string, the database interface name (database interfaces are
                defined in kbengine_defaults.xml->dbmgr->databaseInterfaces).
        """
        return ''


class IKBEngineInterfacesModule:
    """
    The Interfaces process handles access to third-party platforms for the
    KBEngine server.
    """

    @staticmethod
    def addTimer(initialOffset: float,
                 repeatOffset: Union[float, _AddTimerCBType] = -1.0,
                 callbackObj: Optional[_AddTimerCBType] = None) -> _TimerID:
        """Register a timer.

        The timer is triggered by the callback function callbackObj. The callback function will be executed the first time after "initialOffset" seconds, and then will be executed once every "repeatOffset" seconds.

        Example:

        Here is an example of using addTimer
            ```
            import KBEngine

            # Add a timer, perform the first time after 5 seconds, and execute once every 1 second. The user parameter is 9
            KBEngine.addTimer( 5, 1, onTimer_Callbackfun )

            # Add a timer and execute it after 1 second. The default user parameter is 0.
            KBEngine.addTimer( 1, onTimer_Callbackfun )

            def onTimer_Callbackfun( id ):
                print "onTimer_Callbackfun called: id %i" % ( id )
                # If this is a repeated timer, it is no longer needed, call the following function to remove:
                #     KBEngine.delTimer( id )
            ```

        parameters:
            initialOffset	float, specifies the time interval in seconds for
                the timer to register from the first callback.
            repeatOffset	float, specifies the time interval (in seconds)
                between each execution after the first callback execution. You
                must remove the timer with the function delTimer, otherwise it
                will continue to repeat. Values less than or equal to 0 will
                be ignored.
            callbackObj	function, the specified callback function object

        returns:
            integer, the internal id of the timer. This id can be used toremove
                the timer using delTimer
        """
        return -1

    @staticmethod
    def delTimer(id: _TimerID):
        """
        The function delTimer is used to remove a registered timer. The removed
        timer is no longer executed. Single-shot timers are automatically
        removed after the callback is executed, and it is not necessary to use
        delTimer to remove it. If the delTimer function uses an invalid id
        (for example, has been removed), it will generate an error

        A use case for the KBEngine.addTimer reference timer.

        parameters:
            id	integer, timer id to remove
        """

    @staticmethod
    def accountLoginResponse(commitName: str, realAccountName: str,
                             extraDatas: bytes, errorCode: int):
        """
        After onRequestAccountLogin is called back, the script needs to call
        this function to give the result of the login processing.

        parameters:
            commitName	string, the name submitted by the client when requested.
            realAccountName	string, returns the real account name (if there
                are no special requirements it is ually commitName, this is
                available when logging in with various alias accounts).
            extraDatas	bytes, the data attached to the client's request. Can
                forward the data to a third-party platform and provide an
                opportunity to modify it. This parameter can be read in the
                script via the getClientDatas interface of the base entity.
            errorCode	integer, error code. If you need to interrupt the
                user's behavior, you can set the error code here. The error
                code can be referenced (KBEngine.SERVER_ERROR_*, described in
                kbengine/kbe/res/server/server_errors.xml),
                otherwise submitting KBEngine.SERVER_SUCCESS represents
                permitting the login.
        """

    @staticmethod
    def createAccountResponse(commitName: str, realAccountName: str,
                              extraDatas: bytes, errorCode: int):
        """
        After onRequestCreateAccount is called back, the script needs to call
        this function to give an account creation processing result.

        parameters:
            commitName	string, the name submitted by the client when requested.
            realAccountName	string, returns the real account name (if there are
                no special requirements it is ually commitName, this is
                available when logging in with various alias accounts).
            extraDatas	bytes, the data attached to the client's request. Can
                forward the data to a third-party platform and provide an
                opportunity to modify it. This parameter can be read in the
                script via the getClientDatas interface of the base entity.
            errorCode	integer, error code. If you need to interrupt the user's
                behavior, you can set the error code here. The error code
                can be referenced (KBEngine.SERVER_ERROR_*, described in
                kbengine/kbe/res/server/server_errors.xml), otherwise
                submitting KBEngine.SERVER_SUCCESS represents permitting the login.
        """

    @staticmethod
    def chargeResponse(orderID: str, extraDatas: bytes, errorCode: int):
        """
        After onRequestCharge is called back, the script needs to call this
        function to give the billing result.

        parameters:
            ordersID	string, the ID of the order
            extraDatas	bytes, the data attached to the client's request. Can
                forward the data to a third-party platform and provide an
                opportunity to modify it. This parameter can be read in the
                script via the getClientDatas interface of the base entity.
            errorCode	integer, error code. If you need to interrupt the
                user's behavior, you can set the error code here. The error
                code can be referenced (KBEngine.SERVER_ERROR_*, described
                in kbengine/kbe/res/server/server_errors.xml), otherwise
                submitting KBEngine.SERVER_SUCCESS represents permitting
                the login.
        """

    @staticmethod
    def executeRawDatabaseCommand(command: str,
                                  callback: Optional[DBCallback] = None,
                                  threadID: Optional[int] = None,
                                  dbInterfaceName: Optional[str] = None):
        """
        This script function executes a database command on the database,
        which is directly parsed by the relevant database.

        Please note that using this function to modify entity data may not be
        effective because if the entity has been checked out, the modified data
        will still be archived by the entity and cause overwriting.

        This function is strongly not recommended for reading or modifying entity data.

        parameters:
            command	This database command will be different for different
                database configuration scenarios. For a MySQL database it is
                an SQL query.
            callback

        Optional parameter, callback object (for example, a function) called
        back with the command execution result.
        This callback has 4 parameters: result set, number of rows affected,
        auto value, error message.

        Example:
            def sqlcallback(result, rows, insertid, error):
                print(result, rows, insertid, error)

            As the above example shows, the result parameter corresponds to the
            "result set", and the result set parameter is a row List. Each line
            is a list of strings containing field values. If the command execution
            does not return a result set (for example, a DELETE command), or the
            command execution encounters an error, the result set is None.

            The rows parameter is the "number of rows affected", which is an
            integer indicating the number of rows affected by the command execution.
            This parameter is only relevant for commands that do not return results
            (such as DELETE).
            This parameter is None if there is a result set return or if there is
            an error in the command execution.

            The insertid is a long value, similar to an entity's databaseID. When
            successfully inserting data int a table with an auto long type field,
            it returns the data at the time of insertion.
            More information can be found in mysql's mysql_insert_id() method. In
            addition, this parameter is only meaningful when the database type is
            mysql.

            Error corresponds to the "error message", when the command execution
            encounters an error, this parameter is a string describing the error.
            This parameter is None when the command execution has not occurred.

        threadID	int32, optional parameter, specifies a thread to process
            this command. Users can use this parameter to control the execution
            order of certain commands (dbmgr is multi-threaded). The default is
            not specified. If threadId is the ID of an entity, it will be added
            to the entity's archive queue and written by the thread one by one.
        dbInterfaceName	string, optional parameter, specifies a database
            interface. By default it uses the "default" interface. Database
            interfaces are defined by kbengine_defaults.xml->dbmgr->databaseInterfaces.
        """
        pass

    @staticmethod
    def urlopen(url: _UrlType, callback: _HttpCBType, postData: bytes,
                headers: _HeadersType):
        """This script function is providing an external HTTP/HTTPS asynchronous request.

        parameters:
            url	A valid HTTP/HTTPS URL.
        callback
            Optional parameter with a callback object (for example, a function)
            that requests execution results. This callback takes five parameters:
                the HTTP request return code (eg: 200),
                the returned content,
                the returned HTTP protocol header,
                whether it succeeded,
                and the requested URL.

            Example:
            def onHttpCallback(httpcode, data, headers, success, url):
                print(httpcode, data, headers, success, url)

            As the above example shows:

                httpcode: The parameter corresponds to the "HTTP request return code",
                    is an integer.
                data: The parameter is “returned content &rdquo;, it is a string.
                headers: The parameter is the HTTP protocol header returned by the
                    server, such as:{"Content-Type": "application/x-www-form-urlencoded"},
                    is an dict.
                success: Whether the execution is successful or not, when the
                    request execution has an error, it is False, and the error '
                    information can be further judged by httpcode.
                url: Is the URL used by the request.

        postData	Optional parameter, the default is GET mode request server.
            If you need POST mode, please provide the content that needs POST.
            The engine will automatically request the server using POST, is an
            bytes.
        headers	Optional parameter, HTTP header used when requesting, such
            as: {"Content-Type": "application/x-www-form-urlencoded"}, is an dict.
        """

    @staticmethod
    def onInterfaceAppReady():
        """This function is called back when the current process is ready.

        Note: This callback interface must be implemented in the portal module
        ( kbengine_defaults.xml ->entryScriptFile).
        """

    @staticmethod
    def onInterfaceAppShutDown():
        """This function is called back when the process shuts down.

        Note: This callback interface must be implemented in the portal module
        (kbengine_defaults.xml ->entryScriptFile).
        """

    @staticmethod
    def onRequestCreateAccount(registerName: str, password: str, datas: bytes):
        """
        This callback is called when the client requests the server to create
        an account.

        The data can be checked and modified within this function, and the
        final result is submitted to the engine through KBEngine.createAccountResponse.

        Note: This callback interface must be implemented in the portal module
        ( kbengine_defaults.xml ->entryScriptFile).

        parameters:
            registerName	string, the name submitted by the client when requested.
            password	string, password
            datas	bytes, the data attached to the client's request, can
                forward data to a third-party platform.
        """

    @staticmethod
    def onRequestAccountLogin(loginName: str, password: str, datas: bytes):
        """
        This callback is called when the client requests the server to login
        an account.

        The data can be checked and modified within this function, and the final
        result is submitted to the engine through KBEngine.accountLoginResponse.

        Note: This callback interface must be implemented in the portal module
        (kbengine_defaults.xml ->entryScriptFile).

        parameters:
            loginName	string, the name submitted by the client when requested.
            password	string, password.
            datas	bytes, the data attached to the client request, can forward
                data to a third-party platform.
        """

    @staticmethod
    def onRequestCharge(ordersID: int, entityDBID: int, datas: bytes):
        """
        This callback is invoked when billing is requested (usually
        KBEngine.charge is called on baseapp).

        Data can be checked and modified within this function, and the final
        result is submitted to the engine via KBEngine.chargeResponse.

        Note: This callback interface must be implemented in the portal module
        (kbengine_defaults.xml ->entryScriptFile).

        parameters:
            ordersID	uint64, the ID of the order.
            entityDBID	uint64, the entity DBID of the submitted order.
            datas	bytes, the data attached to the client request, can
                forward data to a third-party platform.
        """


class IKBEngineLoggerModule:

    @staticmethod
    def addTimer(initialOffset: float,
                 repeatOffset: Union[float, _AddTimerCBType] = -1.0,
                 callbackObj: Optional[_AddTimerCBType] = None) -> _TimerID:
        """Register a timer.

        The timer is triggered by the callback function callbackObj. The callback function will be executed the first time after "initialOffset" seconds, and then will be executed once every "repeatOffset" seconds.

        Example:

        Here is an example of using addTimer
            ```
            import KBEngine

            # Add a timer, perform the first time after 5 seconds, and execute once every 1 second. The user parameter is 9
            KBEngine.addTimer( 5, 1, onTimer_Callbackfun )

            # Add a timer and execute it after 1 second. The default user parameter is 0.
            KBEngine.addTimer( 1, onTimer_Callbackfun )

            def onTimer_Callbackfun( id ):
                print "onTimer_Callbackfun called: id %i" % ( id )
                # If this is a repeated timer, it is no longer needed, call the following function to remove:
                #     KBEngine.delTimer( id )
            ```

        parameters:
            initialOffset	float, specifies the time interval in seconds for
                the timer to register from the first callback.
            repeatOffset	float, specifies the time interval (in seconds)
                between each execution after the first callback execution. You
                must remove the timer with the function delTimer, otherwise it
                will continue to repeat. Values less than or equal to 0 will
                be ignored.
            callbackObj	function, the specified callback function object

        returns:
            integer, the internal id of the timer. This id can be used toremove
                the timer using delTimer
        """
        return -1

    @staticmethod
    def delTimer(id: _TimerID):
        """
        The function delTimer is used to remove a registered timer. The removed
        timer is no longer executed. Single-shot timers are automatically
        removed after the callback is executed, and it is not necessary to use
        delTimer to remove it. If the delTimer function uses an invalid id
        (for example, has been removed), it will generate an error

        A use case for the KBEngine.addTimer reference timer.

        parameters:
            id	integer, timer id to remove
        """

    @staticmethod
    def urlopen(url: _UrlType, callback: _HttpCBType, postData: bytes,
                headers: _HeadersType):
        """This script function is providing an external HTTP/HTTPS asynchronous request.

        parameters:
            url	A valid HTTP/HTTPS URL.
        callback
            Optional parameter with a callback object (for example, a function)
            that requests execution results. This callback takes five parameters:
                the HTTP request return code (eg: 200),
                the returned content,
                the returned HTTP protocol header,
                whether it succeeded,
                and the requested URL.

            Example:
            def onHttpCallback(httpcode, data, headers, success, url):
                print(httpcode, data, headers, success, url)

            As the above example shows:

                httpcode: The parameter corresponds to the "HTTP request return code",
                    is an integer.
                data: The parameter is “returned content &rdquo;, it is a string.
                headers: The parameter is the HTTP protocol header returned by the
                    server, such as:{"Content-Type": "application/x-www-form-urlencoded"},
                    is an dict.
                success: Whether the execution is successful or not, when the
                    request execution has an error, it is False, and the error '
                    information can be further judged by httpcode.
                url: Is the URL used by the request.

        postData	Optional parameter, the default is GET mode request server.
            If you need POST mode, please provide the content that needs POST.
            The engine will automatically request the server using POST, is an
            bytes.
        headers	Optional parameter, HTTP header used when requesting, such
            as: {"Content-Type": "application/x-www-form-urlencoded"}, is an dict.
        """

    @staticmethod
    def onLoggerAppReady():
        """This function is called back when the current process is ready.

        Note: This callback interface must be implemented in the portal module
        ( kbengine_defaults.xml ->entryScriptFile).
        """

    @staticmethod
    def onLoggerAppShutDown():
        """This function is called back when the process shuts down.

        Note: This callback interface must be implemented in the portal module
        (kbengine_defaults.xml ->entryScriptFile).
        """

    @staticmethod
    def onLogWrote(datas: bytes):
        """
        If this function is implemented in the script, it is invoked when the
        logger process obtains a new log.

        The database interface is defined in kbengine_defaults.xml->dbmgr->databaseInterfaces.

        Note: This callback interface must be implemented in the portal module
        (kbengine_defaults.xml ->entryScriptFile).

        parameters:
            datas	bytes, log data.
        """

    @staticmethod
    def onReadyForShutDown() -> Union[bool, int]:
        """
        If this function is implemented in the script, it is called when the
        process is ready to exit.

        You can use this callback to control when the process exits.

        Note: This callback interface must be implemented in the portal module
        (kbengine_defaults.xml ->entryScriptFile).

        returns:
            bool, if it returns True, it allows the process to exit. Returning
                other values will cause the process to ask again after a period of time.
        """
        return False
