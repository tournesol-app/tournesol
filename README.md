## Fetching Ubuntu Server Image and Verifying It
- `./base-image/fetch-ubuntu-server-image.sh`

## Installing in a VM for Infrastructure Code Development
- Create a VM using the installer from the previously downloaded ISO
    * tested with the following setup:
        + QEMU/KVM using libvirtd and virtmanager
        + 25GB disk, 4GB RAM, 2 vCPUs
        + default installation, including OpenSSH server, English/US locales and keyboard, my username, password authentication
- Once the installation terminates:
    * reboot the VM
    * make sure to be able to reach its port 22 somehow
    * push your ssh key with `ssh-copy-id <username>@<vm-address>` using the password defined during installation
    * ssh into the VM, run `sudo visudo` to edit `/etc/sudoers` and change the line `%sudo	ALL=(ALL:ALL) ALL` into `%sudo	ALL=(ALL:ALL) NOPASSWD:ALL` to allow members of the `sudo` group to execute commands as root without entering their password

## Provisioning
- Adapt `ansible/inventory.yml` file to reflect how you connect to the host you configure
- Check the administrators list in `ansible/group_vars/tournesol.yml`
- Add users dot files in `ansible/roles/users/files/admin-users` to match administrators tastes and set the `authorized_keys` for each of them
- Set the `DJANGO_DATABASE_PASSWORD` and `DJANGO_SECRET_KEY` to random values (i.e. `export DJANGO_DATABASE_PASSWORD="$(base64 /dev/urandom | head -c 32)"`)
- Run `./ansible/scripts/provisioning-vm.sh apply` (without `apply` it's a dry-run)
- If the kernel was updated, reboot the VM to start using the new one

## TODO
- Setting a production target with hosting domain and certbot for TLS
- Monitoring tools (munin? prometheus/grafana? external health checks?)
- Alerting
- Backup automation and monitoring (database mainly?)
- Staging environment on the same VM?
- Application artifacts retrieval with proper triggers on updates (CI integration, CD?)
- CI/CD design
- IDS/IPS? WAF?
- Applicative logging / metrics
- Analytics (SaaS? Matomo?)
- CDN?
- Container based setup? Docker? k3s?
- Cloud setup relying on managed services?

## WIP

```bash
ssh 192.168.122.60 -- sudo -u gunicorn 'bash -c "source /srv/tournesol-backend/venv/bin/activate && SETTINGS_FILE=/etc/tournesol/settings.yaml python /srv/tournesol-backend/manage.py migrate"'
ssh 192.168.122.60 -- sudo mkdir /var/www/html/static
ssh 192.168.122.60 -- sudo chmod o+rwx /var/www/html/static
ssh 192.168.122.60 -- sudo -u gunicorn 'bash -c "source /srv/tournesol-backend/venv/bin/activate && SETTINGS_FILE=/etc/tournesol/settings.yaml python /srv/tournesol-backend/manage.py collectstatic"'
ssh 192.168.122.60 -- sudo chmod -R o-rwx /var/www/html/static
ssh 192.168.122.60 -- sudo chown -R www-data:www-data /var/www/html/static
ssh -t 192.168.122.60 -- sudo -u gunicorn 'bash -c "source /srv/tournesol-backend/venv/bin/activate && SETTINGS_FILE=/etc/tournesol/settings.yaml python /srv/tournesol-backend/manage.py createsuperuser"'
```

## Staging Installation

- create server
- point a domain name to its IP and configure `ansible/inventory.yml` accordingly
- login as root and run the following:

```bash
useradd -m <username>
mkdir ~<username>/.ssh
cp .ssh/authorized_keys ~<username>/.ssh/
chown -R <username>:<username> ~<username>/.ssh
gpasswd -a <username> sudo
visudo
# change the line `%sudo ALL=(ALL:ALL) ALL` into `%sudo ALL=(ALL:ALL) NOPASSWD:ALL`
```

- set the secrets in your environment `export DJANGO_DATABASE_PASSWORD="$(base64 /dev/urandom | head -c 32)" && export DJANGO_SECRET_KEY="$(base64 /dev/urandom | head -c 32)"`
- run the playbook `./ansible/scripts/provisioning-staging.sh apply`
- create a superuser: `ssh -t <username>@<domain_name> -- sudo -u gunicorn 'bash -c "source /srv/tournesol-backend/venv/bin/activate && SETTINGS_FILE=/etc/tournesol/settings.yaml python /srv/tournesol-backend/manage.py createsuperuser"'`

useradd -m jst
mkdir ~jst/.ssh
cp .ssh/authorized_keys ~jst/.ssh/
chown -R jst:jst ~jst/.ssh
gpasswd -a jst sudo
visudo
