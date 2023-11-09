
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
- One way to use the `ansible_host`, `domain_name`, `api_domain_name`, and `grafana_domain_name` variables is to let them as is (`tournesol-vm`, `tournesol-api`, and `tournesol-grafana`) and to put a `<VM_IP> tournesol-vm tournesol-api tournesol-grafana` line in your `/etc/hosts` file
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

## Migrate to another server

Throughout this procedure we will use the following vocabulary:
- **old server** refers to the server you want to migrate from;
- **new server** refers to the server that will host the new Tournesol instance.

When you see `<OLD_IP>` or `<NEW_IP>` in the commands, replace them by
respectively the IP address of the old server, and the IP address of the new
server.

1. **Reduce DNS TTL**

Decrease the Time To Live (TTL) of the DNS A records to a low value (e.g., 180 seconds).

2. **Disable the external URLs monitoring timer**

Connect to the server monitoring the machine being migrated.

```bash
# from the monitoring server

sudo systemctl stop external-urls-monitoring.timer
```

Don't forget to restart it again after the migration.

3. **Deploy the services in Maintenance Mode on the old server**

Put the platform into maintenance mode to prevent write operations to the database. This ensures data consistency during the migration process.

4. **Stop all Timers**

This will avoid related services to start and avoid potential data loss or duplicated events.

```bash
# from the old server

sudo systemctl stop "tournesol*.timer" export-backups.timer ml-train.timer pg-backups.timer
```

5. **Stop the web analytics Docker containers**

```bash
# from the old server

sudo systemctl stop tournesol-website-analytics.service
```

5. **(a) Create a manual backup of the web analytics volumes**

```bash
# from the old server

sudo mkdir /backups/plausible

cd /var/lib/docker/volumes/

tar cvzf /backups/plausible/plausible_analytics_db-data.tar.gz plausible_analytics_db-data
tar cvzf /backups/plausible/plausible_analytics_event-data.tar.gz plausible_analytics_event-data
```

5. **(b) Create a manual backup of the Tournesol database**

```bash
# from the old server

sudo systemctl start pg-backups.service
```

6. **Copy Backup Files to the New Server**

Transfer the backup files to the new server using a secure method such as SCP.
Make sure the Tournesol database files are placed in the directory
`/backups/tournesol/db/<backup-name>/`.

```bash
# from the new server

sudo mkdir -p -m 777 /backups/plausible
sudo mkdir -p -m 777 /backups/tournesol/db
```

Don't forget to reset the directory mode of `/backups/plausible` to 755 after
the migration.

```bash
# from your local computer

# Plausible
scp -C -3 -r <OLD_IP>:/backups/plausible <USER>@<NEW_IP>:/backups

# PostgreSQL (example)
scp -C -3 -r <OLD_IP>:/backups/tournesol/db/2023-11-09-daily <USER>@<NEW_IP>:/backups/tournesol/db/2023-11-09-uploaded
```

7. **Update DNS Record with the new IP**

Update the DNS records to point to the IP address of the new server. This step
may take some time to be visible globally, depending on your DNS provider and
the TTL you set earlier.

8. **Launch Deployment Script with Maintenance Mode Enabled**

To reuse the secrets from the old server, and to avoid generating new ones,
we use a modified version ofthe deployment script instead of using the default
provisioning script.

First, update the script `ansible/scripts/deploy-with-secrets.sh`:

```bash
# from your local computer

# replace the line:
source "./scripts/get-vm-secrets.sh" "$DOMAIN_NAME"

# by:
source "./scripts/get-vm-secrets.sh" "<OLD_IP>"
```

Do not forget to revert this change once the migration is complete.

Once the new IP address is available in the DNS, and once the deployment
script has been updated to fetch the secrets from the old server, execute
the deployment script on the new server. Ensure that the script is configured
to operate in maintenance mode, so it does not allow public access until the
migration is complete.

```bash
# from your local computer

# either
./infra/ansible/scripts/deploy-staging.sh apply notfast

# or
./infra/ansible/scripts/deploy-prod.sh apply notfast
```

9. **Import Backup**

On the new server, load the backup data and configuration files that you copied in step 5.

To restore the Plausible Analytics data:

```bash
# from the new server

sudo systemctl stop tournesol-website-analytics.service

cd /var/lib/docker/volumes/

sudo mv plausible_analytics_db-data plausible_analytics_db-data.OLD
sudo mv plausible_analytics_event-data plausible_analytics_event-data.OLD

sudo tar xvzf /backups/plausible/plausible_analytics_db-data.tar.gz plausible_analytics_db-data
sudo tar xvzf /backups/plausible/plausible_analytics_event-data.tar.gz plausible_analytics_event-data

sudo systemctl start tournesol-website-analytics.service
```

To restore the Tournesol database (PostgreSQL):

```bash
# from your local computer

cd ansible
ansible-playbook restore-backup.yml -i inventory.yml -l <ansible-host> -e restore_backup_name=2023-11-09-uploaded
```

10. **Redeploy the Stack Without Maintenance Mode**

After successful data import and configuration adjustments, redeploy your web application stack without maintenance mode. This allows the application to be accessible to users again.

11. **Cleanup**

Reset the temporary modifications. The secrets should now be retrieved from
the new server.

```bash
# from you local machine

git checkout ansible/scripts/deploy-with-secrets.sh
```

Restart the URLs monitoring:

```bash
# from the monitoring server

sudo systemctl start external-urls-monitoring.timer
```

Reset the directory mode of the directories in `/backups/` to 755:

```bash
# from the new server

sudo chomd 755 /backups/plausible
sudo chomd 755 /backups/tournesol
```

Check if all systemd timers are enabled and started. They should be loaded and
active:

```bash
# from the new server

sudo systemctl stop "tournesol*.timer" export-backups.timer ml-train.timer pg-backups.timer
```

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
