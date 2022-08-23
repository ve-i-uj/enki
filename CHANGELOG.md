
# Changelog

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
