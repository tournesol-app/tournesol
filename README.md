# Tournesol: collaborative content recommendation

This github hosts the code of the platform [Tournesol.app](https://tournesol.app).

See the wiki page [Contribute to Tournesol](https://wiki.tournesol.app/index.php/Contribute_to_Tournesol) for details.

![Home page of Tournesol.app](https://user-images.githubusercontent.com/10453308/115123905-9b6b4300-9fbf-11eb-8853-25552d13f7b0.png)

We use [TensorFlow](http://tensorflow.org/) to compute the aggregated scores,
[Django](https://www.djangoproject.com/) for the backend, and [React.js](https://reactjs.org/) for the front-end.

## How to launch (tested on Ubuntu in WSL and on Ubuntu 20.04)

![Continuous Integration](https://github.com/tournesol-app/tournesol/workflows/Continuous%20Integration/badge.svg?branch=master)

<details>
  <summary>Click to expand</summary>

First, clone this repo and `cd` to it.

<h3>Prerequisites</h3>

1. Make sure that Python 3 is installed.

2. Install Firefox version 84.0.1:
   
   To check the version of Firefox:
   
   ```
   $ firefox --version
   Mozilla Firefox 84.0.1
   ```
   
   If the output of `$ firefox --version` is different from above, install the correct version of Firefox with:
   
   ```
   wget -c https://download-installer.cdn.mozilla.net/pub/firefox/releases/84.0.1/linux-x86_64/en-US/firefox-84.0.1.tar.bz2
   tar -xvf firefox-84.0.1.tar.bz2
   sudo ln -fs $(pwd)/firefox/firefox /usr/bin/firefox
   ```

2. [Install](https://github.com/nodesource/distributions/blob/master/README.md) latest nodejs:
   
   ```
   curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

3. Install dependencies for front-end:

   ```
   $ cd frontend
   frontend $ npm ci
   frontend $ cd ..
   ```

4. Install the dependencies specified in `pkglist.txt`:

   ```
   $ sudo apt-get install $(grep -vE "^\s*#" pkglist.txt | tr "\n" " ")
   ```

5. Create a virtual environment for backend and install its dependencies:

   ```
   $ python3 -m pip install --upgrade pip
   $ python3 -m venv venv

   # run that to go inside the virtual environment
   $ source venv/bin/activate
   (venv) $ pip install -r backend/requirements.txt
   ```
6. Run tests to see that the installation is correct: `./tests.sh`

<h3>Building and running front-end</h3>

```
$ cd frontend

# will watch for changes made to the frontend source code and re-build automatically:
frontend $ npm run dev
```

<h3>Running back-end</h3>

```
(venv) $ . ./debug_export.sh # to set env vars
# cd backend

# (optional) run training
(venv) backend $ python manage.py ml_train

# (optional) download latest video metadata
(venv) backend $ python manage.py add_videos

# optional: create a user for yourself
(venv) backend $ python manage.py createsuperuser

# now go to localhost:8000
(venv) backend $ python manage.py runserver
```
</details>

## API
<details>
  <summary>Click to expand</summary>

API is implemented in [Django-REST](https://www.django-rest-framework.org/) using [Spectacular](https://github.com/tfranzel/drf-spectacular) for annotations compliany with [OpenAPI 3.0](https://swagger.io/specification/):

* API (v2): [api_v2](backend/backend/api_v2), running at [api/v2/](http://127.0.0.1:8000/api/v2/).
* For API v2, the [OpenAPI 3](https://swagger.io/specification/) schema is available at [schema.json](backend/schema.json)
  or at [schema/](http://127.0.0.1:8000/schema/)
  - To generate it, run
    ```shell
    backend $ python manage.py spectacular --file schema.json --format openapi-json --validate
    ```
* For API v2, auto-generated documentation is available as well:
  - Via Swagger: [schema/swagger-ui/](http://127.0.0.1:8000/schema/swagger-ui/)
  - Via ReDoc: [schema/redoc/](http://127.0.0.1:8000/schema/redoc/)
  
* <s>Old API (v1): [api.py](backend/backend/api_v1/api.py), will run at [api_explorer/](http://127.0.0.1:8000/api_explorer/)</s> deprecated

</details>

## Documentation

- Backend documentation (Sphinx): [backend/doc/build/html/index.html](backend/doc/build/html/index.html)
- API v2 documentation in Markdown (auto-generated): [API/README.md](API/README.md)
- API v2 documentation for JavaScript auto-generated code: [frontend/api/README.md](frontend/api/README.md)


## Website structure

- Main page -- loads react.js template
- `/admin` Django admin panel. Use the superuser login you created
- Training artifacts: `/files`

### Machine learning model

<details>
  <summary>Click to expand</summary>

- The video fields (reliability, ...) are described in [rating_fields.py](backend/backend/rating_fields.py).
- The model transforms Expert Ratings (pairwise comparisons), [`ExpertRating`](backend/backend/models.py) model into aggregated scores for each `Video`
- Per-expert scores are written to the `VideoRating` model
- To run the model training, call `backend $ python manage.py ml_train`, this will run the [ml_train.py](backend/backend/management/commands/ml_train.py)
  * The script will save weights and plots to `backend/../.models/`
  * The script will use the [default config file](backend/backend/ml_model/config/featureless_config.gin) specified by `--config`
  * To run hyperparameter tuning with [ray tune](https://docs.ray.io/en/latest/tune/index.html), add the `--tune` option and use a corresponding config file, such as
    [featureless_config_hparam_search.gin](backend/backend/ml_model/config/featureless_config_hparam_search.gin).
    The file will generate TensorBoard logs and best/worst predictions in `~/ray_results`.
- There are 2 frameworks used in the project:
  * Embedding model. Uses the `Video.embedding` field in order to represent a video
  * **(now used)** [Featureless model](https://www.overleaf.com/project/5f44dd8e84c8540001bf1552).
    For each video and each expert, there is a variable
- Code structure for the ML models, see [backend/backend/ml_model](backend/backend/ml_model)
  1. [preference_aggregation.py](backend/backend/ml_model/preference_aggregation.py) defines the abstract preference aggregation model without application to Tournesol
     - Constructor creates the model, `fit()` trains it, `__call__()` is for prediction.
     - `MedianPreferenceAggregator` takes outputs of many models and computes the median
     - [preference_aggregation_featureless.py](backend/backend/ml_model/preference_aggregation_featureless.py) Featureless implementation
       - `VariableIndexLayer` defines the Keras layer with a variable which takes indices as inputs and outputs `variable[index]`
       - `AllRatingsWithCommon` defines the wrapper around `VariableIndexLayer` with user-friendly access (indices are converted into names and vice-versa), as well as checkpointing
       - `FeaturelessPreferenceLearningModel` defines a wrapper around `AllRatingsWithCommon` which implements prediction for a particular user, and ratings storage
       - `FeaturelessMedianPreferenceAverageRegularizationAggregator` implements the losses, minibatch computation and the plotting of losses
     - [preference_aggregation_with_embeddings.py](backend/backend/ml_model/preference_aggregation_with_embeddings.py) Embedding implementation
  2. [client_server/database_learner.py](backend/backend/ml_model/client_server/database_learner.py) Abstract class to load data to and from the database into the Preference Aggregation model
     - Constructor loads data, the `fit()` method trains the model, `update_features()` saves results. `load()` and `save()` are for checkpointing
     - [django_ml_featureless.py](backend/backend/ml_model/client_server/django_ml_featureless.py) Featureless implementation
     - [django_ml_embedding.py](backend/backend/ml_model/client_server/django_ml_embedding.py) Embedding implementation

<h4>Where to add online updates</h4>

The rough plan to add online updates would be to:
1. Create a `DatabasePreferenceLearnerFeatureless` as a global object inside the Django code (do once, it would take time)
2. Load current weights data from a checkpoint (do once, it would take time), use `.load()`
3. Load the ratings into the learner, use `.fit()` with `0` epochs
4. Do custom updates (write your own `tf.function` that will re-compute the weights)
5. Get the results and send via API

For quick development, you can use Jupyter notebooks (running by-default on port 8899 if started via [launch.sh](launch.sh))

</details>

## Directory structure

<details><summary>Click to expand</summary>

- notebooks -- research and development
- frontend -- react.js code
- backend -- django/tensorflow code
- backend/db.sqlite3 -- database with videos, preferences, ratings
- backend/api.py -- API definition
- backend/models.py -- Models definition. After updating, run `(venv) backend $ python manage.py makemigrations && python manage.py migrate`
- backend/ml_models.py -- Machine Learning part of the project (server definition included)
- backend/ml_client.py _trainr
- backend/preference_aggregation.py -- code to aggregate expert ratings
- backend/rating_fields.py -- video fields (rating)
- backend/video_search.py -- code to search for a video by name in Django database
- backend/add_videos.py -- code to import videos from YouTube
- backend/management - code to automate import/ml server tasks
- config -- server configuration files
- scripts -- server scripts

</details>

## Useful things
- Running the notebook to interface Django models
  `(venv) backend $ python manage.py shell_plus --notebook`
- Populate the database with videos: `notebooks/populate-database.ipynb` use Notebook with Django (as above)
- Show the PCA of all embeddings and other stats: `notebooks/video-database-stats.ipynb`

## Development workflow
- The `dev-server` branch contains code running at `dev.tournesol.app` and contains unmerged pull-requests
- The `master` branch contains tested code. `dev-server` gets merged into it when the pull-request gets merged
- Before commiting, use `tests.sh` to run tests 
- To run github action locally (useful to test dependencies installation as well), run `act -b --reuse` with [act](https://github.com/nektos/act)
- Integration tests produce videos of the format `integration_test_xxxx.avi`. A frame is grabbed each time an attribute is requested from a driver (this is a hacky a bit)
