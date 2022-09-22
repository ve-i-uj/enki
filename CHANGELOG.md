# Changelog

## [0.4.0] - 2021-09-22

### Changed

- Using the asyncio protocol interface instead of the tornado library

## [0.3.0] - 2021-09-19

### Added

- The example how to start enki application
- A new class to move the controlled entity at the server
- The cellapp message descriptions for "forwardEntityMessageToCellappFromClient"
- The scripts to generate code to the user defined directory

### Changed

- Generated types, entities, kbenginexml files were moved out of the project
- Ninmah generates code to the external directory
- Enki contains only messages descriptions and these descriptions are not generated

## [0.2.0] - 2021-09-07

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

## [0.1.0] - 2021-08-23

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
