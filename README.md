# Enki (Python library for networking with KBEngine components)

The library contains classes for processing, receiving, sending messages between any KBEngine components (both server and client). Implemented classes of low-level clients (UDP, TCP) that send, receive, serialize, deserialize messages of [KBEngine](https://github.com/kbengine/kbengine "Open source MMOG server engine"), both via an open TCP channel, and open a callback server (UDP, TCP) to receive a response from another cluster component.

Can be used for

* code generation of plugins for any language on jinja templates (for generation, the assets folder is read and the specification is requested from the server via importClientMessages)
* writing scripts to manipulate the game cluster based on component messages (it is possible to embed in the admin panel in Python)
* writing integration tests for client-server interaction
* as a library for writing network components in Python

Based on the library, the specification of the client-server interaction of the server game engine KBEngine is fully implemented. Implemented both a network interaction protocol and the official [API for client plugins](https://kbengine.github.io//assets/other/kbengine_api.html#client/Modules/KBEngine.html?id=9). A code generator has been written to generate client code based on (xml) client-server interaction specifications (types.xml , entities.xml , *.def files). An example of using the client [see here](examples/console-kbe-demo-client/main.py). See below for an example of code generation.

Based on this library, a new component [Supervisor](enki/app/supervisor/main.py) was written that repeats the API of the Machine component, because The Machine component prevented deploy components in separate Docker containers. An example of deploy a cluster in Docker can be found [here](https://github.com/ve-i-uj/shedu). Also there are [healthcheck scripts](tools/cmd) for the KBEngine components based on this library.

There is [a console utility](tools/msgreader.py) to analyze network traffic between components. Network traffic is captured using [WireShark](https://www.wireshark.org/) and deserialized from bytes into a human-readable message (see [MessageReader examples](#MessageReader)).

## Install dependencies

```bash
REPOS_DIR=<YOUR_REPOS_DIR>
cd $REPOS_DIR
git clone git@github.com:ve-i-uj/enki.git
cd enki
sudo pip install pipenv
pipenv install
```

To start the application it needs the started kbengine.

## Start the KBEngine server

```bash
cd $REPOS_DIR
git clone https://github.com/ve-i-uj/shedu
cd shedu
./configure
cp configs/kbe-v2.5.12-demo.env .env
make build && make start
```

## Start the example application

Start the console example client to see by logs the client-server communication works.

```bash
cd <ENKI DIR>
cp configs/example.env .env
make hello
make start_console_app
```

Other operations

```bash
make help
```

## Логика сетевого взаимодействия

Логика на уровне кода разделена на два абстрактных слоя

* 1) сетевой (сетевое взаимодействие с сервером, сереиализация, адреса и порты и т.п.)
* 2) игровой (игровые сущности, реднер, UI, игровая логика)

Под каждый слой есть интерфейс. Между игрой и сервером есть ~30 основных событий в обе стороны. Из этих событий разворачиваются уже игровые действия (вызов методов сущностей, обновление свойств, системные сообщения, например, результат логина). Под каждое событие в интерфейсе есть метод и колбэк для этого метода. Каждый слой - это сиглтон.

Принцип следующий: в своём слое берётся ссылка на другой слой. У другого слоя вызывается метод (не начинающийся на "on_"), метод с тем же названием, но с приставкой "on_" вызывается в другом слое. Другой слой может находиться в другом потоке, процессе или компьютере - это уже вопрос реализации.

В данной реализации слоёв используются потоки. Вызываем метод с аргументами в своём трэде, колбэк с этими же аргументами вызовется уже в другом трэде. Сетевой код асинхронный на asyncio. Взаимодействие между трэдами осуществляется из сетевого слоя в игровой через очередь, из игрового слоя в сетевой - через api asyncio для планирования корутин из другого трэда.

Каждый слой запущен в отдельном трэде: игровой трэд - главный синхронный трэд, сетевой с asyncio loop асинхронный - дочерний. Элементами очереди (из сетевого трэда в игровой) являются ссылка на метод игрового слоя ("on_" метод) и аргументы для этого метода. Из игрового трэда в сетевой через asyncio в планировщик добавляется инициализированная нужными агрументами корутина. Корутиной в данном случае является "on_" метод сетевого слоя. Корутина будет вызывана в сетевом трэде.

Синхронизация игрового трэда с сетевым осуществляется только при непосредственном вызове процедуры `clientapp.sync_layers`. B этой процедуре будет происходить вычитывание из очереди элементов и вызов колбэков в игровом трэде, содержащихся в этих элементах.

## Игровой цикл

Синхронизация игрового и сетевого слоя происходит принудительно вызовом `clientapp.sync_layers`. Синхронизация осуществляется переданное кол-во времени В этот момент клиент-серверная игровая логика оживает: начинается сетевая коммуникация с сервером, обновляется состояние игровых сущностей, будут вызываться их публичные клиентские методы. Исполнение попадает в сущности, с клиента так же будут вызываться удалённые серверные методы. Когда `clientapp.sync_layers` отдаёт управление, синхроннизация клиента приостанавливается. В этот момент можно отрисовывать экран, считать ввод клавиатуры, делать что-то не связанное с игровыми сущностями и сетевым взаимодействием. В это время отправка на сервер событий возможна (если GIL по какой-то причине уйдёт в сетевой трэд), но получение событий возможно только при вызоыве `clientapp.sync_layers`.

## Многотрэдовая специфика Python

Из-за специфики многопоточности в Python, нужно учитывать, что сетевой трэд будет исполнятся только когда ему отдадут GIL. Если игровой трэд (а он главный) не встретит блокирующих вызовов, то сетевой трэд может очень долго не получать GIL и соответственно не выполняться. Соответсвенно, сетевая синхронизация полностью останавливается, пока у сетевого потока нет GIL. Чтобы ускорить захват GIL сетевым трэдом, в игровом трэде при чтении сообщений из очереди в `clientapp.sync_layers` будут происходить небольшие остановки трэда через time.sleep, чтобы "оживлять" сетевую коммуникацию.

Если есть сообщения в очереди в игровом трэде, мы их читаем "тик" времени. В этот момент вызываются методы и обновляются свойства клиентских сущностей. Методы клиентских сущностей в свою очередь могут  вызывать удалённые методы на сервере и таким образом помещать сообщения в очередь для отправки (в данном случает очередь для отправки выполняет планировщик asyncio, принимая корутины для вызова их в сетевом трэде). Но чтобы сообщения отправились, нужно передать GIL сетевому трэду, и отправить их нужно ещё до возврата управления из процедуры `clientapp.sync_layers`. Поэтому в `clientapp.sync_layers` сперва исполнение отдаётся сетевому трэду на чтение tcp пакетов от сервера и создания из них событий для игрового трэда и отправку запланированных событий серверу. Дальше GIL возвращается в игровой трэд (по неконтролируемой логике интерпритатора Python), в игровом трэде читаются события от сервера (и таким образом генерируются новые события для сервера) и затем исполнение снова время отдаётся сетевому трэду, чтобы от отправил новые сообщения и принял ответы. Такова примерная внутренняя последовательность работы `clientapp.sync_layers`.

Проверка элементов в очереди сделана блокирующей с таймаутом. В обратном случае можно полуить дэдлок. Если нет элементов в очереди, а вызов не блокирующий, то игровой трэд может долго не отдавать GIL сетевому трэду. А сетевой трэд без GIL не читает tcp пакеты и не создаёт элементы для очереди. При блокирующей проверке, при пустой очереди будет блокировка и передача GIL сетевому трэду, который в свою очередь наполнит очередь.

<a name="MessageReader"><h2>MessageReader</h2></a>

There is a script that can be used to analyze network traffic between KBEngine components. Using the script, you can analyze both KBEngine messages in an envelope (when its id and length are passed in the message head), and bare messages to a callback address (bare messages doesn't have a message id and its length and sent to a specific port opened by the component).

WireShark is used to capture traffic. Next, you need to select a package between the KBEngine server components and copy the package data in hexadecimal form.

![msgreader_example](https://github.com/ve-i-uj/enki/assets/6612371/2da966da-f9d1-4cd3-8ced-546124286064)

For the `msgreader` script to work in Python, you need to activate the Python virtual environment. You need to activate it once and then use the script.

<details>

<summary>The example of activating a virtual environment</summary>

```console
leto@leto-PC:~/2PeopleCompany/REPOS/enki$ pipenv shell
Launching subshell in virtual environment...
leto@leto-PC:~/2PeopleCompany/REPOS/enki$  . /home/leto/.local/share/virtualenvs/enki-AEzvoHOr/bin/activate
(enki) leto@leto-PC:~/2PeopleCompany/REPOS/enki$ export PYTHONPATH=.
```

</details>
<br/>

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
