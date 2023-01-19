#!/usr/bin/bash
# Write the new version to the version.txt file and mark the current commit
# by a version tag.

USAGE="\nUsage. The scripts sets a new project version. Use the new version \
in the first argument. The script works only on the \"develop\" branch. \
Example:\nbash $0 v1.2.3\n"

# Import global constants of the project
curr_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $( realpath "$curr_dir"/../init.sh )
source $( realpath $SCRIPTS/log.sh )

VERSION_PATH="$PROJECT_DIR/version.txt"

version="$1"
if [ -z "$version" ]; then
    log error "There is no version in the first argument"
    echo -e "$USAGE"
    exit 1
fi

if [ $( git branch --show-current ) != "develop" ]; then
    log error "The script works only on the \"develop\" branch."
    echo -e "$USAGE"
    exit 1
fi

echo "The version \"$version\" will be set ..."
git commit -a -m "Set the version \"$version\" (auto commit)"
echo "$version" | tee >( xargs git tag ) > "$VERSION_PATH"
git push origin develop
git push --tags -f

log info "Done ($0)"
