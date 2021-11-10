# Create a development environment with `docker-compose`

## Quick start

### Requirements:
* docker-compose
* curl
* expect

### Start the containers

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

Then, the application is visible on http://localhost:3000.  

