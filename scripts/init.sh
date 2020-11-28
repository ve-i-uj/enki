#
# Constants for bash scripts of the project
#

SERVICE_NAME="enki"

curr_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJ_DIR=`realpath $curr_dir/..`
# Dirctory of python virtual environment
PYVENV_DIR="$HOME/.local/share/virtualenvs/"

echo
echo "*******************************"
echo
echo "SERVICE_NAME=$SERVICE_NAME"
echo
echo "Directories:"
echo
echo "PROJ_DIR=$PROJ_DIR"
echo "PYVENV_DIR=$PYVENV_DIR"
echo
echo "*******************************"
echo
