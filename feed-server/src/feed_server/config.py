import os

# Hostname configuration
FEED_SERVER_HOSTNAME = os.environ["FEED_SERVER_HOSTNAME"]
FEED_SERVER_DID = f"did:web:{FEED_SERVER_HOSTNAME}"

# Set FEED_SERVER_RUN_TASKS_IN_LIFESPAN=1 to listen to Jetstream and process posts
# in the server main process. (For dev and testing purposes only)
FEED_SERVER_RUN_TASKS_IN_LIFESPAN = os.environ.get("FEED_SERVER_RUN_TASKS_IN_LIFESPAN") == "1"
