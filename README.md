## Fetching Ubuntu Server Image and Verifying It
- `./fetch-ubuntu-server-image.sh`

## Installing in a VM for Infrastructure Code Development
- Create a VM using the installer from the previously downloaded ISO
    * tested with the following setup:
        + QEMU/KVM using libvirtd and virtmanager
        + 50GB disk, 4GB RAM, 2 vCPUs
        + default installation, including OpenSSH server, English/US locales and keyboard, my username, password authentication
- Once the installation terminates:
    * reboot the VM
    * make sure to be able to reach its port 22 somehow
    * push your ssh key with `ssh-copy-id <username>@<vm-address>` using the password defined during installation
    * ssh into the VM, run `sudo visudo` to edit `/etc/sudoers` and change the line `%sudo	ALL=(ALL:ALL) ALL` into `%sudo	ALL=(ALL:ALL) NOPASSWD:ALL` to allow members of the `sudo` group to execute commands as root without entering their password

## Provisioning
- Adapt `ansible/inventory.yml` file to reflect how you connect to the host you configure
- Check the administrators list in `ansible/group_vars/tournesol.yml`
- Add users dot files in `ansible/roles/users/files/admin-users` to match administrators tastes
- Run `ansible-playbook -i inventory.yml -l tournesol-vm setup.yml --verbose` from `ansible` directory
- If the kernel was updated, reboot the VM to start using the new one
