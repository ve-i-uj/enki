# Changelog

## [0.6.0] - 2023-06-13

### Added

- The new component "Supervisor" replacing the Machine component was added
- Implementation of the TCP server for the component Supervisor
- Commands to check if a component is alive
- The script forced adds the hasCell, hasBase, hasClient attributes to the entity in the entities.xml and the script can add empty entity modules
- The handler, the command for the message "Machine::lookApp" were added
- Added new command to send message "Machine::queryComponentID"
- Added "debugpy" package to the project dependencies to debug Supervisor in VSCode
- The implementation of the UDP server for the component
- Added new handlers for the "Cellapp::*" messages
- Added new handler for the "DBMgr::onAppActiveTick" message
- Added a new module contains the message handlers of the Machine component
- The MsgReader can read a bare message data without message envelope
- Added a new script to parse hex stream of message from WireShark (MsgReader)
- A new command scripts sending `all components`::queryLoad were added
- The command script for sending Machine::onQueryAllInterfaceInfos uses the stream client
- New children classes of the command and the client to handle server stream
- A new script for sending the Logger::queryLoad message to Logger
- The script modify_kbe_config.py moved to Enki from the project Shedu

### Changed

- The base class "Command" has the state to recognize rejected connection
- check_confis.sh was moved to the "scripts" dir
- The settings.py module was split (a separate module for an each executable file)
- Merged the tcp client class and its connection
- The generator of the entities code was renamed to "egenerator"
- The script modify_kbe_config.py reads kbengine.xml attributes from the configuration file

### Fixed

- The script "set_version.sh" can read the arguments "-h" and "--help"

## [0.5.1] - 2023-01-20

### Added

- The example of the request to the Machine component using the "enki" library

### Fixed

- The unit and integration tests were updated

## [0.5.0] - 2023-01-19

### Changed

- The project code and logic split on game layer logic and net layer logic. Every layer is serving in the separate thread.
- The entity serializators are code generated classes for serialization of the RPC to the server. They have dynamicly generated methods based on the "entities_def" files.
- The console game example was updated for the enki threaded realization
- The enki package is the main user interface for the game logic layer (it contains a few function to start and to stop the net thread and the KBEngine module)

### Added

- Code generation for entities serializators
- The KBEngine module implementation was added
- Makefile was added like API for the Enki project
- There is .env file to configure project commands
- The example of using enki to healthcheck kbe (send_hello.py)

## [0.4.1] - 2022-09-25

### Changed

- The application stop actions are synchronous
- The server tick is just a asyncio task now
- Using only Position and Direction types for Entity.position and Entity.direction

## [0.4.0] - 2022-09-22

### Changed

- Using the asyncio protocol interface instead of the tornado library

## [0.3.0] - 2022-09-19

### Added

- The example how to start enki application
- A new class to move the controlled entity at the server
- The cellapp message descriptions for "forwardEntityMessageToCellappFromClient"
- The scripts to generate code to the user defined directory

### Changed

- Generated types, entities, kbenginexml files were moved out of the project
- Ninmah generates code to the external directory
- Enki contains only messages descriptions and these descriptions are not generated

## [0.2.0] - 2022-09-07

### Added

- The project can send and receive all client-server kbengine messages
- The scripts to manage the project version were added
- Parsing of kbengine.xml + merge with default config data
- Scripts to generate code and start the application
- Integration tests

### Changed

- The "onAppActiveTickCB" handler was fixed (a debug assert was removed)

### Fixed

- Gracefully shutdown

## [0.1.0] - 2022-08-23

### Added

- Code generation of kbe entity components
- The deserialization of the kbe entity components
- Handling of the "onRemoteMethodCall" message for components was added
- A new handler for the "OnEntityDestroyedHandler" message was added

### Changed

- Ninmah was moved to the "tools" directory
- Damkina was renamed to the "application" package name of the enki
- Code generation for entities and components is using jinja templates
- The python version of the project was updated to Py3.9
- The structure of the "tests" directory was updated
- Generated entities were updated

### Fixed

- The code generator was fixed to use aliasID
- The handler for the "onRemoteMethodCall" message was fixed (uint8 vs uint16)
- Entity properties were not updated

## [0.0.0] - 2022-08-21

### Added

- A kbengine client to connect and to serve kbe server connections
- Serializer and deserializer of kbe messages
- A code generator of the kbe entities (ninmah)
- A new parsers for the "entity_defs" directory and entities.xml was added
- Type system to build a kbe application
- A draft of the kbengine application (damkina)
