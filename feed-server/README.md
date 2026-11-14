# feed-server

An [AT Protocol](https://atproto.com) feed generator server for Bluesky, written in Python with FastAPI.

## Architecture

````
                ┌───────────────────┐
                │ Jetstream         │
                │ (ATproto network) │
                └─────────┬─────────┘
                          │ posts, reposts
                          ▼
                  ┌──────────────┐
                  │ (1) listener │
                  └───────┬──────┘
                          │ queue
                          ▼
┌───────────────┐    ┌─────────┐    ┌─────────────────┐    ┌─────────────────┐
│ (2) processor │◄──►│  Redis  │◄──►│ (3) API + feeds │◄──►│ Bluesky AppView │
└───────────────┘    └─────────┘    └─────────────────┘    └─────────────────┘
````

1. The **listener** reads posts and reposts from [Jetstream v1](https://bsky.network/docs/jetstream/)
and pushes them to a queue in Redis.

2. The **processor** reads the queue, then stores and indexes the records for the feeds.

3. The **API** answers the Bluesky AppView requests (like `app.bsky.feed.getFeedSkeleton`).
Each feed reads the indexed records from Redis.


| # | Component | Code |
|---|-----------|------|
| (1) | Jetstream listener | [`indexer/jetstream.py`](./src/feed_server/indexer/jetstream.py), started by [`worker_jetstream.py`](./src/feed_server/worker_jetstream.py) |
| (2) | Processor | `process_posts()` in [`main.py`](./src/feed_server/main.py), started by [`worker_process.py`](./src/feed_server/worker_process.py) |
| (3) | API + feeds | FastAPI app in [`main.py`](./src/feed_server/main.py), routes in [`routes/`](./src/feed_server/routes), feeds in [`feeds/`](./src/feed_server/feeds) |
| | Redis | [`db/redis.py`](./src/feed_server/db/redis.py) |


## Install

Install Redis server.

Create the `.env` file.

```bash
cp .env.example .env
```

And configure the environment variables.

```bash
# For development, with ATproto records processing in background tasks
FEED_SERVER_HOSTNAME=localhost
FEED_SERVER_RUN_TASKS_IN_LIFESPAN=1

# For production, where workers are to be started separately
FEED_SERVER_HOSTNAME=at.example.com
FEED_SERVER_RUN_TASKS_IN_LIFESPAN=0
```

## Usage

### Run the server

To serve all feeds (hardcoded for now), run:

```bash
uv run --env-file .env fastapi dev src/feed_server/main.py
```

On production you want to run the workers in different processes. Also run:

```bash
# To listen to the stream of ATproto records, and queue them:
uv run --env-file .env src/feed_server/worker_jetstream.py
```

```bash
# To read the queued records, index and prepare them for the feeds:
uv run --env-file .env src/feed_server/worker_process.py
```

### Publish the feeds

[`scripts/feedgen.py`](./scripts/feedgen.py) publishes or unpublishes a feed generator record on a Bluesky account:

````bash
uv run scripts/feedgen.py --help
````

## Available Feeds

### Chronofair 

[Source](./src/feed_server/feeds/chronofair.py)

Your chronological feed, but fairer. ChronoFair rebalances posts across all your followed accounts. No single poster floods your feed. An open building block for social recommendation.

* Only considers posts and reposts by followed accounts
* Gives the same weight to all followed accounts, independently of the number of their posts
* Gives more weight to reposts by multiple followed accounts
* Gives less weight to posts already seen

#### Notes

Requester's follows are currently retrived (and cached) from the public Bluesky API, in [`follows.py`](./src/feed_server/follows.py)

### Chronological

[Source](./src/feed_server/feeds/chronological.py)

A regular chronological feed, as an example.


### Videos

[Source](./src/feed_server/feeds/videos.py)

A non-personalized feed, retrieving all posts mentioning a video recommended collectively on [Tournesol](https://tournesol.app).

The videos are checked against the Tournesol API, in [`feeds/videos.py`](./src/feed_server/feeds/videos.py)

## Copyright & License

Copyright 2026 Association Tournesol and contributors.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.

Included license:
 - [AGPL-3.0-or-later](./LICENSE)
