#
# Constants for bash scripts of the project
#

_curr_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

PROJECT_DIR=$( realpath "$_curr_dir/.." )
PROJECT_NAME=$( basename "$PROJECT_DIR" )

SCRIPTS="$PROJECT_DIR/scripts"

source `realpath $SCRIPTS/log.sh`
