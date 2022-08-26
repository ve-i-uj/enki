#!/bin/bash
# Start the project application.

curr_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $( realpath "$curr_dir/init.sh" )

if [ -z "$VIRTUAL_ENV" ]; then
    cd "$PROJECT_DIR"
    pipenv shell
fi

export PYTHONPATH="$PROJECT_DIR"
export LOG_LEVEL="$LOG_LEVEL"
python "$PROJECT_DIR/enki/application/main.py"
