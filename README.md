# Enki (python network plugin for connecting with KBEngine)

## Install dependencies

```bash
REPOS_DIR=<YOUR_REPOS_DIR>
cd $REPOS_DIR
git clone git@github.com:ve-i-uj/enki.git
cd enki
sudo pip install pipenv
pipenv install
```

## Start the example application

Started kbengine and path to the assets are neened to start the application.

```bash
# Set necessary data
export ASSETS_PATH=<the absolute path to your assest>
export LOGIN_APP_HOST=localhost
export LOGIN_APP_PORT=20013

pipenv shell

# Generate code based on the server assets
bash scripts/generate_code.sh

# Start the example application
LOG_LEVEL=INFO bash scripts/start_app.sh
```
