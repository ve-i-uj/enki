# Enki (библиотека Python сетевого взаимодействия с компонентами KBEngine)

## Обзор

Enki — это библиотека Python реализующая базовый функционал для сетевого взаимодействия с компонентами [KBEngine](https://github.com/kbengine/kbengine "Open source MMOG server engine").

Библиотека содержит классы для обработки, получения, отправки сообщений между любыми компонентами KBEngine (как серверными, так и клиентскими). Реализованы классы низкоуровневых клиентов (UDP, TCP), которые отправляют, получают, сериализуют, десериализуют сообщения [KBEngine](https://github.com/kbengine/kbengine "Серверный игровой движок с открытым исходным кодом"), как через открытый TCP-канал, так и через сетевые UDP, TCP колбэки для получения ответа от другого компонента кластера (когда в сообщении передаётся порт ожидания ответа и на нём ожидается ответ).

Изначально я создавал проект, как клиентский плагин под KBEngine на Python. Но в процессе развития проект разросся и я его разделил на библиотеку и инструменты для разработки под KBEngine на основе этой библиотеки. Список того, что реализовано приведён ниже.

## Table of contents

[Установка](#instalation)

[Серверный компонент "Supervisor"](#supervisor)

[Декодировщих сообщений "Message Reader"](#msgreader)

[Скрипты для проверки здоровья серверных компонентов](#healthcheck)

[Генератор кода серверных игровых сущностей "Assets API Code Generator"](#assetsapi)

[Скрипт для быстрой модификаци конфига "modify_kbe_config"](#modify_kbe_config)

[Скрипт для нормализации конфига при запуске в Docker "Assets normalization"](#normalize_entitiesxml)

[Клиентский плагин "ClientApp"](#clientapp)

<a name="instalation"><h2>Установка</h2></a>

```bash
REPOS_DIR=<YOUR_REPOS_DIR>
cd $REPOS_DIR
git clone git@github.com:ve-i-uj/enki.git
cd enki
sudo pip install pipenv
pipenv install
pipenv shell
```

<a name="supervisor"><h2>Серверный компонент "Supervisor"</h2></a>

При запуске каждого серверного компонента архитектуры KBEngine в отдельном контейнере `Docker` я столкнулся с проблемой, что компонент `Machine` `KBEngine` регистрирует другие компоненты только в том случае, если они расположены на том же хосте, что и Machine. А при запуске каждого компонента в отдельном Docker-контейнере кластер не работал, т.к. Machine не регистрировала компоненты и они не могли найти друг друга при запуске.

Чтобы решить эту проблему, я переписал компонент `Machine`, повторяющий Machine API, чтобы кластер `KBEngine` можно было развернуть в `Docker`. Я назвал компонент Supervisor. [Supervisor](enki/app/supervisor) написан на основе данной Python библиотеки «Enki».

<a name="msgreader"><h2>Декодировщих сообщений "Message Reader"</h2></a>

Консольная утилита для просмотра сообщений между компонентами KBEngine.

<details>
<summary>В кратце про сообщения</summary>

Взаимодействие между компонентами движка KBEngine происходит на основе сообщений. Сообщение состоит из 1) заголовок в виде id сообщения и (иногда) его длины, 2) и тела сообщения. Плюс оптимизации в зависимости от настроек и содержания данных. Само сообщение - это массив байт. Спецификация сообщения описывает последовательность типов данных в теле сообщния для их сериализации / десериализации. Сообщения могут передаваться по TCP или UDP. Взаимодействие может происходить, как с постоянными открытыми для прослушки портами, так и портами, которые открываются на прослушку под колбэк на конкретное сообщение. Так же сообщение может не иметь ни id, ни длины, т.к. в некоторых случаях предполагается, что придёт конкретное сообщение (типа оптимизация для тех же колбэк-портов).

</details>
<br/>

И так. Сообщение - это просто массив байт и чтобы его можно было быстро просматривать в человеко-читаемой форме, я написал этот инструмент.

Для удобного просмотра сообщений перемещающихся между компонентами игрового движка я написал [скрипт](tools/msgreader.py), который можно использовать для анализа сетевого трафика между компонентами KBEngine. С помощью этого скрипта можно анализировать как сообщения `KBEngine` с заголовком (когда его id и длина передаются в заголовке сообщения), так и голые сообщения на callback-адрес (голые сообщения не имеют id сообщения и длины и отправляются на определенный порт, открытый компонентом).

Для захвата трафика используется WireShark или tcpdump. Далее необходимо выбрать пакет между серверными компонентами KBEngine и скопировать данные пакета в шестнадцатеричном виде.

![msgreader_example](https://github.com/ve-i-uj/enki/assets/6612371/2da966da-f9d1-4cd3-8ced-546124286064)

Чтобы утилита `msgreader` работала на Python, необходимо активировать виртуальную среду Python. Виртуальное окружение - это интерпритатор питона с локально установленными библиотеками под конкретный проект. Вам нужно [активировать виртуальное окружение](#instalation) один раз, а затем использовать скрипт.

Сценарий должен получить компонент назначения сообщения и двоичные данные, скопированные в шестнадцатеричной форме из WireShark. Скрипт десериализует данные и выводит их в консоль в удобном для чтения формате. Поля с двойным подчеркиванием добавлены самим скриптом для удобства чтения, т.е. поля с двойным подчёркиванием в сообщении не отправлялись. Например, поля «addr» и «finderRecvPort» в сообщении закодированы. Обработчик этого сообщения добавляет к результату поле `__callback_address`, в котором адрес уже в понятной и привычной форме.

В этом случае запрос отправляется компоненту Machine. Вывод скрипта показывает, что компонент Baseapp запрашивает адрес компонента Logger и просит отправить ответ на адрес 172.24.0.9:20747.

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

Данные распечатанные скриптом значительно понятнее, чем `01002300e80300006b62656e67696e650006000000591b0000000000000a000000ac180009510b`.

Это был пример с сообщением, которое имеет заголовок. Теперь рассмотрим пример дисериализации сообщения без заголовка. В трафике, захваченном WireShark, находим ответ на сообщение "Machine::onFindInterfaceAddr", т.к. адрес ответа теперь известен - 172.24.0.9:20747 (известен из сообщения "Machine::onFindInterfaceAddr").

![callback_response](https://github.com/ve-i-uj/enki/assets/6612371/2436b950-b046-49a6-b31a-1c11c3409099)

Получатель сообщения KBEngine знает, какое сообщение будет отправлено в ответ и что ответ будет отправлен без заголовка (т.е. без идентификатора сообщения и его длины). В этом случае, чтобы десериализовать сообщение, скрипту нужно сообщить id сообщение через аргумента командой строки `--bare-msg` (--bare-msg "Machine::onBroadcastInterface"). Аргумент должен идти после шеснадцатиричных данных.

<details>

<summary>Пример чтения сообщения "Machine::onBroadcastInterface"</summary>

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

Как видно из ответа, компонент Machine отправил компоненту Baseapp адреса компонента Logger (Machine регистрирует все ключевые компоненты).

Список реализованных обработчиков для сообщения можно посмотреть [здесь](enki/handler/serverhandler/__init__.py). Утилита для чтения сообщений работает только для KBEngine v2.

<a name="healthcheck"><h2>Скрипты для проверки здоровья серверных компонентов</h2></a>

Я написал [скрипты для проверки работоспособности](tools/cmd) кластера KBEngine на основе моей библиотеки Python "Enki". Сценарии основаны на классах команд, которые инкапсулируют сетевое подключение к серверному компоненту, сериализацию данных и получение ответа. Команды (как и библиотека Enki) написаны в асинхронном стиле Python.

Скрипты используются в [моем проекте по развертыванию кластера KBEngine в Docker](https://github.com/ve-i-uj/shedu).

<details>

<summary>Пример использования healthcheck скрипта</summary>

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


<a name="assetsapi"><h2>Генератор кода серверных игровых сущностей "Assets API Code Generator"</h2></a>

Инструмент генерирует родительские классы серверных сущностей полностью отражающих интерфейс из `*.def` файлов. Это ускоряет разработку за счёт помощи анализаторов кода, таких например, как Pylance (анализатор кода по умолчанию в VSCode). В сгенерированном коде есть ссылки на def файлы сущностей, их удалённые методы и типы, что облегчает навигацию по коду.

Сгенерирвоанные классы сущностей без ошибок парсятся [Enterprise Architect](https://sparxsystems.com) - это даёт возмность импортировать сгенерированне классы в `Enterprise Architect` и строить диаграммы для визуального описания клиент-серверной логику (например, через диаграмму последовательности, т.к. сгенериваронные сущности сразу содержат удалённые методы).

Например, конкретно для сущности Avatar будет сгененирован его полный API: методы, свойства, удалённые вызовы на другие компоненты, типы параметров, определённые в файлах `entity_defs/Avatar.def` и `types.xml` (включая типы, которые возвращают конвертеры, подключенные к FIXED_DICT).

Данный инструмент является генератором кода интерфейсов для сущностей, определённых в `entity_defs`. Достаточно создать xml файлы игровых сущностей и затем запустить генератор родительских классов. Будет сгенерированы интерфейсы, у которых есть все методы и свойства определённые в `entity_defs`. Эти родительские классы при наследовании дадут возможность IDE указывать на ошибки в использовании методов ещё до запуска игры и подсказывать интерфейс удалённых методов сущности (и таким образом позволяет сэкономить время разработки). Так же генерируются все типы из `types.xml` для подсказок типов удалённых вызовов.

![Peek 2023-08-15 17-01](https://github.com/ve-i-uj/enki/assets/6612371/ff762b3a-fad8-44fb-943c-3070a3cc01cb)

Примеры (используется код `kbengine_demos_assets`):

<br/>
<details>
<summary>Подсказка сигнатуры удалённого метода сущности, на основе  Account.def</summary>

![image](https://github.com/ve-i-uj/enki/assets/6612371/b37b48b7-2adb-4ebd-9fe9-ef15128de87f)

<br/>

![image](https://github.com/ve-i-uj/enki/assets/6612371/6ff83663-1c3a-4d12-9115-7596b8c0273f)

</details>

<br/>
<details>
<summary>Подсказка свойства сущности, на основе Account.def</summary>

IDE по сгенерированному интерфейсу `IBaseAccount` подсказывает имя свойства и его тип
<br/>

![image](https://github.com/ve-i-uj/enki/assets/6612371/e4a03b64-a0d3-4953-ab56-3b16b84effc0)

Определение типа свойства `Account.characters` (`AvatarInfosList`)
<br/>

![image](https://github.com/ve-i-uj/enki/assets/6612371/647a3941-bede-424b-b210-a07fcd0240fb)

В данном случае тип свойства - это тип, возвращаемый конвертером (`TAvatarInfosList`)

![image](https://github.com/ve-i-uj/enki/assets/6612371/bfaefc4d-07e9-41ad-878b-257785fad093)

Тип свойста `Account.characters` - это `AVATAR_INFOS_LIST`. B types.xml прописано, то `AVATAR_INFOS_LIST` - это FIXED_DICT, с подключенным конвертером `AVATAR_INFOS.AVATAR_INFOS_LIST_PICKLER`

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

Генератор кода понимает, что к FIXED_DICT подключен конвертер. Но для того, чтобы генератор понял, какой тип возвращает конвертер, нужно добавить аннотацию типа методу `AVATAR_INFOS_LIST_PICKLER.createObjFromDict`

</details>

<br/>
<details>
<summary>Подключение API к интерфейсу</summary>

![image](https://github.com/ve-i-uj/enki/assets/6612371/b368a4c1-12e3-4844-ad6e-ed7f8250e48f)

API для интерфейсов сущностей (`scripts/cell/interfaces`) генерируется в пакете `assetsapi.interfaces`. Под каждый интерфейс будет отдельный модуль, в этом модуле будут классы API для наследования. Родительские классы API для интерфейсов сущностей (`scripts/cell/interfaces`) уже наследуют API сущности (`KBEngine.Entity`), поэтому подсказки API сущности будут сразу присутствовать.

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

Смотри так же [пример на основе Demo](https://github.com/ve-i-uj/modern_kbengine_demos_assets), где все сущности, интерфейсы, компоненты имеею подключенные интерфейсы / API.

### Настройка VSCode

Ниже приведён пример файла настроек рабочего пространства для VSCode для работы с assets папки KBEngine, содержащей игровые скрипты и конфигурационные файлы. Последовательность сохранения файла в VSCode: "Open Folder" --> "Sava Workspace As" -->  Copy the config content to the workspace file --> Replace the line "/tmp/kbengine_demos_assets" everywhere in the config with the path to your assets. Конфиг ниже сохранён в папку `assets/.vscode`

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

### Зависимости

Для работы сгенерированного API нужна библиотеку Python `typing-extensions`, подключенная к assets. Когда движок будет запуск серверные скрипты на Python, эта библиотека должна быть.

Здесь есть два решения: 1) [быстрое] просто скопировать библиотеку из данного проекта (совместимость не гарантируется). Скопировать можно в ручную или при генерации API добавить переменную окружения `ADD_TYPING_EXTENSIONS_LIB=true`.

В ручную:

```bash
cd enki
cp tools/assetsapi/forcopy/typing_extensions.py /tmp/kbengine_demos_assets/scripts/common/
```

Или второе решение 2) [долгое] установить библиотеку через pip для Python такой же версии, как и KBEngine и под OS, на которой запущен сервер KBEngine (нужен установленный Docker). Инструкция приведена [здесь](https://github.com/ve-i-uj/modern_kbengine_demos_assets/).

### Генерация API серверных сущностей и типов

Для генерации серверных сущностей изначально нужно сгенерировать API движка. Необходимо указать путь до папки assets. Код будет сгенерирован в папку server_common. Обратите внимание, что в данном случае ещё добавляется переменная окружения `ADD_TYPING_EXTENSIONS_LIB=true`. Если библиотеку `typing_extensions.py` была добавлена через сборку Python и pip, как описано выше, то просто уберите эту переменную.

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

Теперь есть код API движка, в папке `server_common` должен появиться пакет `assetsapi`. Чтобы корректно работал анализатор кода Pylance, а так же корректно запускался код движком, необходимо библиотеки движка импортировать из сгенерированного пакета `assetsapi`. Во время импорта код в `assetsapi` сам определяет, от куда импортировать модули движка: из самого движка или нужно только подключить API. Далее, чтобы сгенерировать методы и свойства для каждой конкретной сущности нужно поменять в модулях конвертеров (`scripts/user_type`) `import KBEngine` (если такой импорт имеется, как в случае с demo) на импорт такого вида:

```python
from assetsapi.kbeapi.baseapp import KBEngine
```

Это нужно, т.к генератор кода во время генерации кода читает модули, содержащие конвертеры (папка `scripts/user_type`) и генерерует методы сущности сразу с параметрами типов, которые возвращают конвертеры (если конвертеры аннотированы типами).

В случае `kbengine_demos_assets` достаточно просто удалить `import KBEngine` в модуле `AVATAR_INFOS.py` и модуле `AVATAR_DATA.py` (т.к. он не используется). B модуле `KBEDebug.py` нужно заменить `import KBEngine` на `from assetsapi.kbeapi.baseapp import KBEngine`.

После этого нужно запустить

```bash
GAME_ASSETS_DIR=/tmp/kbengine_demos_assets python tools/assetsapi/main.py
```

API для сущностей должен быть сгенерирован. Теперь надо его подключить.

<details>
<summary>NB (импорт модуля KBEngine для cellapp и baseapp)</summary>

Импорт для baseapp и cellapp отличаются называнием последнего модуля

```python
# For `base` entity component
from assetsapi.kbeapi.baseapp import KBEngine
# For `cell` entity component
from assetsapi.kbeapi.cellapp import KBEngine
```

но для таких папок как `scripts/user_type`, `common/user_type` или `server_common/user_type` можно использовать любой из этих импортов. Т.к. часть API модуля `KBEngine` общая для обоих компонентов, а в рантейме под капотом пакета `assetsapi` модуль `KBEngine` будет импортирован из движка через `import KBEngine` (т.е. сразу для нужного компонента).

</details>
<br/>

### Подключение API к сущностям

Для каждой сущности будет сгенерирован свой API, который располагается в папке `scripts/server_common/assetsapi/entity`. Например, для сущности `Avatar` API будет располагаться в `scripts/server_common/assetsapi/entity/avatar.py`. API - это интерфейс, который нужно унаследовать, как первый родительский класс.

![Generated_API](https://github.com/ve-i-uj/enki/assets/6612371/6836666d-06e5-4427-9d49-63d6afa08157)

В примере видно, что 1) сохранены настройки рабочего пространства для VSCode, чтобы работала навигация по коду ("Save Workspace As ..." и затем скопировать в файл пример настроек выше), 2) добавили библиотеку "typing_extensions.py" в соответствии с инструкциями выше. 3) Сгенерировали код интерфейсов сущности. 4) Модифицируем файл `scripts/base/Avatar.py`: нужно удалить `import KBEngine` и вместо него импортировать `KBEngine` из пакета `scripts/server_common/assetsapi` (пункт 5). 6) Далее унаследовали первым родительским классом IBaseAvatar, импортированный из модуля `assetsapi.entity.avatar` (пункт 5). 7) При наборе кода Pylance подсказывает какие есть атрибуты у экземпляра, какие удалённые методы и так же сигнатуры удалённого метода (пункт 8). В VSCode (+ Pylance) oтображаются методы, свойства сущностей из конфигурационных файлов (`scripts/entity_defs`), API взаимодействия с KBEngine из Python. Pylance так же добавляет проверку типов к используемым методам.

Обратите внимание, что KBEngine.Proxy наследуется последним (как и `KBEngine.Entity` в других модулях). Это нужно, чтобы нормально обработалось множественное наследование. Иначе можно получить ошибку на невозможность осуществить MRO. Классы сущностей могут наследовать интерфейсы из `scripts/entity_defs/interfaces`. Под интерфейсы тоже генерируются родительские классы с API. Чтобы работало автодополнение в модулях для `scripts/entity_defs/interfaces` родительские классы с API тоже наследуют интерфейс сущности из KBEngine (т.е. наследуют `KBEngine.Entity`) и может получиться конфликт при множественном наследовании.

### Импорт модулей из движка (KBEngine и Math)

Модули движка нужно импортировать из пакета `scripts/server_common/assetsapi`

```python

from assetsapi.kbeapi.baseapp import KBEngine
from assetsapi.kbeapi.Math import Vector3

```

### Генерация типов по types.xml

Данный инструмент так же генерирует типы данных, которые используются в удалённых методах сущностей. Типы данных генерируются на основе типов `types.xml`. Сгенерированные типы используются в описании сигнатур методов, особенно это актуально при использовании FIXED_DICT в качестве параметра. Сгенерированные типы находятся в модуле `scripts/server_common/assetsapi/typesxml.py`, их можно импортировать из этого модуля и использовать в методах сущностей.

<br/>
<details>
<summary>Пример использования сгенерированного типа</summary>

![image](https://github.com/ve-i-uj/enki/assets/6612371/8ed805d5-a47b-4112-a7df-16fec136adc5)
<br/>
<br/>
<br/>
![image](https://github.com/ve-i-uj/enki/assets/6612371/2dc4fa68-244b-4821-b259-daba38908513)

</details>

Если к FIXED_DICT подключен конвертер и у конвертера аннотироны типы метода, то в сгенерированных методах будет сразу использован тип, возвращаемый конвертером.

<br/>
<details>
<summary>Пример добавления типа, возвращаемого конвертером</summary>

Добавляем аннотоции возвращаемого типа (файл `scripts/user_type/AVATAR_INFOS.py`)

![FD_with_converter_2](https://github.com/ve-i-uj/enki/assets/6612371/48ff0f05-1a38-44fe-80e7-cc760a61d8a5)

Перегенерируем API и увидим нужный тип в методе

![FD_with_converter_1](https://github.com/ve-i-uj/enki/assets/6612371/7a63345d-a941-4b28-b6b5-1689ac27f418)

</details>
<br/>

Для конвертеров отдельно генерируются FIXED_DICT (в пакет `assetsapi.user_type`). Сгенерированные классы для FIXED_DICT сразу содержат информацию о ключах, которые можно в них использовть. Соответственно Pylance (анализатор кода) может указать, на ситуации, когда в словаре используются неуказанные ключи. Имя FIXED_DICT будет таким же, как и в types.xml, только в CamelCase и с суффиксом "FD".

Если в user_type используются сторонние библиотеки, то их нужно добавить через переменную SITE_PACKAGES_DIR. Это должна быть папка с библиотеками Python.

Пример

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

Ниже приведён пример, в котором у конвертера указан тип FIXED_DICT (`AVATAR_INFOS`), который он получит в конвертер, и затем конвертер вернёт пользовательский тип `TAvatarInfos`. В примере, например, показана попытка добавить ключ, которого нет в описании. Pylance в этом случае указывает на ошибку - это удобно и помагает отловить ошибки ещё на стадии разработки.

<br/>
<details>
<summary>Пример использования сгенерированного типа</summary>

![image](https://github.com/ve-i-uj/enki/assets/6612371/8b4fd257-dc45-4e81-82f0-8d1ea6cc8f22)

</details>
<br/>

### Имена аргументов и документация к методу

Генератор может давать имена аргументам и добавлять в документацию к сгенерированному методу. Для этого при описании удалённого метода сущности нужно добавить xml комментарии следующим образом

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
<summary>Получим сгенерированный код с документацией</summary>

![image](https://github.com/ve-i-uj/enki/assets/6612371/80288528-033c-4989-a664-417609b68a64)
<br/>
![image](https://github.com/ve-i-uj/enki/assets/6612371/ebd71a56-54a8-46fa-a08f-8f0cd95c9dcb)

</details>
<br/>

Формирование имени параметра по комментарию можно отключить, если выставить переменную `USE_DEF_COMMENTS_LIKE_PARAMS=false`. Отключение формирования параметров по комментариям может понадобиться, например, если комментарии уже существуют.

### Диаграмма сгенерированных классов

Диаграмма приведена на основе сущности Avatar. Указанные классы или будут сгенерированы на основе Avatar.def файла (IBaseAvatar) или будут находиться в пакете `assetsapi` (например, KBEngine.Proxy).

![Class diagram of generated classes (12 08 23)](https://github.com/ve-i-uj/enki/assets/6612371/d72ed351-d8fd-4871-b028-66c9b01e1b0e)

Во время запуска кода из движка KBEngine у сгенерированных классов будет пустое тело, поэтому они не будут конфликтовать со свойствами и методами из движка.

### Инструменты для разработки

Вместе с `assetsapi` можно добавить в `server_common` инструменты для разработки. Добавить инструменты можно, добавив переменную окружения `ADD_ASSETSTOOLS=true` при генерации кода. В этом случае будет создана папка `scripts/server_common/assetstools`, в которой будут следующие вспомогательные инструменты.

Описание этих инструментов можно посмотреть [в репозитории обновлённого мной демо серверных скриптов](https://github.com/ve-i-uj/modern_kbengine_demos_assets/).

### Заметки

<details>
<summary>Entity Component API</summary>
<br/>

N.B.: В Demo демонстрируется, что можно создать RemoteCall компонента, обратившись сперва к владельцу (т.е. к сущности), а затем обратиться к свойству сущности (которым является компонент) и вызывать удалённый метод. И это всё осуществляетя из тела класса компонента.

В примере в Демо заложена большая потенциальная ошибка, которая ещё и сбивает с толку при понимании API компонентов. По идее один и тот же класс компонента может использоваться разными сущностями, а имя свойства, которое ссылается на компонент может вариироваться от сущности к сущности. Например, если добавить компонент с типов "Test" сущности `Account`, но добавить его под именем `component123`, то код из демо перестанет работат. Не будет он работать, потому что при вызове метода Test.onAttached для компонента, привязанного к `Account` под именем `component123`, у владельца (Account'а) не будет свойства `component1`. Вывод: проще и очевиднее делать удалённый вызов напрямую из самого тела компонента, не прибегая к сущности.

Плохой пример из Demo:

```python
class Test(KBEngine.EntityComponent):

    def onAttached(self, owner):
        INFO_MSG("Test::onAttached(): owner=%i" % (owner.id))
        self.owner.client.component1.helloCB(111)
```

Тоже самое, но очевиднее:

```python
class Test(KBEngine.EntityComponent):

    def onAttached(self, owner):
        INFO_MSG("Test::onAttached(): owner=%i" % (owner.id))
        self.client.helloCB(111)
```

Однако, если компоненент создаётся под конкретную сущность, то подсказывать API сущности можно таким образом:

![image](https://github.com/ve-i-uj/enki/assets/6612371/27a641c7-c57c-44f3-87eb-e32c7c16072f)

<br/>
Но настоятельно реккомендуется подключать API для компонентов, не привязывая их к конкретной сущности на уровне кода. Отношение компонент - сущность - это отношение один ко многим, а не один ко одному. Пример подключения API, без привязки к конкретной сущности:
<br/>
<br/>

![image](https://github.com/ve-i-uj/enki/assets/6612371/ad6d53e2-5580-4571-b0ac-1e5ca29d0ab9)

</details>
<br/>

<details>
<summary>Чтение конвертеров из user_type </summary>
<br/>

Для чтения конвертеров модули из user_type будут импортированы импортируются. Чтобы дать возможность использовать описания FIXED_DICT для аннотации типов FD в конвертере, генерируются классы на Python по types.xml. Классы содержаться в отдельном пакете `assetsapi.user_type`. Получается, что в модули конвертеров (из `user_type`) импортируют сгенерированные модули в том числе и `assetsapi.user_type`. Но для генерации `assetsapi.user_type` нужно прочитать модули конвертеров - а это в итоге приводит к циклическому импорту. Поэтому перед генерацией кода создаётся модуль-заглушка `assetsapi.user_type`, который содержит все FD с конвертерами, но вида `AvatarInfoFD = Dict` (без описания полей). Этого будет достаточно, чтобы прочитать модули конвертеров из `user_type` и затем уже можно будет сгенерировать полноценный `assetsapi.user_type` и `typesxml.py`.

Нюанс с `assetsapi.user_type`. По сути `assetsapi.user_type` - это слегка изменённая копия `typesxml.py`. Данный пакет дублирует модуль `typesxml.py`, но с тем отличием, что все FIXED_DICT с конвертерами здесь заменены на простые FIXED_DICT (c FD суффиксом в имени). Это сделано, т.к. модуль `typesxml.py` импортирует пользовательский тип из модуля с конвертером (пользовательский тип - это тип, в который конвертер конвертирует FIXED_DICT). Но модуль с пользовательским типом сам использует FIXED_DICT, сгенерированные по `typesxml.py`. Если импортировать сгенерированные типы из `typesxml.py` в модуль конвертера, то опять получим циклический импорт (ошибку). Чтобы обойти это, я генерирую `assetsapi.user_type`, который является слегка изменённый модулем `typesxml.py`. Пакет `assetsapi.user_type` должен использоваться только для импорта в модули директории user_type. Цель `assetsapi.user_type` дать возможность указывать спецификацию FIXED_DICT, который
получает конвертер. Эти сгенерированные типы нужны *только* для указания типов, используемых конвертерами в папке user_type. *В методах сущностей типы из пакета `assetsapi.user_type` использоваться не должны*, для этого есть модуль typesxml.py .

### Нюансы генерации типов по types.xml

Типы коллекций, которые на ходу создают внутри себя другие коллекции не будут детально описаны. Например

```
<ARRAY_OF_ARRAY> ARRAY <of> ARRAY <of> AVATAR_INFO </of> </of> </ARRAY_OF_ARRAY>
```

будет сгенерирован в тип вида `ArrayOfArray = List[Array]` (вложенный тип в данном случае просто массив, а не массив, содержащий AVATAR_INFO). Есил нужно более детальное описание типа, то рекоммендуется использовать алиасы. Например

```
<AVATAR_INFOS> ARRAY <of> AVATAR_INFO </of> </AVATAR_INFOS>
<ARRAY_OF_AVATAR_INFOS> ARRAY <of> AVATAR_INFOS </of> </ARRAY_OF_AVATAR_INFOS>
```

тогда `ARRAY_OF_AVATAR_INFOS` будет сгенерирован в тип вида

```
AvatarInfos = List[AvatarInfo]
ArrayOfAvatarInfos = List[AvatarInfos]
```

В данном случае будут указаны и вложенные типы, что гороздо понятнее и легче для дальнейшего сопровождения. Плюс даёт возможность делать проверки type checker'ам.

Если у конвертера не указан возвращаемый тип, то FIXED_DICT с этим конвертером в сгенерированном коде будет иметь тип `Any`.
</details>

<a name="modify_kbe_config"><h2>Скрипт для быстрой модификаци конфига "modify_kbe_config"</h2></a>

[Скрипт](tools/modify_kbeenginexml.py) изменяет или добавляет настройки в ключевой конфигурационный файл KBEngine kbengine.xml. Основная цель скрипта — изменить настройки KBEngine, чтобы кластер KBEngine можно было развернуть в Docker.

Скрипт принимает либо файл, содержащий вносимые изменения (аргумент "--data-file"), либо строку с изменяемыми настройками (аргумент "--kbengine-xml-args").

Настройки файла должны выглядеть так

    root.dbmgr.shareDB=true
    root.interfaces.host=interfaces

Пример см. [здесь](https://github.com/ve-i-uj/shedu/blob/develop/data/kbenginexml.data).

В случае файла в аргументе "--data-file" каждая новая строка представляет собой изменение, которое будет внесено в файл "kbengine.xml". Если такая настройка есть, то она будет изменена, если такой настройки нет, то она будет добавлена.

В случае аргумента командной строки "--data-file" настройки должны быть разделены точкой с запятой.

Пример: `root.dbmgr.shareDB=true;root.interfaces.host=interfaces`

<a name="normalize_entitiesxml"><h2>Скрипт для нормализации конфига при запуске в Docker "Assets normalization"</h2></a>

У KBEngine запутанная логика проверки Ассетов, также отличается поведение компонентов, работающих на одном хосте и на разных хостах. Были проблемы с kbengine-demo-assets. Почти все сущности имеют GameObject в своих интерфейсах. GameObject не имеет методов "cell" и "base", но имеет свойства "cell" и "base". Из-за этого движок при запуске компонентов в разных контейнерах на базе kbengine-demo-assets выдавал при запуске ошибки, такие как

    ERROR baseapp01 1000 7001 [2023-06-07 05:15:27 522] - Space::createCellEntityInNewSpace: cannot find the cellapp script(Space)!
    S_ERR baseapp01 1000 7001 [2023-06-07 05:15:27 522] - Traceback (most recent call last):
    File "/opt/kbengine/assets/scripts/base/Space.py", line 24, in __init__
    self.spaceUTypeB = self.cellData["spaceUType"]
    S_ERR baseapp01 1000 7001 [2023-06-07 05:15:27 522] - AttributeError: 'Space' object has no attribute 'cellData'
    INFO baseapp01 1000 7001 [2023-06-07 05:15:27 522] - EntityApp::createEntity: new Space 2007

Оказалось, что движок требует, чтобы сущности указывали hasCell в файле entity.xml. Поскольку моей целью было работать со стандартными kbengine-demo-assets от разработчиков, я добавил [скрипт](tools/normalize_entitiesxml), который нормализует файл entity.xml. Скрипт при сборке Docker образа игры анализирует ассеты и модифицирует entity.xml, прописывая `hasCell`, `hasBase` сущностям. Но это привело к тому, что почти все сущности имели компоненты `base` и `cell` (hasBase=true и hasCell=true) из-за GameObject в интерфейсах. Движок стал требовать при запуске реализовывать модули для сущностей, например, base/Monster или cell/Spaces. Потом я добавил в скрипт "normalize_entitiesxml" генерацию пустых модулей к таким сущностям при сборке Docker образа.

<a name="clientapp"><h2>Клиентский плагин "ClientApp"</h2></a>

Полностью реализован на Python официальный [API для клиентских плагинов](https://kbengine.github.io//assets/other/kbengine_api.html#client/Modules/KBEngine.html?id=9) игрового движка KBEngine.

Целью написания этого плагина было понимание протокола клиент-серверного взаимодействия многопользовательского серверного игрового движка KBEngine. Плагин написан на языке Python, так как я хорошо знаю этот язык.

В мире Python очень мало значительных инструментов для разработки игр, таких как даже игровые движки уровня Godot. Есть PyGame, но PyGame — это просто очень минималистичная библиотека для перемещения спрайтов (имхо). Разработка больших игр, а тем более многопользовательских, на PyGame — сизифов труд. Поэтому мало верю в практическое применение этого плагина. Однако ниже будет приведен пример генерации кода и запуска [официальной демо-игры KBEngine](https://github.com/kbengine/kbengine_demos_assets) в консоли, чтобы продемонстрировать, что плагин, несмотря на отсутствие графического интерфейса, работает.

### О генераторе кода и плагине

Классы игровых сущностей используются для описания игровой логики. Взаимодействие с серверными частями игровой сущности осуществляется путем вызова удаленных методов сущности через атрибуты `cell` и `base`.

API-интерфейсы сущностей (классы сущностей, методы, свойства) генерируются генератором кода Python на основе библиотеки «enki» (этот проект). Игровые сущности и сериализаторы/десериализаторы сущностей генерируются генератором кода. Игровые сущности — это API, описывающий логику клиент-серверной игры. Сериализаторы сущностей сериализуют удаленные вызовы из типов Python в байты и передают вызов удалённого метода по сети между клиентом и сервером KBEngine.

Генерация кода сущностей и сериализаторов основана на конфигурационных файлах многопользовательского игрового движка KBengine (файлы types.xml , entity.xml , *.def из папки "assets"), а также генерация кода основана на данных из сообщение «Client::onImportClientMessages», это сообщение запрашивается с запущенного игрового сервера. Поэтому для генерации кода игровых сущностей и плагина на Python нужен путь к папке "assets" и запущенный игровой сервер с описанной в "assets" игрой.

### Пример запуска игры на базе ClientApp на Python

Сначала запустите кластер KBEngine с демонстрационными `assets'ами`. Давайте развернем в Linux кластер KBEngine на докер, используя проект Shedu (мой проект с открытым исходным кодом).

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

Теперь сгенерированный плагин находится в каталоге "/tmp/thegame/descr". На основе родительских классов сущностей из сгенерированного плагина можно написать игровую логику. Пример игровой логики можно найти [здесь](examples/console-kbe-demo-client/entities). Я просто скопирую базовые реализации сущностей и модуль точки входа из проекта.

```bash
cp -R /tmp/enki/examples/console-kbe-demo-client/entities/ /tmp/thegame/entities
cp -R /tmp/enki/examples/console-kbe-demo-client/main.py /tmp/thegame/main.py
```

<details>

<summary>Пример игровой логики сущности Account</summary>

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

<summary>Пример точки входа, где игра подключается к серверу и запрашивает список аватаров аккаунта, выбирает аватар и входит в игру (т.е. пример простой игровой логики)</summary>

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

Запустите пример консольного клиента, чтобы увидеть, как работает связь между клиентом и сервером, по записям журнала.

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

См. полный пример [здесь](examples/console-kbe-demo-client).

### Многопоточность клиента

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
