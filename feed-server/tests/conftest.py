import os

# feed_server.config reads required settings from the environment at import time,
# so they must be set before any test imports the application package.
os.environ.setdefault("FEED_SERVER_HOSTNAME", "feed.test")
