# feed-server

## Install

Create the `.env` file.

```bash
cp .env.example .env
```

And configure the environment variables.

```bash
# For development
FEED_SERVER_HOSTNAME=localhost
FEED_SERVER_RUN_TASKS_IN_LIFESPAN=1

# For production
FEED_SERVER_HOSTNAME=at.example.com
FEED_SERVER_RUN_TASKS_IN_LIFESPAN=0
```

## Usage

### Run the server

```bash
uv run --env-file .env fastapi dev src/feed_server/main.py
```

## Available Feeds

### Chronofair 

[Source](./src/feed_server/feeds/chronofair.py)

Your chronological feed, but fairer. ChronoFair rebalances posts across all your followed accounts. No single poster floods your feed. An open building block for social recommendation.

* Only considers posts and reposts by followed accounts
* Gives the same weight to all followed accounts, independently of the number of their posts
* Gives more weight to reposts by multiple followed accounts
* Gives less weight to posts already seen

### Chronological

[Source](./src/feed_server/feeds/chronological.py)

A regular chronological feed, as an example.


### Videos

[Source](./src/feed_server/feeds/videos.py)

A non-personalized feed, retrieving all posts mentioning a video recommended collectively on [Tournesol](https://tournesol.app).


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
