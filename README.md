# Enki (The python network plugin library for connecting with KBEngine)

## Install dependencies

```bash
REPOS_DIR=<YOUR_REPOS_DIR>
cd $REPOS_DIR
git clone git@github.com:ve-i-uj/enki.git
cd enki
sudo pip install pipenv
pipenv install
```

To start the application it needs the started kbengine and the path to the assets.

## Start the KBEngine server

```bash
cd $REPOS_DIR
git clone https://github.com/ve-i-uj/shedu
cd shedu
./configure
cp configs/kbe-v2.5.12-demo.env .env
make build && make start && make logs
```

## Start the example application

Start the console example client to see by logs the client-server communication works.

```bash
cd $REPOS_DIR/enki
bash scripts/start_app.sh
```
