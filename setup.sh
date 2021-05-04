#!/bin/bash

# if at least one command fails, exit with error
set -e

echo "Setting everything up to run Tournesol:"
echo "Step 1: Install the appropriate version of Mozilla Firefox."
echo "Step 2: Install the apt dependencies."
echo "Step 3: Install nodejs dependencies for the frontend."
echo "Step 4: Create a new python3 venv and install the python dependencies for the backend."

echo " "
echo "=================================================="
echo "Step 1 / 4: Install the appropriate version of Mozilla Firefox."
echo " "
# Install the appropriate version of Firefox
if [ "$(firefox --version)" != "Mozilla Firefox 84.0.1" ]; then
    echo "Installing Mozilla Firefox version 84.0.1"
	wget -c https://download-installer.cdn.mozilla.net/pub/firefox/releases/84.0.1/linux-x86_64/en-US/firefox-84.0.1.tar.bz2
    tar -xvf firefox-84.0.1.tar.bz2
else
    echo "OK: Mozilla Firefox version 84.0.1 already installed."
fi

echo " "
echo "=================================================="
echo "Step 2 / 4: Install the apt dependencies."
echo " "
# Install  apt dependencies
sudo apt-get update
sudo apt-get install -y $(grep -vE "^\s*#" pkglist.txt | tr "\n" " ")

# For nodejs, we need to execute the code from nodesource.com, which also executes `apt-get update`
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo apt-get clean

echo " "
echo "=================================================="
echo "Step 3 / 4: Install nodejs dependencies for the frontend."
echo " "
# Install frontend dependencies
cd frontend
npm ci
cd ..

echo " "
echo "=================================================="
echo "Step 4 / 4: Create a new python3 venv and install the python dependencies for the backend."
echo " "
# Create venv and install python3 dependencies:
python3.7 -m venv venv-tournesol
source venv-tournesol/bin/activate
python3.7 -m pip install --upgrade pip
python3.7 -m pip install -r backend/requirements.txt
python3.7 -m pip cache purge
rm -rf ~/.cache/pip/

echo " "
echo "=================================================="
echo "Done."
