import os


def _env_flag(name: str, default: bool) -> bool:
    """Read a boolean flag from the environment.

    Unset or empty means `default`. Otherwise the flag is enabled only if the value
    is exactly "1"; any other value (e.g. "0") disables it.
    """
    value = os.environ.get(name)
    if not value:
        return default
    return value == "1"


def _env_list(name: str) -> list[str] | None:
    """Parse a comma-separated environment variable, or return None if unset or empty."""
    items = [item.strip() for item in os.environ.get(name, "").split(",")]
    return [item for item in items if item] or None


# Required. Public hostname at which the feed is served (no scheme, no port).
# It defines the server's did:web identity.
FEED_SERVER_HOSTNAME = os.environ["FEED_SERVER_HOSTNAME"]
FEED_SERVER_DID = f"did:web:{FEED_SERVER_HOSTNAME}"

# Optional. Comma-separated names of the feeds to serve, e.g. "chronofair,videos_v0".
# When unset, all feeds are served. Valid names are the keys of ALL_FEEDS in
# feeds/__init__.py.
FEED_SERVER_ENABLED_FEEDS = _env_list("FEED_SERVER_ENABLED_FEEDS")

# Set to 1 to run the Jetstream listener and the post processor inside the server
# process. For development and testing only: in production, run them as separate
# workers (worker_jetstream.py and worker_process.py).
FEED_SERVER_RUN_TASKS_IN_LIFESPAN = _env_flag(
    "FEED_SERVER_RUN_TASKS_IN_LIFESPAN",
    default=False,
)

# Enabled by default. The Jetstream listener resumes from the last event position
# stored in Redis, so events received while it was down are replayed on restart.
# Set to 0 to always start from the live stream instead.
FEED_SERVER_JETSTREAM_USE_STORED_CURSOR = _env_flag(
    "FEED_SERVER_JETSTREAM_USE_STORED_CURSOR",
    default=True,
)
