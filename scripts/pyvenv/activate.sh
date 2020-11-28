#!/bin/bash
#
# Activate the python virtual environment of the project
#

curr_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source `realpath $curr_dir/../init.sh`

source "$PYVENV_DIR/$SERVICE_NAME/bin/activate"
