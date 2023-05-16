#!/bin/bash
# Check a configuration file of the project.

curr_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source $( realpath "$curr_dir/init.sh" )
source $( realpath "$curr_dir/log.sh" )

is_valid=true

if [ ! -f $PROJECT_DIR/.env ]; then
    log error "There is no \"$PROJECT_DIR/.env\" file"
    exit 1
fi

if [ -z "${LOGINAPP_HOST:-}" ]; then
    log warn "The \"LOGINAPP_HOST\" variable is unset"
    is_valid=false
fi

if [ -z "${LOGIN_APP_PORT:-}" ]; then
    log warn "The \"LOGIN_APP_PORT\" variable is unset"
    is_valid=false
fi

if [ ! -z "${LOGIN_APP_PORT:-}" ] && [ ! "${LOGIN_APP_PORT:-}" -eq "${LOGIN_APP_PORT:-}" ] 2>/dev/null; then
    log warn "The \"LOGIN_APP_PORT\" variable is not integer"
    is_valid=false
fi

if [ -z "${GAME_ACCOUNT_NAME:-}" ]; then
    log warn "The \"GAME_ACCOUNT_NAME\" variable is unset"
    is_valid=false
fi

if [ -z "${GAME_PASSWORD:-}" ]; then
    log warn "The \"GAME_PASSWORD\" variable is unset"
    is_valid=false
fi

if [ -z "${GAME_ASSETS_DIR:-}" ]; then
    log warn "The \"GAME_ASSETS_DIR\" variable is unset"
    is_valid=false
fi

if [ ! -z "${GAME_ASSETS_DIR:-}" ] && [ ! -d "${GAME_ASSETS_DIR:-}" ]; then
    log warn "There is no assets directory \"$GAME_ASSETS_DIR\""
    is_valid=false
fi

if [ -z "${GAME_GENERATED_CLIENT_API_DIR:-}" ]; then
    log warn "The \"GAME_GENERATED_CLIENT_API_DIR\" variable is unset"
    is_valid=false
fi

if $is_valid; then
    log info "The \".env\" configuration file is Ok"
    exit 0
fi
log error "The \".env\" configuration file is invalid"
exit 1
