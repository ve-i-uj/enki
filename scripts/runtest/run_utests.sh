#!/bin/bash
# Run unit tests.

curr_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $( realpath "$curr_dir/init.sh" )

cd "$PROJECT_DIR"
pytest -o log_cli=true --log-cli-level=DEBUG --disable-warnings tests/utests
