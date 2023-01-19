### The console client of the KBEngine game server


Start the KBEngine server.

```bash
git clone https://github.com/ve-i-uj/shedu
cd shedu
./configure
cp configs/kbe-v2.5.12-demo.env .env
make build && make start && make logs_console
```

Then generate the python code for kbe client.

```bash
cd <ENKI DIR>
cp configs/example.env .env
make send_hello
make start_console_app
```


```bash
bash scripts/start_app.sh
```
