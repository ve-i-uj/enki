# Ninmah (the code generator for the python kbengine client plugin)

## Install the enki project

```bash
REPOS_DIR=<YOUR_REPOS_DIR>
cd $REPOS_DIR
git clone git@github.com:ve-i-uj/enki.git
cd enki
sudo pip install pipenv
pipenv install
```

## Start the code generator

To start the code generator set the environment variables described below.

```bash
# Set necessary data
export LOGIN_APP_HOST=localhost \
    LOGIN_APP_PORT=20013 \
    ASSETS_PATH=<the absolute path to your assest> \
    ACCOUNT_NAME=<YOUR ACCOUNT NAME> \
    PASSWORD=12345 \
    DST_DIR=/tmp/descr \
    LOG_LEVEL=DEBUG

# Start the python virtual environment (you are in the enki project root directory)
pipenv shell

# Generate code based on the server assets
PYTHONPATH=. python tools/ninmah
```