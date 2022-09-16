#!/usr/bin/bash
#

USAGE="
Usage. The scripts generate the python code for kbe client to the /tmp directory.

Example:
pipenv shell
bash $0 <path to the assets dir>
"

curr_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $( realpath "$curr_dir/../scripts/init.sh" )

cd "$PROJECT_DIR"

if [ -z "$VIRTUAL_ENV" ]; then
    echo "[ERROR] Activate the python virtual environment at first! (pipenv shell)"
    echo -e "$USAGE"
    exit 1
fi

assets_path="$1"
if [ -z "$assets_path" ]; then
    echo "[ERROR] There is no assets directory in the first argument"
    echo -e "$USAGE"
    exit 1
fi

if [ ! -d "$assets_path" ]; then
    echo "[ERROR] There is no assets directory \"$assets_path\""
    echo -e "$USAGE"
    exit 1
fi

export LOGIN_APP_HOST=localhost \
    LOGIN_APP_PORT=20013 \
    ASSETS_PATH="$assets_path" \
    ACCOUNT_NAME=112 \
    PASSWORD=112 \
    DST_DIR=/tmp/descr \
    LOG_LEVEL=INFO

# Generate code based on the server assets
PYTHONPATH=. python tools/ninmah