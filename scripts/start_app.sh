#!/bin/bash
# Start the example application.

curr_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $( realpath "$curr_dir/init.sh" )

cd "$PROJECT_DIR"

if [[ -z "${VIRTUAL_ENV-}" ]]; then
    log error "Activate the python virtual environment at first! (pipenv shell)"
    exit 1
fi

LOG_LEVEL=DEBUG PYTHONPATH="$PROJECT_DIR" python example/console-kbe-demo-client/main.py
