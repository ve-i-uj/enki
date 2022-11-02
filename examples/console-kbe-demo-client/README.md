### The console client of the KBEngine game server

This example just illustrates the client-server communication works.

Start the KBEngine server.

```bash
git clone https://github.com/ve-i-uj/shedu
cd shedu
./configure
cp configs/kbe-v2.5.12-demo.env .env
make build && make start && make logs
```

And then generate the python code for kbe client.

```bash
cd <ENKI PROJECT>
pipenv shell
LOG_LEVEL=DEBUG bash scripts/gen_ents_to.sh --assets-dir=../KBEngine/kbengine_demos_assets --dst-dir="$HOME/2PeopleCompany/REPOS/enki/example/console-kbe-demo-client/descr" --force
```

The "entities" package contains implementation of the kbe entities.

Start the console client to see by logs the client-server communications works.

```bash
bash scripts/start_app.sh
```
