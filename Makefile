SHELL := /bin/bash

ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
SCRIPTS := $(ROOT_DIR)/scripts

export PYTHONPATH := $(ROOT_DIR)
export PIPENV_VERBOSITY=-1

ifneq ("$(wildcard .env)","")
	include .env
	export $(shell sed 's/=.*//' .env)
endif

.PHONY: *
.EXPORT_ALL_VARIABLES:
.DEFAULT:
	@echo Use \"make help\"

all: help

loginapp_send_hello: ## Send the "hello" message to the loginapp
	@pipenv run python cmd/healthcheck/loginapp/send_hello.py

machine_send_onQueryAllInterfaceInfos: ## Send the "onQueryAllInterfaceInfos" message to Machine
	@pipenv run python cmd/healthcheck/machine/send_onQueryAllInterfaceInfos.py

generate_entities: ## Generate the python code of the client game API
	@rm -rf $(GAME_GENERATED_CLIENT_API_DIR)
	@export GAME_ASSETS_DIR="$(GAME_ASSETS_DIR)" \
    	ACCOUNT_NAME=$(GAME_ACCOUNT_NAME) \
    	PASSWORD=$(GAME_PASSWORD) \
    	GAME_GENERATED_CLIENT_API_DIR="$(GAME_GENERATED_CLIENT_API_DIR)"; \
	pipenv run python tools/ninmah

check_config: ## Check variables in the configuration file
	@pipenv run bash $(SCRIPTS)/check_config.sh

start_console_app:
	@pipenv run python examples/console-kbe-demo-client/main.py

-----: ## -----

define HELP_TEXT
*** [enki] Help ***

The python network library for communication with the KBEngine game server.

The .env file in the root directory is mandatory. Copy the config from the "configs" directory
or set your own settings in the "<project_dir>/.env" settings file. For more information
visit the page <https://github.com/ve-i-uj/enki>

Example:

cp configs/example.env .env
make send_hello
make start_console_app
_____

Rules:

endef

export HELP_TEXT
help: ## This help
	@echo "$$HELP_TEXT"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $$(echo $(MAKEFILE_LIST) | cut -d " " -f1) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "%-15s %s\n", $$1, $$2}'
	@echo
