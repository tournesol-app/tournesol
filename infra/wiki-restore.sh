#!/usr/bin/env bash

set -Eeuo pipefail

CURRENT_DIR="$(dirname "$0")"

cd "$CURRENT_DIR"

export VM_ADDR="${1:-"staging.tournesol.app"}"
export VM_USER="${2:-"$USER"}"

ssh "$VM_USER@$VM_ADDR" -- mkdir -p tmp-wiki-restore

tar xvf mediawiki.tgz
scp -r images "$VM_USER@$VM_ADDR":./tmp-wiki-restore/
scp -r resources "$VM_USER@$VM_ADDR":./tmp-wiki-restore/
rm -rf images resources

ssh "$VM_USER@$VM_ADDR" -- sudo cp -r ./tmp-wiki-restore/images/* /var/lib/mediawiki/images/
ssh "$VM_USER@$VM_ADDR" -- sudo chown -R www-data:www-data /var/lib/mediawiki/images
ssh "$VM_USER@$VM_ADDR" -- sudo cp ./tmp-wiki-restore/resources/assets/{sunflower.jpg,tournesol_logo.png} /usr/share/mediawiki/resources/assets/
ssh "$VM_USER@$VM_ADDR" -- rm -rf tmp-wiki-restore

# ssh "$VM_USER@$VM_ADDR" -- sudo mv /etc/mediawiki/LocalSettings.php /etc/mediawiki/LocalSettings.php.tmp

# ssh "$VM_USER@$VM_ADDR" -- sudo -u www-data php /var/lib/mediawiki/maintenance/install.php \
# --confpath /tmp/LocalSettings.php \
# --dbname mediawiki \
# --dbuser mediawiki \
# --dbpass "$MEDIAWIKI_DATABASE_PASSWORD" \
# --installdbuser mediawiki \
# --installdbpass "$MEDIAWIKI_DATABASE_PASSWORD" \
# --pass "$MEDIAWIKI_ADMIN_PASSWORD" \
# --server http://tournesol-wiki \
# --scriptpath / \
# Tournesol \
# admin

# ssh "$VM_USER@$VM_ADDR" -- sudo mv /etc/mediawiki/LocalSettings.php.tmp /etc/mediawiki/LocalSettings.php

# ssh "$VM_USER@$VM_ADDR" -- echo "$MEDIAWIKI_ADMIN_PASSWORD" \> mediawiki_admin_password
# ssh "$VM_USER@$VM_ADDR" -- sudo mv mediawiki_admin_password /root/mediawiki_admin_password
# ssh "$VM_USER@$VM_ADDR" -- sudo chown root:root /root/mediawiki_admin_password
# ssh "$VM_USER@$VM_ADDR" -- sudo chmod go-rwx /root/mediawiki_admin_password

ssh "$VM_USER@$VM_ADDR" -- sudo -u www-data php /var/lib/mediawiki/maintenance/importImages.php --search-recursively /var/lib/mediawiki/images

ssh "$VM_USER@$VM_ADDR" -- sudo -u www-data php /var/lib/mediawiki/maintenance/importDump.php --conf /etc/mediawiki/LocalSettings.php < dump.xml
rm dump.xml

ssh "$VM_USER@$VM_ADDR" -- sudo -u www-data php /var/lib/mediawiki/maintenance/update.php
ssh "$VM_USER@$VM_ADDR" -- sudo -u www-data php /var/lib/mediawiki/maintenance/rollbackEdits.php --user "MediaWiki_default" --titles "Main_Page" --summary "revert defaut page"
