# Starting the development environment

## Requirements:
* `docker-compose-plugin` (or `docker-compose`)
* curl


## On Windows

It is recommended on Windows to install:
* WSL2, with a Linux distribution (from a Powershell as administrator: `wsl --install`)
* Docker Desktop (which includes `docker-compose`)

For the frontend dynamic updates to work properly, the git repository should be **cloned inside the WSL2 file system**

If `git diff` displays unexpected modifications (`old mode 100755 new mode 100644`), you can execute 
`git config core.filemode false` to indicate Git to ignore the executable bit in files permissions.

Beware that `./run-docker-compose.sh` in Windows may use a shortcut to the MinGW64 bash (also called Git bash).
If so, type `bash run-docker-compose.sh` to use the WSL2 bash instead.


## Start the containers

```bash
./run-docker-compose.sh
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

The created database includes metadata about ~ 5000 videos, as well as 5 sample accounts with usernames
`user1`, `user2`, `user3`, `user4` and `user5`, and password `tournesol`.


## Rebuild the containers while preserving the database

By default, the database content is initialized with test data.
To recreate the containers (e.g to update the backend dependencies) while preserving the data, use:
```bash
./run-docker-compose.sh restart
```
