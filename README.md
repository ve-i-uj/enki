# Enki (a Python library for networking with KBEngine components)

## Overview

Enki is a Python library for networking with KBEngine components.

The library contains classes for processing, receiving, sending messages between any KBEngine components (both server and client). Implemented classes of low-level clients (UDP, TCP) that send, receive, serialize, deserialize messages of [KBEngine](https://github.com/kbengine/kbengine "Open source MMOG server engine"), both via an open TCP channel, and open a callback server (UDP, TCP) to receive a response from another cluster component.

There are several implemented tools based on the library in the project.

## Table of contents

[Installation](#instalation)

[The component "Supervisor"](#supervisor)

[Message Reader](#msgreader)

[Healthcheck scripts](#healthcheck)

[The script "modify_kbe_config"](#modify_kbe_config)

[Assets normalization](#normalize_entitiesxml)

[ClientApp](#clientapp)

[ClientApp threads](#clientapp_threads)

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
(enki) leto@leto-PC:~/2PeopleCompany/REPOS/enki$ python tools/msgreader.py machine 01002300e80300006b62656e67696e650006000000591b0000000000000a000000ac180009510b
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

```console
(enki) leto@leto-PC:~/2PeopleCompany/REPOS/enki$ python tools/msgreader.py machine e80300006b62656e67696e65000a000000d107000000000000591b000000000000ffffffffffffffffffffffffac180004ec35ac1800049dad0007000000000000000000000000f031010000000000000000000000000000000000000000000000000000000000d084000000000000ac1800044f82 --bare-msg "Machine::onBroadcastInterface"
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

As you can see from the response, the Machine component sends the data of the Logger component to the callback address.

Implemented analysis of 10 messages, a list of which can be viewed [here](enki/handler/serverhandler/__init__.py)

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
make build_game && make start_game
```

You now have a running KBEngine cluster. Generate the plug-in code and start the console game.

```bash
cd /tmp
git clone git@github.com:ve-i-uj/enki.git
git clone https://github.com/kbengine/kbengine_demos_assets.git
mkdir thegame
cd enki
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

Now there is a generated plugin in the directory "/tmp/thegame/descr". Based on the parent entity classes from the generated planig, you can write game logic. An example of game logic can be found [here](examples/console-kbe-demo-client/entities).  I'll just copy the base entity implementations and entry point module from the project.

```bash
cp -R /tmp/enki/examples/console-kbe-demo-client/entities/ entities
cp -R /tmp/enki/examples/console-kbe-demo-client/main.py main.py
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
pipenv shell
cd /tmp/thegame
export PYTHONPATH=${PYTHONPATH}:/tmp/thegame
export GAME_ACCOUNT_NAME=1 \
    GAME_PASSWORD=1
LOG_LEVEL=DEBUG python main.py
```

See full example [here](examples/console-kbe-demo-client).

<a name="clientapp_threads"><h3>ClientApp threads</h3></a>

<details>

<summary>Логика реализации сетевого взаимодействия</summary>

Логика на уровне кода разделена на два абстрактных слоя

* 1) сетевой (сетевое взаимодействие с сервером, сереиализация, адреса и порты и т.п.)
* 2) игровой (игровые сущности, реднер, UI, игровая логика)

Под каждый слой есть интерфейс. Между игрой и сервером есть ~30 основных событий в обе стороны. Из этих событий разворачиваются уже игровые действия (вызов методов сущностей, обновление свойств, системные сообщения, например, результат логина). Под каждое событие в интерфейсе есть метод и колбэк для этого метода. Каждый слой - это сиглтон.

Принцип следующий: в своём слое берётся ссылка на другой слой. У другого слоя вызывается метод (не начинающийся на "on_"), метод с тем же названием, но с приставкой "on_" вызывается в другом слое. Другой слой может находиться в другом потоке, процессе или компьютере - это уже вопрос реализации.

В данной реализации слоёв используются потоки. Вызываем метод с аргументами в своём трэде, колбэк с этими же аргументами вызовется уже в другом трэде. Сетевой код асинхронный на asyncio. Взаимодействие между трэдами осуществляется из сетевого слоя в игровой через очередь, из игрового слоя в сетевой - через api asyncio для планирования корутин из другого трэда.

Каждый слой запущен в отдельном трэде: игровой трэд - главный синхронный трэд, сетевой с asyncio loop асинхронный - дочерний. Элементами очереди (из сетевого трэда в игровой) являются ссылка на метод игрового слоя ("on_" метод) и аргументы для этого метода. Из игрового трэда в сетевой через asyncio в планировщик добавляется инициализированная нужными агрументами корутина. Корутиной в данном случае является "on_" метод сетевого слоя. Корутина будет вызывана в сетевом трэде.

Синхронизация игрового трэда с сетевым осуществляется только при непосредственном вызове процедуры `clientapp.sync_layers`. B этой процедуре будет происходить вычитывание из очереди элементов и вызов колбэков в игровом трэде, содержащихся в этих элементах.

#### Игровой цикл

Синхронизация игрового и сетевого слоя происходит принудительно вызовом `clientapp.sync_layers`. Синхронизация осуществляется переданное кол-во времени В этот момент клиент-серверная игровая логика оживает: начинается сетевая коммуникация с сервером, обновляется состояние игровых сущностей, будут вызываться их публичные клиентские методы. Исполнение попадает в сущности, с клиента так же будут вызываться удалённые серверные методы. Когда `clientapp.sync_layers` отдаёт управление, синхроннизация клиента приостанавливается. В этот момент можно отрисовывать экран, считать ввод клавиатуры, делать что-то не связанное с игровыми сущностями и сетевым взаимодействием. В это время отправка на сервер событий возможна (если GIL по какой-то причине уйдёт в сетевой трэд), но получение событий возможно только при вызоыве `clientapp.sync_layers`.

#### Многотрэдовая специфика Python

Из-за специфики многопоточности в Python, нужно учитывать, что сетевой трэд будет исполнятся только когда ему отдадут GIL. Если игровой трэд (а он главный) не встретит блокирующих вызовов, то сетевой трэд может очень долго не получать GIL и соответственно не выполняться. Соответсвенно, сетевая синхронизация полностью останавливается, пока у сетевого потока нет GIL. Чтобы ускорить захват GIL сетевым трэдом, в игровом трэде при чтении сообщений из очереди в `clientapp.sync_layers` будут происходить небольшие остановки трэда через time.sleep, чтобы "оживлять" сетевую коммуникацию.

Если есть сообщения в очереди в игровом трэде, мы их читаем "тик" времени. В этот момент вызываются методы и обновляются свойства клиентских сущностей. Методы клиентских сущностей в свою очередь могут  вызывать удалённые методы на сервере и таким образом помещать сообщения в очередь для отправки (в данном случает очередь для отправки выполняет планировщик asyncio, принимая корутины для вызова их в сетевом трэде). Но чтобы сообщения отправились, нужно передать GIL сетевому трэду, и отправить их нужно ещё до возврата управления из процедуры `clientapp.sync_layers`. Поэтому в `clientapp.sync_layers` сперва исполнение отдаётся сетевому трэду на чтение tcp пакетов от сервера и создания из них событий для игрового трэда и отправку запланированных событий серверу. Дальше GIL возвращается в игровой трэд (по неконтролируемой логике интерпритатора Python), в игровом трэде читаются события от сервера (и таким образом генерируются новые события для сервера) и затем исполнение снова время отдаётся сетевому трэду, чтобы от отправил новые сообщения и принял ответы.

Проверка элементов в очереди сделана блокирующей с таймаутом. В обратном случае можно полуить дэдлок. Если нет элементов в очереди, а вызов не блокирующий, то игровой трэд может долго не отдавать GIL сетевому трэду. А сетевой трэд без GIL не читает tcp пакеты и не создаёт элементы для очереди. При блокирующей проверке, при пустой очереди будет блокировка и передача GIL сетевому трэду, который в свою очередь наполнит очередь.

</details>
<br/>
