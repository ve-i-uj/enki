#!/bin/bash
# Run integration tests.

curr_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $( realpath "$curr_dir/init.sh" )

cd "$PROJECT_DIR"
export LOGINAPP_HOST=localhost \
    LOGINAPP_PORT=20013
pytest -o log_cli=true --log-cli-level=INFO --disable-warnings tests/itests

