## Fetching Ubuntu Server Image and Verifying It
- `./fetch-ubuntu-server-image.sh`

## Installing in a VM for Infrastructure Code Development
- Create a VM using the installer from the previously downloaded ISO
    * tested with the following setup:
        + QEMU/KVM using libvirtd and virtmanager
        + 50GB disk, 4GB RAM, 2 vCPUs
        + default installation, including OpenSSH server, English/US locales and keyboard, my username, password authentication