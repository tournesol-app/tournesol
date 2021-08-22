## Fetching Debian Bullseye Image and Verifying It

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

- Once the installation terminates and the VM has rebooted:
  - login as root using your hypervisor interface, install `sudo` and add your user into the `sudo` group: `apt install sudo && gpasswd -a <username> sudo`
  - still as root, run `visudo` to edit `/etc/sudoers` and change the line `%sudo ALL=(ALL:ALL) ALL` into `%sudo ALL=(ALL:ALL) NOPASSWD:ALL` to allow members of the `sudo` group to execute commands as root without entering their password
  - push your ssh key with `ssh-copy-id <username>@<vm-address>` using the password defined during installation

## Provisioning

- make sure to be able to reach port 22 of the VM somehow (could be a port forward in your hypervisor)
- Adapt `ansible/inventory.yml` file to reflect how you connect to the host you configure (if you don't have the necessary setup, don't set `letsencrypt_email` variable)
- One way to use the `ansible_host`, `domain_name`, `api_domain_name`, `mediawiki_domain_name` and `grafana_domain_name` variables is to let them as is (`tournesol-vm`, `tournesol-api`, `tournesol-wiki` and `tournesol-grafana`) and to put a `<VM_IP> tournesol-vm tournesol-api tournesol-wiki tournesol-grafana` line in your `/etc/hosts` file
- Check the administrators list in `ansible/group_vars/tournesol.yml`
- Add users dot files in `ansible/roles/users/files/admin-users` to match administrators tastes and set the `authorized_keys` for each of them either in `ansible/group_vars/tournesol.yml` or in `ansible/roles/users/files/admin-users/<username>/.ssh/authorized_keys`
- Run `source ./ansible/scripts/generate-secrets.sh` to generate secrets
- Run `./ansible/scripts/provisioning-vm.sh apply` (without `apply` it's a dry-run)

## TODO

- Backup automation and monitoring (database mainly?)
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

You can do the same with another VM or a different user name:

```bash
source ./ansible/scripts/get-vm-secrets.sh "tournesol-vm" "jst"
```
