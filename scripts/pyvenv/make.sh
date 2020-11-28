#!/bin/bash
#
# Cretes python virtual environment
#

curr_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source `realpath $curr_dir/../init.sh`

python3 -m pip install -U pip
python3 -m pip install -U virtualenv

if [ ! -d "$PYVENV_DIR" ]; then
	mkdir -p $PYVENV_DIR
fi

python3 -m venv "$PYVENV_DIR/$SERVICE_NAME"
