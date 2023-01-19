# Constants for bash scripts of the project.

_curr_dir=$( realpath "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"/.. )
export _curr_dir=$_curr_dir  # С этой строкой PROJECT_DIR корректно прописывается envsubst (?)

export PROJECT_DIR="$_curr_dir"
export SCRIPTS="$PROJECT_DIR/scripts"

export PROJECT_NAME=enki
