# mATRIC Infrastructure Provisioning

## Prerequisite

* A Server that can be accessed via SSH
* Linux - Ubuntu/Debian

### Adding a key file

* ssh-add matric_staging.pem

## Ansible

There are some playbooks available for provisioning the server and ensuring the environment
is ready for a github action runner deployment.

### Inventory

Add the new server to the Ansible inventory and groups

* inventory/hosts - The main host definitions
* inventory/group_vars/matrics/vars - The matrics group variables

The labels for github runner are configured as group vars. eg. labels: staging, self-hosted.
These should match the labels requested in the workflow yml for the environment.

Github Personal Access Token

This is stored in an ansible vault and requires the vault password.

* inventory/group_vars/all/vault

### Provisioning the server

This will run the 'runner.yml' playbook which provisions and configures docker and the github runner.

* make install

This should register the server as a github runner. You can check this by going to the mATRIC-master repo and finding the runner under Actions->Runners->Self Hosted