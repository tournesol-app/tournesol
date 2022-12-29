
# Infrastructure

## Installing in a VM for Infrastructure Code Development

This section covers how to set up a production-like environment in a virtual machine.

This personal environment allows developers to work on the Ansible deployment recipe and to test their modifications. If you want to work of the Tournesol application code, use the `dev-env` instead.


- Fetch the Debian Bullseye Image and verify it: `./base-image/fetch-debian-image.sh`

- Create a VM using the installer from the previously downloaded ISO

  - tested with the following setup:
    - QEMU/KVM using libvirtd and virtmanager
    - 20GB disk, 4GB RAM, 4 vCPUs
    - default installation:
      - language: English
      - location: other->Europe->Switzerland
      - locale: en_US.UTF-8
      - keyboard: American English
      - hostname: tournesol
      - domain name: empty
      - set a root password
      - username: yours (twice, full name and login)
      - set a user password
      - partitioning: use entire disk, all files in one partition
      - pick a mirror close to your location
      - software selection: only SSH server and standard system utilities

- Once the installation terminates and the VM has rebooted:
  - login as root using your hypervisor interface, install `sudo` and add your user into the `sudo` group: `apt install sudo && gpasswd -a <username> sudo`
  - make sure to be able to reach port 22 of the VM somehow (could be a port forward in your hypervisor)
  
If for any reason you're not able to set up a virtual machine on your computer - your hardware have missing virtualization capabilities, or is not powerful enough - you can still use a remote virtual machine from a Cloud provider. Some Cloud providers offer free credits for new users, but it can get costly if you rent a powerful server and forget to stop it after use. Note this installation method **is not supported** by the team, and you might encounter unexpected issues. 


## Provisioning

