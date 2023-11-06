# Starting the development environment

## Requirements:
* `docker-compose-plugin` (or `docker-compose`)
* curl


### On Windows

It is recommended on Windows to install:
* **WSL2**, with a Linux distribution (just execute `wsl --install` in a Powershell as administrator. More info here: https://docs.microsoft.com/en-us/windows/wsl/install)
* **Docker Desktop** (which includes `docker-compose`. The default configuration should be fine. More info here: https://docs.docker.com/desktop/windows/wsl/)


For the frontend dynamic updates to work properly, the git repository should be **cloned inside the WSL2 file system**.

Beware that `./run-docker-compose.sh` in Windows may use a shortcut to the MinGW64 bash (also called Git bash).
If so, type `bash run-docker-compose.sh` to use the WSL2 bash instead.

If `run-docker-compose.sh` returns the error `rm: cannot remove 'db-data': Permission denied`, db-data can be deleted by executing `sudo rm -R db-data` in the WSL bash.

If `git diff` displays unexpected modifications (`old mode 100755 new mode 100644`), you can execute `git config core.filemode false` to indicate Git to ignore the executable bit in files permissions.

If `compose up` fails with `=> ERROR resolve image config for docker.io/docker/dockerfile:1`, a solution is usually to delete the Docker config.json in WSL2: `bash -c 'rm ~/.docker/config.json'`


## Initialize the containers

The first time you start the dev-env, you will need to build the Docker
containers with the following command.

> **Note**
>
> If you are on Linux, you may encounter the error "Permission denied".
> Usually you can fix it by adding your user to the `docker` group
> (more details in  [the official documentation][docker-docs-linuxpostinstall]).

```bash
./run-docker-compose.sh init
```

The script will create 3 containers:

- **`tournesol-dev-db`**: the PostgreSQL database.   
The data will be stored in `./db-data/` and used as a docker volume.

- **`tournesol-dev-api`**: the Django server.  
    This container runs the development server with the code contained in `../backend/`.  
The code will be reloaded automatically on any file change.  
Follow the logs with `docker logs -f tournesol-dev-api`

* **`tournesol-dev-front`**: the React development server.  
Similarly, this container uses the code present in `../frontend/` to rebuild the application automatically.  
Follow the logs with `docker logs -f tournesol-dev-front`

A superuser will be created automatically with username `user` and the default password `tournesol`.

Then, the application is accessible on http://localhost:3000.

The created database includes video metadata, users and comparisons derived from a subset of Tournesol public dataset.
An additional non-admin user is also created: `user1` with password `tournesol`.

## Restart the containers

When you need to start or restart the existing containers, use:
```bash
./run-docker-compose.sh restart
```

## Rebuild the containers while preserving the database

When you run `init`, the database content is initialized with test data.
To recreate the containers (e.g to update the backend dependencies) while preserving the data, use:
```bash
./run-docker-compose.sh recreate
```

## See all available commands

```bash
./run-docker-compose.sh help
```

## Useful docker command

This will help you during the development.

```bash
# see the running containers
docker ps

# see all containers
docker ps -a

# fetch a container's logs
docker logs tournesol-dev-api

# follow the logs output
docker logs -f tournesol-dev-api
```

## Dump the current database

```bash
./dump-db.sh
```

A .sql.gz file will be written to the directory "./db" (e.g `dump_2022-10-17T16:18:10Z.sql.gz`).


### Push a dev-env db version to the GitHub Container Registry (for Maintainers)

> **Note**  
> To authenticate to the Container registry (ghcr.io) you will need to login (via `docker login`)
> using a GitHub personal access token.  
> See [Authenticating to the Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-to-the-container-registry) for more details.

The dev-env database (loaded by default when initializing the dev-env) is hosted as a Docker image: [ghcr.io/ghcr.io/tournesol-app/postgres-dev-env](https://github.com/tournesol-app/tournesol/pkgs/container/postgres-dev-env) on GitHub. The exact version used in the dev-env and end-to-end tests can be found in [docker-compose.yml](./docker-compose.yml).

To build and push a new version of this image using a dump created as above, use the following commands:

```bash
docker build db --build-arg DUMP_FILE=YOUR_DUMP_FILE_NAME --tag ghcr.io/tournesol-app/postgres-dev-env:YOUR_NEW_TAG

docker push ghcr.io/tournesol-app/postgres-dev-env:YOUR_NEW_TAG
```

⚠️ On MacOS M1, you should specify the correct build platform using:

```bash
docker buildx build --platform linux/amd64 db --build-arg DUMP_FILE=YOUR_DUMP_FILE_NAME --tag ghcr.io/tournesol-app/postgres-dev-env:YOUR_NEW_TAG
```

[docker-docs-linuxpostinstall]: https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user
