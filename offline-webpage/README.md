## Description

Server to display the webpage announcing that the site is offline and offering to submit an email address to be notified when it will be back up.

## Create Database

```bash
./create-db.sh
```

## Build Server

```bash
go build
```

## Launch Server

```bash
./offline-webpage
```

## Create Database

```bash
./get-emails.sh
```

## Deployment

- copy `offline-webpage` directory onto the server in your home directory

  ```bash
  scp -P 23 -r ../offline-webpage <username>@tournesol.app:.
  ```

- SSH into the server

  ```bash
  ssh -p 23 <username>@tournesol.app
  ```

- build the server

  ```bash
  pushd ~/offline-webpage && go build && popd
  ```

- copy the server in `/srv/` and set the proper ownership and permissions
  ```bash
  sudo mkdir -p /srv/offline-webpage
  sudo cp ~/offline-webpage/{create-db.sh,get-emails.sh,offline-webpage,index.html} /srv/offline-webpage/
  sudo chown -R www-data:www-data /srv/offline-webpage
  sudo chmod -R u=rwx,g=,o= /srv/offline-webpage
  sudo chmod u=rw,g=,o= /srv/offline-webpage/index.html
  ```
- copy the service file and set the proper ownership and permissions

  ```bash
  sudo cp ~/offline-webpage/offline-webpage.service /etc/systemd/system/
  sudo chown root:root /etc/systemd/system/offline-webpage.service
  sudo chmod u=rw,g=r,o=r /etc/systemd/system/offline-webpage.service
  ```

- create the database

  ```bash
  sudo -u www-data /srv/offline-webpage/create-db.sh
  ```

- enable and start the service

  ```bash
  sudo systemctl daemon-reload && sudo systemctl enable --now offline-webpage
  ```

- configure the proxy to forward requests to `127.0.0.1:8080` and to set `x-forwarded-for` header
