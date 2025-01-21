.ONESHELL:
SHELL := /bin/bash

.PHONY: help

help:  ## mATRIC
	@awk 'BEGIN {FS = ":.*?## "} /^[.a-zA-Z4_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s \n", $$1, $$2}' $(MAKEFILE_LIST)

check: pat  ## Check playbook
	ansible-playbook --check --ask-vault-pass playbooks/runner.yml

install: ## Install runner
	ansible-playbook --ask-vault-pass playbooks/runner.yml

inv:  ## List the inventory
	ansible-inventory --ask-vault-pass --list

# Development

debug:  ## Run the debug playbook
	ansible-playbook --ask-vault-pass playbooks/debug.yml

role: ## Make a new ansible role
	ansible-galaxy init $1

# Prerequisites

prereq: ansible sshpass ansible deps  sshkeys ## Install all prerequisites

deps:  ## Install dependencies
	ansible-galaxy install -r requirements.yml

sshpass:  ## Install sshpass needed for ansible ssh connection
	sudo apt install sshpass

ansible:  ## Install ansible
	pip install ansible

sshkeys:  ## Install ssh pem file
	ssh-add ./matric_staging.pem
