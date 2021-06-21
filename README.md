## Fetching Debian Buster Image and Verifying It

- `./base-image/fetch-debian-image.sh`

## Installing in a VM for Infrastructure Code Development

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

- Once the installation terminates:
  - reboot the VM
  - make sure to be able to reach its port 22 somehow
  - login as root using your hypervisor interface, install `sudo` and add your user into the `sudo` group: `apt install sudo && gpasswd -a <username> sudo`
  - still as root, run `visudo` to edit `/etc/sudoers` and change the line `%sudo ALL=(ALL:ALL) ALL` into `%sudo ALL=(ALL:ALL) NOPASSWD:ALL` to allow members of the `sudo` group to execute commands as root without entering their password
  - push your ssh key with `ssh-copy-id <username>@<vm-address>` using the password defined during installation

## Provisioning

- Adapt `ansible/inventory.yml` file to reflect how you connect to the host you configure (if you don't have the necessary setup, don't set `domain_name` and `letsencrypt_email` variables)
- Check the administrators list in `ansible/group_vars/tournesol.yml`
- Add users dot files in `ansible/roles/users/files/admin-users` to match administrators tastes and set the `authorized_keys` for each of them
- Set the `DJANGO_DATABASE_PASSWORD`, `DJANGO_SECRET_KEY` and `GRAFANA_ADMIN_PASSWORD` to random values (i.e. `export DJANGO_DATABASE_PASSWORD="$(base64 /dev/urandom | head -c 32)"`)
- Run `./ansible/scripts/provisioning-vm.sh apply` (without `apply` it's a dry-run)
- If the kernel was updated, reboot the VM to start using the new one

## TODO

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

## Creating a superuser

```bash
ssh -t <username>@<server_address> -- sudo -u gunicorn 'bash -c "source /srv/tournesol-backend/venv/bin/activate && SETTINGS_FILE=/etc/tournesol/settings.yaml python /srv/tournesol-backend/manage.py createsuperuser"'
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

## Retrieving Staging Secrets

To run the playbook on the staging VM without changing the secrets, first fetch them and set them in your environment:

```bash
source ./ansible/scripts/get-staging-secrets.sh
```
