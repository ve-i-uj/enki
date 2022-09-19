#!/usr/bin/bash

USAGE="
Usage. The script generates the python code for kbe client.

If the destination directory exists the script exits. Use the "--force"
argument to remove the existed destination directory at first.

Example:

pipenv shell

bash $0 \\
  --assets-dir=/home/$USER/my-assets \\
  --dst-dir=/home/$USER/thegame/thegame/descr \\
  [--force]
"

curr_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $( realpath "$curr_dir/../scripts/init.sh" )

cd "$PROJECT_DIR"

if [[ -z "${VIRTUAL_ENV-}" ]]; then
    log error "Activate the python virtual environment at first! (pipenv shell)"
    echo -e "$USAGE"
    exit 1
fi

log debug "Parse CLI arguments ..."
assets_dir=""
dst_dir=""
help=false
force=false
for arg in "$@"
do
    key=$( echo "$arg" | cut -f1 -d= )
    value=$( echo "$arg" | cut -f2 -d= )

    case "$key" in
        --assets-dir)               assets_dir=${value} ;;
        --dst-dir)                  dst_dir=${value} ;;
        --force)                    force=true ;;
        --help)                     help=true ;;
        -h)                         help=true ;;
        *)
    esac
done
log debug "Command: $(basename ${0}) --assets-dir=$assets_dir --dst-dir=$dst_dir --force=$force"

if [ "$help" = true ]; then
    echo -e "$USAGE"
    exit 0
fi

if [ -z "$assets_dir" ] || [ -z "$dst_dir" ]; then
    log error "Not all arguments passed" >&2
    echo -e "$USAGE"
    exit 1
fi

if [ ! -d "$assets_dir" ]; then
    log error "There is no assets directory \"$assets_dir\""
    echo -e "$USAGE"
    exit 1
fi

if [ -d "$dst_dir" ]; then
    if ! $force; then
        log error "The destination directory already exists (use the --force " \
                  "flag to remove the already existed destination directory)"
        exit 1
    fi
    rm -rf "$dst_dir"
    log info "The old destination directory has been removed"
fi

mkdir -p "$dst_dir"

export LOGIN_APP_HOST=localhost \
    LOGIN_APP_PORT=20013 \
    ASSETS_PATH="$assets_dir" \
    ACCOUNT_NAME=112 \
    PASSWORD=112 \
    DST_DIR="$dst_dir" \
    LOG_LEVEL="${LOG_LEVEL:-INFO}"

# Generate code based on the server assets
PYTHONPATH="$PROJECT_DIR" python tools/ninmah
