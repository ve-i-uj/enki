#!/bin/bash
# Start the code generator.

curr_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $( realpath "$curr_dir/init.sh" )

cd "$PROJECT_DIR"
export PYTHONPATH="$PROJECT_DIR"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"

cmd="python \"$PROJECT_DIR/tools/ninmah/main.py\""
if [ -z "$VIRTUAL_ENV" ]; then
    pipenv run python "$PROJECT_DIR/tools/ninmah/main.py"
fi

python "$PROJECT_DIR/tools/ninmah/main.py" --log-level=$LOG_LEVEL