- push your ssh key with `ssh-copy-id <username>@<ip-address>` using the password defined during installation
- Connect to the SSH port 22
- As root, run `visudo` to edit `/etc/sudoers` and change the line `%sudo ALL=(ALL:ALL) ALL` into `%sudo ALL=(ALL:ALL) NOPASSWD:ALL` to allow members of the `sudo` group to execute commands as root without entering their password
- Adapt `ansible/inventory.yml` file to reflect how you connect to the host you configure (if you don't have the necessary setup, don't set `letsencrypt_email` variable)
- One way to use the `ansible_host`, `domain_name`, `api_domain_name`, `mediawiki_domain_name` and `grafana_domain_name` variables is to let them as is (`tournesol-vm`, `tournesol-api`, `tournesol-wiki` and `tournesol-grafana`) and to put a `<VM_IP> tournesol-vm tournesol-api tournesol-wiki tournesol-grafana` line in your `/etc/hosts` file
- Check the administrators list in `ansible/group_vars/tournesol.yml`
- Add users dot files in `ansible/roles/users/files/admin-users` to match administrators tastes and set the `authorized_keys` for each of them either in `ansible/group_vars/tournesol.yml` or in `ansible/roles/users/files/admin-users/<username>/.ssh/authorized_keys`
- Run `source ./ansible/scripts/generate-secrets.sh` to generate secrets
- Run `./ansible/scripts/provisioning-vm.sh apply` (without `apply` it's a dry-run)

## TODO

- Application artifacts retrieval with proper triggers on updates (CI integration, CD?) (for now ansible clones, builds and deploys during each run)
- CI/CD design
- IDS/IPS? WAF?
- Applicative logging / metrics (Django models can be instrumented using django_prometheus that is already in place)
- Analytics (SaaS? Matomo?)
- CDN?

## Creating a superuser

```bash
ssh -t <username>@<server_address> -- sudo -u gunicorn 'bash -c "source /srv/tournesol-backend/venv/bin/activate && SETTINGS_FILE=/etc/tournesol/settings.yaml python /srv/tournesol-backend/manage.py createsuperuser"'
```

## Staging Installation

- create server
- point a domain name to its IP and configure `ansible/inventory.yml` accordingly
- login as root and run the following:

```bash
USERNAME=<username>
useradd -m $USERNAME
mkdir /home/$USERNAME/.ssh
cp .ssh/authorized_keys /home/$USERNAME/.ssh/
chown -R $USERNAME:$USERNAME /home/$USERNAME/.ssh
gpasswd -a $USERNAME sudo
visudo
# change the line `%sudo ALL=(ALL:ALL) ALL` into `%sudo ALL=(ALL:ALL) NOPASSWD:ALL`
```

- set the secrets in your environment (`source ./ansible/scripts/generate-secrets.sh`)
- run the playbook `./ansible/scripts/provisioning-staging.sh apply`
- create a superuser: `ssh -t <username>@<domain_name> -- sudo -u gunicorn 'bash -c "source /srv/tournesol-backend/venv/bin/activate && SETTINGS_FILE=/etc/tournesol/settings.yaml python /srv/tournesol-backend/manage.py createsuperuser"'`

## Retrieving Staging Secrets

To run the playbook on the staging VM without changing the secrets, first fetch them and set them in your environment:

```bash
source ./ansible/scripts/get-vm-secrets.sh
```

You can do the same with another VM or a different username:

```bash
source ./ansible/scripts/get-vm-secrets.sh "tournesol-vm" "jst"
```

## Dump Tournesol DB

```bash
ssh -t <username>@<domain_name> -- sudo -u postgres 'bash -c '\''DUMP_DATE=$(date +%Y-%m-%d) && pg_dump -d tournesol -T auth_group -T django_content_type -T auth_permission -T auth_group_permissions -T django_admin_log -T django_migrations -T django_session -T oauth2_provider_application -T oauth2_provider_grant -T oauth2_provider_idtoken -T oauth2_provider_accesstoken -T oauth2_provider_refreshtoken --data-only --inserts > /tmp/dump_$DUMP_DATE.sql && tar cvzf /tmp/dump_$DUMP_DATE.sql.tar.gz -C /tmp dump_$DUMP_DATE.sql && rm /tmp/dump_$DUMP_DATE.sql'\'''
scp "staging.tournesol.app:/tmp/dump_*.sql.tar.gz" .
ssh -t <username>@<domain_name> -- sudo -u postgres 'rm /tmp/dump_*.sql.tar.gz'
```

## Restore Postgres backup

### Restore an entire backup from the current host

```bash
ansible-playbook restore-backup.yml -i inventory.yml -l <ansible-host> -e restore_backup_name=<pg_backup_name>
```
e.g:
```bash
ansible-playbook restore-backup.yml -i inventory.yml -l tournesol-vm -e restore_backup_name=2021-11-12-weekly
```

### Import a backup from another host to an existing database

Data related to OAuth applications in the target database will be preserved to keep a configuration compatible with other services (frontend, etc.).

To import a backup from production to the local tournesol VM:
```
./ansible/scripts/fetch-and-import-pg-backup.sh --backup-name 2021-11-12-weekly --from tournesol.app --to-ansible-host tournesol-vm
```

## Using Grafana with Loki to Browse Logs

Grafana can be used to monitor and alert on various types of data, including log data. The Loki plugin for Grafana allows you to easily view and analyze logs.

### Nginx Logs

The server is using Nginx as a reverse proxy, and produces access logs in JSON format. Each line of the log file `json_access.log` will contain a single request represented in JSON. Here are some examples of queries you can use to filter and analyze these logs in Grafana with Loki.

The Loki plugin provides a query builder and an "explain" option that make relatively easy to create a custom query to look for specific events.

> Direct link (on staging):  
https://grafana.staging.tournesol.app/goto/mPTIzpt4k?orgId=1

#### Query examples

* To view all logs for a specific HTTP host:

```
{filename="/var/log/nginx/json_access.log"} | json | http_host = `api.tournesol.app`
```

You can also use the Grafana query language to combine multiple filters and perform more advanced searches.

* To view all logs for a specific path and/or method:

```
{filename="/var/log/nginx/json_access.log"} | json | http_host = `api.tournesol.app` | request_method = `POST` | request_uri =~ `/users/me/comparisons.*`
```

* To view all logs for a specific HTTP status code:

```
{filename="/var/log/nginx/json_access.log"} | json | status >= 500
```

* To view all logs for a specific user agent:

```
{filename="/var/log/nginx/json_access.log"} | json | http_user_agent =~ ".*iPhone OS.*"
```

* To view all API requests with duration over 500ms:
```
{filename="/var/log/nginx/json_access.log"} | json | http_host = "api.tournesol.app" | request_time > 0.5
```

### Systemd Services

You can use Grafana with the Loki plugin to view and analyze the logs produced by services managed by Systemd.

To view logs for a specific Systemd unit, you can use the {unit="service_name"} filter. For example, to view logs for the ml-train service:

```
{unit="ml-train.service"}
```

As with Nginx logs, you can use the Grafana query language to combine multiple filters and perform more advanced searches. For example, to view logs for the gunicorn service containing the word "Warning":

```
{unit="gunicorn.service"} |= `Warning`
```
> Direct link (on staging):  
https://grafana.staging.tournesol.app/goto/lVgjR0pVk?orgId=1

## Copyright & License

Copyright 2021-2022 Association Tournesol and contributors.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.

Included license:
 - [AGPL-3.0-or-later](./LICENSE)
