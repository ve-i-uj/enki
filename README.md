# Enki (a Python library for networking with KBEngine components)

## Overview

Enki is a Python library for networking with [KBEngine](https://github.com/kbengine/kbengine "Open source MMOG server engine") components.

The library contains classes for processing, receiving, sending messages between any KBEngine components (both server and client). Implemented classes of low-level clients (UDP, TCP) that send, receive, serialize, deserialize messages of [KBEngine](https://github.com/kbengine/kbengine "Open source MMOG server engine"), both via an open TCP channel, and open a callback server (UDP, TCP) to receive a response from another cluster component.

Initially, I created the project as a client plugin for KBEngine in Python. But in the process of development, the project grew and I divided it into a library and development tools for KBEngine based on this library. Below is a list of what has been implemented.

There is also this [README in Russian](README_RU.md) (так же есть [README на русском языке](README_RU.md))

## Table of contents

[Installation](#instalation)

[The component "Supervisor"](#supervisor)

[Message Reader](#msgreader)

[Healthcheck scripts](#healthcheck)

[Assets API Code Gegerator](#assetsapi)

[The script "modify_kbe_config"](#modify_kbe_config)

[Assets normalization](#normalize_entitiesxml)

[ClientApp](#clientapp)

[ClientApp threads](#clientapp_threads)

[Tests](#tests)

<a name="instalation"><h2>Installation</h2></a>

```bash
REPOS_DIR=<YOUR_REPOS_DIR>
cd $REPOS_DIR
git clone git@github.com:ve-i-uj/enki.git
cd enki
sudo pip install pipenv
pipenv install
pipenv shell
```

<a name="supervisor"><h2>The component "Supervisor"</h2></a>

When running each server component of the KBEngine architecture in a separate Docker container, I ran into the problem that the KBEngine Machine component only registers other components if they are located on the same host as the Machine. And when running each component in a separate Docker container, the cluster did not work because Machine did not register components and they could not find each other at startup.

To solve this problem, I rewrote the Machine component repeating the Machine API so that the KBEngine cluster can be deployed into Docker. I called the component Supervisor. [Supervisor](enki/app/supervisor) is written based on the Python library "Enki".

<a name="msgreader"><h2>Message Reader</h2></a>

There is [a script](tools/msgreader.py) that can be used to analyze network traffic between KBEngine components. Using the script, you can analyze both KBEngine messages in an envelope (when its id and length are passed in the message head), and bare messages to a callback address (bare messages doesn't have a message id and its length and sent to a specific port opened by the component).

WireShark is used to capture traffic. Next, you need to select a package between the KBEngine server components and copy the package data in hexadecimal form.

![msgreader_example](https://github.com/ve-i-uj/enki/assets/6612371/2da966da-f9d1-4cd3-8ced-546124286064)

For the `msgreader` script to work in Python, you need to activate the Python virtual environment. You need [to activate]() it once and then use the script.

The script needs to get the message destination component and the binary data copied in hexadecimal form. The script deserializes the data and displays it in the console in a convenient readable format. Fields with double underscores are added by the script itself for easy reading, these fields were not sent in the message. For example, the `addr` and `finderRecvPort` fields in the message are encoded. The handler of this message adds the `__callback_address` field to the result, in which the address is already in a clear and familiar form.

In this case, the request is sent to the Machine component. The output of the script shows that the Baseapp component requests the address of the Logger component and asks to send a response to the address 172.24.0.9:20747.

```console
(enki) leto@leto-PC:/tmp/enki$ python tools/msgreader.py machine 01002300e80300006b62656e67696e650006000000591b0000000000000a000000ac180009510b
[INFO] 2023-06-10 11:34:48,908 [msgreader.py:168 - main()] *** Machine::onFindInterfaceAddr (id = 1) ***
{   'msg_id': 1,
    'result': {   '__callback_address': AppAddr(host='172.24.0.9', port=20747),
                  '__component_type': <ComponentType.BASEAPP: 6>,
                  '__find_component_type': <ComponentType.LOGGER: 10>,
                  'addr': 151001260,
                  'componentID': 7001,
                  'componentType': 6,
                  'findComponentType': 10,
                  'finderRecvPort': 2897,
                  'uid': 1000,
                  'username': 'kbengine'},
    'success': True,
    'text': ''}
```

Further, in the traffic captured by WireShark, we find the response to this message, because the reply address is known (172.24.0.9:20747).

![callback_response](https://github.com/ve-i-uj/enki/assets/6612371/2436b950-b046-49a6-b31a-1c11c3409099)

The KBEngine sources know which message will be sent in response and that the response will be sent without an envelope (i.e. without the message id and its length). In this case, to deserialize the message, the script needs to be know what the message is in the `--bare-msg` argument (--bare-msg "Machine::onBroadcastInterface"). The argument must come after the data.

<details>

<summary>The example of reading "Machine::onBroadcastInterface"</summary>

```console
(enki) leto@leto-PC:/tmp/enki$ python tools/msgreader.py machine e80300006b62656e67696e65000a000000d107000000000000591b000000000000ffffffffffffffffffffffffac180004ec35ac1800049dad0007000000000000000000000000f031010000000000000000000000000000000000000000000000000000000000d084000000000000ac1800044f82 --bare-msg "Machine::onBroadcastInterface"
[INFO] 2023-06-10 11:54:22,014 [msgreader.py:130 - main()] *** Machine::onBroadcastInterface (id = 8) ***
{   'msg_id': 8,
    'result': {   '__callback_address': AppAddr(host='172.24.0.4', port=20354),
                  '__component_type': <ComponentType.LOGGER: 10>,
                  '__external_address': AppAddr(host='172.24.0.4', port=40365),
                  '__internal_address': AppAddr(host='172.24.0.4', port=60469),
                  'backRecvAddr': 67115180,
                  'backRecvPort': 33359,
                  'componentID': 2001,
                  'componentIDEx': 7001,
                  'componentType': 10,
                  'cpu': 0.0,
                  'extaddr': 67115180,
                  'extaddrEx': '',
                  'extport': 44445,
                  'extradata': 0,
                  'extradata1': 0,
                  'extradata2': 0,
                  'extradata3': 34000,
                  'globalorderid': -1,
                  'grouporderid': -1,
                  'gus': -1,
                  'intaddr': 67115180,
                  'intport': 13804,
                  'machineID': 0,
                  'mem': 0.0,
                  'pid': 7,
                  'state': 0,
                  'uid': 1000,
                  'usedmem': 20049920,
                  'username': 'kbengine'},
    'success': True,
    'text': ''}
```

</details>
<br/>

As you can see from the response, the Machine component sends the data of the Logger component to the callback address.

Implemented messages are listed [here](enki/handler/serverhandler/__init__.py)

<a name="healthcheck"><h2>Healthcheck scripts</h2></a>

I wrote [scripts to test the health](tools/cmd) of a KBEngine cluster based on my Python library "Enki". The scripts are based on command classes that encapsulate a network connection to a server component, data serializing and receiving a response. Commands (like the library Enki) are written in asynchronous Python style.

The scripts are used in [my project to deploy a KBEngine cluster in Docker](https://github.com/ve-i-uj/shedu).

<details>

<summary>An example of the healtcheck script</summary>

```python
"""Check if the component is alive.

For this command to work, you first need to find out the internal address of the component,
because connections from outside are discarded (lookApp only works for INTERNAL
connections).

But, this script is used to check the health of the Supervisor
component. Supervisor has the API of the component "Machine", but it doesn't
have restriction for INTERNAL address, so the script will get response.
"""

import asyncio
import logging
import sys

import environs

from enki import settings
from enki.core.enkitype import AppAddr
from enki.core import msgspec
from enki.command import RequestCommand
from enki.core.kbeenum import ComponentType
from enki.core.message import Message
from enki.handler.serverhandler.common import OnLookAppParsedData
from enki.misc import log

logger = logging.getLogger(__name__)

_env = environs.Env()

MACHINE_ADDR = AppAddr(
    _env.str('KBE_MACHINE_HOST'),
    _env.int('KBE_MACHINE_TCP_PORT')
)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    cmd_lookApp = RequestCommand(
        MACHINE_ADDR,
        Message(msgspec.app.machine.lookApp, tuple()),
        resp_msg_spec=msgspec.custom.onLookApp.change_component_owner(ComponentType.MACHINE),
        stop_on_first_data_chunk=True
    )
    res = await cmd_lookApp.execute()
    if not res.success:
        logger.error(res.text)
        sys.exit(1)

    msgs = res.result
    msg = msgs[0]
    pd = OnLookAppParsedData(*msg.get_values())

    logger.info(pd.asdict())
    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())

```

</details>
<br/>


<a name="assetsapi"><h2>Assets API Code Gegerator</h2></a>

The tool generates parent classes of server-side entities that fully reflect the interface from `*.def` files. This speeds up development with the help of code analyzers such as Pylance (the default code analyzer in VSCode). The generated code has links to entity def files, their remote methods and types, which makes it easier to navigate through the code.

Generated entity classes are parsed without errors by [Enterprise Architect](https://sparxsystems.com) - this makes it possible to import generated classes into `Enterprise Architect` and build diagrams to visually describe the client-server logic (for example, through a sequence diagram, i.e. j. Generated entities immediately contain remote methods).

For example, specifically for the Avatar entity, its full API will be generated: methods, properties, remote calls to other components, parameter types defined in the `entity_defs/Avatar.def` and `types.xml` files (including types that return converters connected to FIXED_DICT).

This tool is an interface code generator for entities defined in `entity_defs`. It is enough to create xml files of game entities and then run the parent class generator. Interfaces will be generated that have all the methods and properties defined in `entity_defs`. These parent classes, when inherited, will allow the IDE to point out errors in the use of methods even before the game starts and hint at the interface of remote methods of the entity (and thus save development time). It also generates all types from `types.xml` for remote call type hints.

![Peek 2023-08-15 17-01](https://github.com/ve-i-uj/enki/assets/6612371/ff762b3a-fad8-44fb-943c-3070a3cc01cb)

Examples (using code `kbengine_demos_assets`):

<br/>
<details>
<summary>Entity remote method signature hint, based on Account.def</summary>

![image](https://github.com/ve-i-uj/enki/assets/6612371/b37b48b7-2adb-4ebd-9fe9-ef15128de87f)

<br/>

![image](https://github.com/ve-i-uj/enki/assets/6612371/6ff83663-1c3a-4d12-9115-7596b8c0273f)

</details>

<br/>
<details>
<summary>Entity property hint, based on Account.def</summary>

IDE on the generated interface `IBaseAccount` suggests the name of the property and its type
<br/>

![image](https://github.com/ve-i-uj/enki/assets/6612371/e4a03b64-a0d3-4953-ab56-3b16b84effc0)

Determining the property type `Account.characters` (`AvatarInfosList`)
<br/>

![image](https://github.com/ve-i-uj/enki/assets/6612371/647a3941-bede-424b-b210-a07fcd0240fb)

In this case, the property type is the type returned by the converter (`TAvatarInfosList`)

![image](https://github.com/ve-i-uj/enki/assets/6612371/bfaefc4d-07e9-41ad-878b-257785fad093)

The type of the `Account.characters` property is `AVATAR_INFOS_LIST`. B types.xml is written, then `AVATAR_INFOS_LIST` is FIXED_DICT, with the converter `AVATAR_INFOS.AVATAR_INFOS_LIST_PICKLER` connected

```xml
	<AVATAR_INFOS_LIST>	FIXED_DICT
		<implementedBy>AVATAR_INFOS.AVATAR_INFOS_LIST_PICKLER</implementedBy>
		<Properties>
			<values>
				<Type>	ARRAY <of> AVATAR_INFOS </of>	</Type>
			</values>
		</Properties>
	</AVATAR_INFOS_LIST>
```

The code generator understands that a converter is connected to FIXED_DICT. But in order for the generator to understand what type the converter returns, you need to add a type annotation to the `AVATAR_INFOS_LIST_PICKLER.createObjFromDict` method

</details>

<br/>
<details>
<summary>Connecting an API to an interface</summary>

![image](https://github.com/ve-i-uj/enki/assets/6612371/b368a4c1-12e3-4844-ad6e-ed7f8250e48f)

The API for entity interfaces (`scripts/cell/interfaces`) is generated in the `assetsapi.interfaces` package. There will be a separate module for each interface, in this module there will be API classes for inheritance. The API parent classes for entity interfaces (`scripts/cell/interfaces`) already inherit the entity API (`KBEngine.Entity`), so the entity API hints will be immediately present.

</details>

<br/>
<details>
<summary>Entity API</summary>

![image](https://github.com/ve-i-uj/enki/assets/6612371/022d2fb6-0176-4992-b52e-e863909d6f7d)

</details>

<br/>
<details>
<summary>Types</summary>

![image](https://github.com/ve-i-uj/enki/assets/6612371/8ed805d5-a47b-4112-a7df-16fec136adc5)
<br/>
<br/>
<br/>
![image](https://github.com/ve-i-uj/enki/assets/6612371/2dc4fa68-244b-4821-b259-daba38908513)

</details>

<br/>
<details>
<summary>KBEngine API</summary>

![image](https://github.com/ve-i-uj/enki/assets/6612371/0bf61219-4dd5-460d-a07c-41d7b4c3ef19)

</details>
<br/>
<br/>

See also [Demo based example](https://github.com/ve-i-uj/modern_kbengine_demos_assets) where all entities, interfaces, components have connected interfaces/APIs.

### Configuring VSCode

Below is an example of a workspace settings file for VSCode to work with the assets of the KBEngine folder containing game scripts and configuration files. The sequence to save the file in VSCode is: "Open Folder" --> "Sava Workspace As" --> Copy the config content to the workspace file --> Replace the line "/tmp/kbengine_demos_assets" everywhere in the config with the path to your assets. The config below is saved in the `assets/.vscode` folder

<details>
<summary>assets/.vscode/kbengine_demos_assets.code-workspace</summary>

    {
        "folders": [
            {
                "path": ".."
            }
        ],
        "settings": {
            "python.analysis.extraPaths": [
                "${workspaceFolder}/scripts/user_type",
                "${workspaceFolder}/scripts/server_common",
                "${workspaceFolder}/scripts/common",
                "${workspaceFolder}/scripts/data",
            ],
            "files.associations": {
                "*.def": "xml"
            },
            "files.exclude": {
                "**/.git": true,
                "**/.svn": true,
                "**/.hg": true,
                "**/CVS": true,
                "**/.DS_Store": true,
                "**/__pycache__": true
            },
            "python.languageServer": "Pylance",
            "python.analysis.exclude": [
            ],
            "python.analysis.ignore": [
            ],
        },
    }

</details>
<br/>

### Dependencies

The generated API requires the `typing-extensions` Python library included with assets. When the engine will run server-side Python scripts, this library should be there.

There are two solutions here: 1) [quick] just copy the library from the given project (compatibility not guaranteed). You can copy it manually or add the environment variable `ADD_TYPING_EXTENSIONS_LIB=true` when generating the API.

By hand:

```bash
cd enki
cp tools/assetsapi/forcopy/typing_extensions.py /tmp/kbengine_demos_assets/scripts/common/
```

Or the second solution 2) [long] install the library via pip for Python of the same version as KBEngine and under the OS running the KBEngine server (needs Docker installed). The instruction is [here](https://github.com/ve-i-uj/modern_kbengine_demos_assets/).

### Generate server-side entity and type APIs

To generate server entities, you first need to generate the engine API. You must specify the path to the assets folder. The code will be generated in the server_common folder. Note that in this case, the `ADD_TYPING_EXTENSIONS_LIB=true` environment variable is also added. If the `typing_extensions.py` library was added via the Python and pip build as described above, then simply remove this variable.

```bash
cd /tmp
git clone https://github.com/kbengine/kbengine_demos_assets.git
git clone git@github.com:ve-i-uj/enki.git
cd enki
pipenv install
pipenv shell
GAME_ASSETS_DIR=/tmp/kbengine_demos_assets \
    ONLY_KBENGINE_API=true \
    ADD_TYPING_EXTENSIONS_LIB=true \
    python tools/assetsapi/main.py
```

Now there is an engine API code, the `assetsapi` package should appear in the `server_common` folder. In order for the Pylance code analyzer to work correctly, as well as to run the code correctly by the engine, it is necessary to import the engine libraries from the generated `assetsapi` package. During import, the code in `assetsapi` itself determines where to import engine modules from: from the engine itself or you just need to connect the API. Further, in order to generate methods and properties for each specific entity, you need to change `import KBEngine` in the converter modules (`scripts/user_type`) (if there is such an import, as in the case of demo) to an import of this type:

```python
from assetsapi.kbeapi.baseapp import KBEngine
```

This is necessary because the code generator during code generation reads modules containing converters (the `scripts/user_type` folder) and generates entity methods immediately with the type parameters that the converters return (if the converters are annotated with types).

In the case of `kbengine_demos_assets`, simply remove `import KBEngine` in the `AVATAR_INFOS.py` module and `AVATAR_DATA.py` module (because it is not used). In the `KBEDebug.py` module, replace `import KBEngine` with `from assetsapi.kbeapi.baseapp import KBEngine`.

After that you need to run

```bash
GAME_ASSETS_DIR=/tmp/kbengine_demos_assets python tools/assetsapi/main.py
```

An API for entities must be generated. Now we need to connect it.

<details>
<summary>NB (KBEngine module import for cellapp and baseapp)</summary>

Imports for baseapp and cellapp differ in the name of the last module

```python
# For `base` entity component
from assetsapi.kbeapi.baseapp import KBEngine
# For `cell` entity component
from assetsapi.kbeapi.cellapp import KBEngine
```

but for folders like `scripts/user_type`, `common/user_type` or `server_common/user_type` any of these imports can be used. Because part of the API of the `KBEngine` module is common for both components, and in the runtime under the hood of the `assetsapi` package, the `KBEngine` module will be imported from the engine via `import KBEngine` (i.e. immediately for the required component).

</details>
<br/>

### Import modules from the engine (KBEngine and Math)

Engine modules need to be imported from the package `scripts/server_common/assetsapi`

```python

from assetsapi.kbeapi.baseapp import KBEngine
from assetsapi.kbeapi.Math import Vector3

```

### Generation of types from types.xml

This tool also generates data types that are used in entity remote methods. Data types are generated based on `types.xml` types. Generated types are used in the description of method signatures, this is especially true when using FIXED_DICT as a parameter. The generated types are located in the `scripts/server_common/assetsapi/typesxml.py` module, they can be imported from this module and used in entity methods.

<br/>
<details>
<summary>An example of using a generated type</summary>

![image](https://github.com/ve-i-uj/enki/assets/6612371/8ed805d5-a47b-4112-a7df-16fec136adc5)
<br/>
<br/>
<br/>
![image](https://github.com/ve-i-uj/enki/assets/6612371/2dc4fa68-244b-4821-b259-daba38908513)

</details>

If a converter is connected to FIXED_DICT and the converter has method annotations, then the generated methods will immediately use the type returned by the converter.

<br/>
<details>
<summary>Example of adding the type returned by the converter</summary>

Add return type annotations (file `scripts/user_type/AVATAR_INFOS.py`)

![FD_with_converter_2](https://github.com/ve-i-uj/enki/assets/6612371/48ff0f05-1a38-44fe-80e7-cc760a61d8a5)

Regenerate the API and see the required type in the method

![FD_with_converter_1](https://github.com/ve-i-uj/enki/assets/6612371/7a63345d-a941-4b28-b6b5-1689ac27f418)

</details>
<br/>

For converters, FIXED_DICT is generated separately (to the `assetsapi.user_type` package). The generated classes for FIXED_DICT contain information about the keys that can be used in them. Accordingly, Pylance (code analyzer) can indicate situations when unspecified keys are used in the dictionary. The name FIXED_DICT will be the same as in types.xml, only in CamelCase and with "FD" suffix.

If third-party libraries are used in user_type, then they must be added via the SITE_PACKAGES_DIR variable. This should be the Python libraries folder.

Example

```python
...

class AvatarInfosFD(TypedDict):
     """AVATAR_INFOS (<file:///./../../../scripts/entity_defs/types.xml#43>)"""
     dbid: Dbid
     name: str
     roleType: int
     level: int
     data: AvatarData

...
```

Below is an example where the converter has a FIXED_DICT (`AVATAR_INFOS`) type that it will receive into the converter, and then the converter will return the custom type `TAvatarInfos`. The example, for example, shows an attempt to add a key that is not in the description. Pylance in this case indicates an error - this is convenient and helps to catch errors at the development stage.

<br/>
<details>
<summary>An example of using a generated type</summary>

![image](https://github.com/ve-i-uj/enki/assets/6612371/8b4fd257-dc45-4e81-82f0-8d1ea6cc8f22)

</details>
<br/>

### Argument names and method documentation

The generator can give names to arguments and add to the documentation for the generated method. To do this, when describing a remote entity method, you need to add xml comments as follows

```xml
<root>

    <!-- The entity class documentation -->

    <Properties>
    </Properties>

    <BaseMethods>
    </BaseMethods>

    <CellMethods>
    </CellMethods>

    <ClientMethods>
        <!-- The method documentation -->
        <resp_get_avatars>
            <Arg> AVATAR_INFOS </Arg> <!-- parameter_name -->
        </resp_get_avatars>
    </ClientMethods>
</root>
```

<br/>
<details>
<summary>Get generated code with documentation</summary>

![image](https://github.com/ve-i-uj/enki/assets/6612371/80288528-033c-4989-a664-417609b68a64)
<br/>
![image](https://github.com/ve-i-uj/enki/assets/6612371/ebd71a56-54a8-46fa-a08f-8f0cd95c9dcb)

</details>
<br/>

Formation of the parameter name by comment can be disabled by setting the variable `USE_DEF_COMMENTS_LIKE_PARAMS=false`. You may need to disable the formation of parameters based on comments, for example, if comments already exist.

### Diagram of generated classes

The diagram is based on the Avatar entity. The specified classes will either be generated based on the Avatar.def file (IBaseAvatar) or will be in the `assetsapi` package (eg KBEngine.Proxy).

![Class diagram of generated classes (12 08 23)](https://github.com/ve-i-uj/enki/assets/6612371/d72ed351-d8fd-4871-b028-66c9b01e1b0e)

When running code from the KBEngine engine, the generated classes will have an empty body, so they will not conflict with properties and methods from the engine.

### Development Tools

Along with `assetsapi` you can add development tools to `server_common`. Tools can be added by adding the `ADD_ASSETSTOOLS=true` environment variable when generating code. In this case, the `scripts/server_common/assetstools` folder will be created, which will contain the following auxiliary tools.

A description of these tools can be found [in the repository of the server script demo I updated](https://github.com/ve-i-uj/modern_kbengine_demos_assets/).

### Notes

<details>
<summary>Entity Component API</summary>
<br/>

N.B.: The Demo demonstrates that you can create a RemoteCall of a bean by first accessing the owner (ie the entity) and then accessing the property of the entity (which is the bean) and calling the remote method. And this is all done from the body of the component class.

The example in the Demo has a large potential error, which is also confusing when understanding the components API. In theory, the same component class can be used by different entities, and the name of the property that refers to the component can vary from entity to entity. For example, if you add a component with types "Test" of the `Account` entity, but add it under the name `component123`, then the code from the demo will stop working. It won't work, because when you call the Test.onAttached method on a component bound to an `Account` named `component123`, the owner (Account'a) will not have the `component1` property. Conclusion: it is easier and more obvious to make a remote call directly from the component body itself, without resorting to the entity.

Bad example from Demo:

```python
class Test(KBEngine.EntityComponent):

     def onAttached(self, owner):
         INFO_MSG("Test::onAttached(): owner=%i" % (owner.id))
         self.owner.client.component1.helloCB(111)
```

Same thing, but more obvious:

```python
class Test(KBEngine.EntityComponent):

     def onAttached(self, owner):
         INFO_MSG("Test::onAttached(): owner=%i" % (owner.id))
         self.client.helloCB(111)
```

However, if the component is created for a specific entity, then the API of the entity can be hinted in this way:

![image](https://github.com/ve-i-uj/enki/assets/6612371/27a641c7-c57c-44f3-87eb-e32c7c16072f)

<br/>
But it is strongly recommended to connect the API for components without binding them to a specific entity at the code level. The component-to-entity relationship is a one-to-many relationship, not a one-to-one relationship. An example of connecting an API, without being tied to a specific entity:
<br/>
<br/>

![image](https://github.com/ve-i-uj/enki/assets/6612371/ad6d53e2-5580-4571-b0ac-1e5ca29d0ab9)

</details>
<br/>

<details>
<summary>Reading converters from user_type </summary>
<br/>

To read converters, modules from user_type will be imported. To enable the use of FIXED_DICT declarations for annotating FD types in the converter, Python classes are generated from types.xml. The classes are contained in a separate package `assetsapi.user_type`. It turns out that the generated modules, including `assetsapi.user_type`, are imported into converter modules (from `user_type`). But to generate `assetsapi.user_type` you need to read converter modules - and this eventually leads to circular imports. Therefore, before generating the code, a stub module `assetsapi.user_type` is created, which contains all FDs with converters, but of the form `AvatarInfoFD = Dict` (without field descriptions). This will be enough to read the converter modules from `user_type` and then it will be possible to generate a full-fledged `assetsapi.user_type` and `typesxml.py`.

Nuance with `assetsapi.user_type`. Basically `assetsapi.user_type` is a slightly modified copy of `typesxml.py`. This package duplicates the `typesxml.py` module, but with the difference that all FIXED_DICT with converters are replaced here with simple FIXED_DICT (with FD suffix in the name). This is done because the `typesxml.py` module imports a custom type from the converter module (the custom type is the type that the converter converts FIXED_DICT to). But the custom type module itself uses the FIXED_DICTs generated by `typesxml.py`. If we import the generated types from `typesxml.py` into the converter module, we again get a cyclic import (an error). To get around this, I generate `assetsapi.user_type` which is a slightly modified `typesxml.py` module. The `assetsapi.user_type` package should only be used for imports into modules in the user_type directory. The purpose of `assetsapi.user_type` is to allow the FIXED_DICT specification to be specified, which
gets the converter. These generated types are needed *only* to specify the types used by the converters in the user_type folder. *Types from the `assetsapi.user_type` package should not be used in entity methods*, there is a module typesxml.py for this.

### Nuances of generating types from types.xml

Collection types that create other collections within themselves on the fly will not be described in detail. For example

```
<ARRAY_OF_ARRAY> ARRAY <of> ARRAY <of> AVATAR_INFO </of> </of> </ARRAY_OF_ARRAY>
```

will be generated into a type like `ArrayOfArray = List[Array]` (the nested type in this case is just an array, not an array containing AVATAR_INFO). If you need a more detailed description of the type, then it is recommended to use aliases. For example

```
<AVATAR_INFOS> ARRAY <of> AVATAR_INFO </of> </AVATAR_INFOS>
<ARRAY_OF_AVATAR_INFOS> ARRAY <of> AVATAR_INFOS </of> </ARRAY_OF_AVATAR_INFOS>
```

then `ARRAY_OF_AVATAR_INFOS` will be generated into a view type

```
AvatarInfos = List[AvatarInfo]
ArrayOfAvatarInfos = List[AvatarInfos]
```

In this case, nested types will also be specified, which is much clearer and easier for further maintenance. Plus gives the chance to do checks type checker'am.

If the converter does not have a return type, then FIXED_DICT with this converter in the generated code will have the type `Any`.
</details>

<a name="modify_kbe_config"><h2>The script "modify_kbe_config"</h2></a>

[The script](tools/modify_kbeenginexml.py) modifies or adds settings to the key KBEngine configuration file kbengine.xml. The main purpose of the script is to change the KBEngine settings so that the KBEngine cluster can be deployed to Docker.

The script accepts either a file containing the changes to be made (argument "--data-file"), or a string with settings to be changed (argument "--kbengine-xml-args").

The file settings should look like

    root.dbmgr.shareDB=true
    root.interfaces.host=interfaces

An example, see [here](https://github.com/ve-i-uj/shedu/blob/develop/data/kbenginexml.data).

In the case of a file, in the "--data-file" argument, each new line is a change that will be made to the "kbengine.xml" file. If such a setting exists, it will be changed, if such a setting does not exist, it will be added.

In the case of the "--data-file" command line argument, the settings must be separated by a semicolon.

Example: `root.dbmgr.shareDB=true;root.interfaces.host=interfaces`

<a name="normalize_entitiesxml"><h2>Assets normalization</h2></a>

KBEngine has a confusing logic for checking assets, also the behavior of components running on the same host and on different hosts is different. There were problems with kbengine-demo-assets. Almost all entities have  GameObject in their interfaces. GameObject does not have "cell" and "base" methods, but has "cell" and "base" properties. Because of this, the engine, when running components in different containers based on kbengine-demo-assets, displayed errors on starting, such as

    ERROR baseapp01 1000 7001 [2023-06-07 05:15:27 522] - Space::createCellEntityInNewSpace: cannot find the cellapp script(Space)!
    S_ERR baseapp01 1000 7001 [2023-06-07 05:15:27 522] - Traceback (most recent call last):
    File "/opt/kbengine/assets/scripts/base/Space.py", line 24, in __init__
    self.spaceUTypeB = self.cellData["spaceUType"]
    S_ERR baseapp01 1000 7001 [2023-06-07 05:15:27 522] - AttributeError: 'Space' object has no attribute 'cellData'
    INFO baseapp01 1000 7001 [2023-06-07 05:15:27 522] - EntityApp::createEntity: new Space 2007

It turned out that the engine required that entities must specify `hasCell` in the entities.xml file. Since my goal was to work with the default kbengine-demo-assets from the developers, I added [a script](tools/normalize_entitiesxml) that normalizes the entities.xml file. The script, when building the game image, analyzes assets and modifies entities.xml, prescribing `hasCell`, `hasBase` to entities. But this led to the fact that almost all entities had `base` and `cell` components (hasBase=true and hasCell=true) due to GameObject in interfaces. The engine began to require, at startup, to implement modules for entities, for example, base/Monster or cell/Spaces. Then I added to the script "normalize_entitiesxml" the generation of empty modules to such entities when building the image.

<a name="clientapp"><h2>ClientApp</h2></a>

There is fully implemented on Python official [API for client plugins](https://kbengine.github.io//assets/other/kbengine_api.html#client/Modules/KBEngine.html?id=9) of the KBEngine game engine in this project.

The purpose of writing this plugin was to understand the client-server interaction protocol of the multiplayer server game engine KBEngine. The plugin is written in the Python language, because I know this language well.

There are very few significant game development tools in the world of Python, such as even Godot-level game engines. There is PyGame, but PyGame is just a very minimalistic library for moving sprites (imho). Large games, and even more so multiplayer games, developing on PyGame is a Sisyphean labour. Therefore, I have little faith in the practical application of this plugin. However, below will be an example of generating code and running [the official KBEngine demo game](https://github.com/kbengine/kbengine_demos_assets) in the console to demonstrate that the plugin, despite the lack of GUI, is working.

### About the code generator and the plugin

Game entity classes are used to describe the game logic. Interaction with the server parts of the game entity is done by calling the remote methods of the entity through the `cell` and `base` attributes.

Entity APIs (entity classes, methods, properties) are generated by a Python code generator based on the library "enki" (this project). Game entities and entity serializers / deserializers are generated by the code generator. The game entities is an API describing the client-server game logic. The entity serializers serialize remote calls with python types and transferring remote interaction over the network between the client and the KBEngine server.

The code generation of entities and serializers is based on the game configuration files of multiplayer game engine KBengine (types.xml , entities.xml , *.def files from the "assets" folder) and also the code generation is based on the data from the "Client::onImportClientMessages" message requested from the server. Therefore to generate the code of game entities and the plugin on Python, you need the path to the "assets" folder and a running game server with the game described in the "assets".

The "assets" directory in the KBEngine architecture contains configuration files that describe client-server entities (types.xml , entities.xml , *.def files) and Python server game scripts that implement these entities. The "assets" directory is actually the game.

### An example of launching a game based on ClientApp on Python

First, run a KBEngine cluster with demo "assets". Let's deploy on Linux the KBEngine cluster to docker using the Shedu project (my open source project).

```bash
cd /tmp
git clone https://github.com/ve-i-uj/shedu
cd shedu
# This script install jq, make, git, python3
./configure

# The config contains all the necessary information to build the official KBEngine demo game.
cp configs/kbe-v2.5.12-demo.env .env

# Let's assume you have already installed docker and docker-compose. If not run
# bash scripts/prepare/install_docker.sh
# bash scripts/prepare/install_compose_v2.sh

# It may take several minutes
make build_kbe build_game make start_game
```

You now have a running KBEngine cluster. Generate the plug-in code and start the console game.

```bash
cd /tmp
git clone git@github.com:ve-i-uj/enki.git
git clone https://github.com/kbengine/kbengine_demos_assets.git
mkdir /tmp/thegame
cd enki
pipenv install
pipenv shell
export LOGINAPP_HOST="0.0.0.0" \
    LOGINAPP_PORT=20013 \
    GAME_ASSETS_DIR=/tmp/kbengine_demos_assets \
    GAME_ACCOUNT_NAME=1 \
    GAME_PASSWORD=1 \
    GAME_GENERATED_CLIENT_API_DIR=/tmp/thegame/descr \
    LOG_LEVEL=INFO
python tools/egenerator/main.py
```

Now there is a generated plugin in the directory "/tmp/thegame/descr". Based on the parent entity classes from the generated plugin, you can write game logic. An example of game logic can be found [here](examples/console-kbe-demo-client/entities).  I'll just copy the base entity implementations and entry point module from the project.

```bash
cp -R /tmp/enki/examples/console-kbe-demo-client/entities/ /tmp/thegame/entities
cp -R /tmp/enki/examples/console-kbe-demo-client/main.py /tmp/thegame/main.py
```

<details>

<summary>An example of the game logic of the Account entity</summary>

```python
"""The game logic of the "Account" entity."""

from enki.core.kbetype import FixedDict
from enki.core.enkitype import NoValue
from enki.app.clientapp.layer.ilayer import INetLayer

import descr


class Account(descr.gameentity.AccountBase):

    def __init__(self, entity_id, is_player: bool, layer: INetLayer):
        super().__init__(entity_id, is_player, layer)
        self._avatar_info_by_dbid = {}
        self._current_avatar_dbid: int = NoValue.NO_ID

    @property
    def current_avatar_dbid(self):
        return self._current_avatar_dbid

    def onReqAvatarList(self, avatar_infos_list_0: FixedDict):
        super().onReqAvatarList(avatar_infos_list_0)
        dbid: int = NoValue.NO_ID
        for info in avatar_infos_list_0['values']:
            dbid = info['dbid']
            self._avatar_info_by_dbid[dbid] = info
        self._current_avatar_dbid = dbid

    def onCreateAvatarResult(self, entity_substate_0: int, avatar_infos_1: FixedDict):
        super().onCreateAvatarResult(entity_substate_0, avatar_infos_1)
        dbid = avatar_infos_1['dbid']
        self._avatar_info_by_dbid[dbid] = avatar_infos_1
        self._current_avatar_dbid = dbid
```

</details>
<br/>

<details>

<summary>An example of an entry point where the game logs in the server and requests a list of account avatars, chooses the avatar and enter the game  (i.e. an example of simple game logic)</summary>

```python
import logging
import sys
import time

import environs

from enki import settings
from enki.misc import log
from enki.core.enkitype import NoValue, AppAddr

from enki.app import clientapp
from enki.app.clientapp import KBEngine

# Generated code for the concrete assets version (entity methods, properties and types)
import descr
# Implementation of the entity methods for the concrete assets version
import entities

logger = logging.getLogger(__name__)

_env = environs.Env()
GAME_ACCOUNT_NAME: str = _env.str('GAME_ACCOUNT_NAME')
GAME_PASSWORD: str = _env.str('GAME_PASSWORD')


def main():
    # Set logging level
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    # Run network logic in a separate thread
    clientapp.start(
        AppAddr('localhost', 20013),
        descr.description.DESC_BY_UID,
        descr.eserializer.SERIAZER_BY_ECLS_NAME,
        descr.kbenginexml.root(),
        entities.ENTITY_CLS_BY_NAME
    )

    # Login using KBEngine API
    KBEngine.login(GAME_ACCOUNT_NAME, GAME_PASSWORD)
    # This thread is waiting for connection result, so it doesn't need GIL
    stop_time = time.time() + settings.CONNECT_TO_SERVER_TIMEOUT + settings.SECOND * 5
    while not clientapp.is_connected() and stop_time > time.time():
        logger.debug(f'Waiting for server connection '
                     f'or exit by timeout (exit time = {stop_time}, now = {time.time()})')
        clientapp.sync_layers(settings.SECOND * 3)

    if not clientapp.is_connected():
        logger.error('Cannot connect to the server. See log records')
        sys.exit(1)

    logger.info('The client net component is ready')

    from entities.account import Account
    acc: Account = KBEngine.player()  # type: ignore
    if acc is None:
        logger.error('Something is going wrong. There is no Account entity')
        sys.exit(1)

    acc.base.reqAvatarList()
    clientapp.sync_layers(settings.SECOND * 0.5)

    if acc.current_avatar_dbid == NoValue.NO_ID:
        acc.base.reqCreateAvatar(1, f'enki_bot_{acc.id}')
        clientapp.sync_layers(settings.SECOND * 0.5)

    if acc.current_avatar_dbid == NoValue.NO_ID:
        logger.error('Something is going wrong. See server log records')
        sys.exit(1)

    acc.base.selectAvatarGame(acc.current_avatar_dbid)

    try:
        while True:
            clientapp.sync_layers()
    except KeyboardInterrupt:
        clientapp.stop()
    logger.info(f'Done')


if __name__ == '__main__':
    main()
```

</details>
<br/>

Run the console client example to see how the client-server communication works by the log records.

```bash
cd /tmp/enki
pipenv install
pipenv shell
cd /tmp/thegame
export PYTHONPATH=${PYTHONPATH}:/tmp/thegame:/tmp/enki
export GAME_ACCOUNT_NAME=1 \
    GAME_PASSWORD=1
LOG_LEVEL=DEBUG python main.py
```

See full example [here](examples/console-kbe-demo-client).

<a name="clientapp_threads"><h3>ClientApp threads</h3></a>

<details>

<summary>Logic for implementing networking</summary>

The logic at the code level is divided into two abstract layers

* 1) network (network interaction with the server, serialization, addresses and ports, etc.)
* 2) gaming (game entities, redner, UI, game logic)

Under each layer there is an interface. Between the game and the server there are ~30 main events in both directions. From these events, game actions are already unfolding (calling entity methods, updating properties, system messages, for example, the result of a login). Under each event in the interface there is a method and a callback for this method. Each layer is a singleton.

The principle is as follows: a link to another layer is taken in its layer. A method (not starting with "on_") is called on another layer, a method with the same name but prefixed with "on_" is called on another layer. Another layer can be in another thread, process or computer - this is already a matter of implementation.

This implementation of layers uses streams. We call the method with arguments in our thread, the callback with the same arguments will be called in another thread. Network code is asynchronous on asyncio. Interaction between threads is carried out from the network layer to the game layer through the queue, from the game layer to the network layer - through the asyncio api for scheduling coroutines from another thread.

Each layer is launched in a separate thread: the game thread is the main synchronous thread, the network thread with asyncio loop is asynchronous - the child one. The elements of the queue (from the network thread to the game thread) are a reference to the game layer method ("on_" method) and arguments for this method. From the game thread to the network thread via asyncio, a coroutine initialized with the necessary arguments is added to the scheduler. The coroutine in this case is the "on_" method of the network layer. The coroutine will be called in the network thread.

Synchronization of the game thread with the network thread is carried out only by directly calling the `clientapp.sync_layers` procedure. This procedure will subtract elements from the queue and call callbacks in the game thread contained in these elements.

#### Game Loop

Synchronization of the game and network layers is forced by calling `clientapp.sync_layers`. Synchronization is carried out for the amount of time passed. At this moment, the client-server game logic comes to life: network communication with the server begins, the state of game entities is updated, their public client methods will be called. Execution falls into entities, remote server methods will also be called from the client. When `clientapp.sync_layers` gives up, client sync is suspended. At this moment, you can draw the screen, read the keyboard input, do something not related to game entities and network interaction. At this time, sending to the event server is possible (if the GIL goes into a network thread for some reason), but receiving events is only possible when calling `clientapp.sync_layers`.

#### Python multi-thread specifics

Due to the nature of multithreading in Python, you need to take into account that a network thread will only be executed when it is given a GIL. If the game thread (and it is the main one) does not encounter blocking calls, then the network thread may not receive the GIL for a very long time and, accordingly, will not be executed. Accordingly, network synchronization stops completely until the network stream has a GIL. To speed up the GIL capture by a network thread, the game thread, when reading messages from the queue in `clientapp.sync_layers`, will have small thread stops after time.sleep to "revive" network communication.

If there are messages queued in the game thread, we read them in a "tick" of time. At this point, methods are called and properties of client entities are updated. Client entity methods, in turn, can call remote methods on the server and thus queue messages for dispatch (in this case, the dispatch queue executes the asyncio scheduler, accepting coroutines to call them in a network thread). But in order for the messages to be sent, the GIL must be passed to the network thread, and they must be sent before control returns from the `clientapp.sync_layers` procedure. Therefore, in `clientapp.sync_layers`, first execution is given to the network thread to read tcp packets from the server and create events for the game thread from them and send scheduled events to the server. Then the GIL returns to the game thread (according to the uncontrolled logic of the Python interpreter), events from the server are read in the game thread (and thus new events for the server are generated) and then execution is again given to the network thread to send new messages and receive responses.

Checking elements in the queue is made blocking with a timeout. Otherwise, you can get a deadlock. If there are no elements in the queue, and the call is not blocking, then the game thread may not give the GIL to the network thread for a long time. A network thread without GIL does not read tcp packets and does not create elements for the queue. With a blocking check, if the queue is empty, it will block and pass the GIL to the network thread, which in turn will fill the queue.

</details>
<br/>

<a name="tests"><h2>Tests</h2></a

There is unit and integration tests. Integration tests require a running KBEngine v2.5.12 server. The Loginapp address must be "0.0.0.0:20013".
