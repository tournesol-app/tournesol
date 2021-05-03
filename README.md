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
You will need [Docker](https://docs.docker.com/get-docker/) installed and configured.

<h3>Building the Docker image</h3>

The final image size (`docker image ls`) is about 4GB, but during the installation it might take more space.

1. Inside the repository, run `sudo docker build -t tournesol-app/tournesol docker`
2. At the end, the script will print the ssh certificate, like
   ```
=== Your ssh public key... ===
ssh-rsa ...
=== /public key
   ```
   Copy the ssh-rsa line to your [GitHub account](https://github.com/settings/keys).
3. Run the container with `sudo docker run -p 8000:8000 -p 8899:8899 -p 5900:5900 -it tournesol-app/tournesol`.
   The `8000` port exposes the web server, the `8899` port exposes the jupyter notebook, and `5900` is for VNC.
4. To run the same container again, remember the host name of the container (`root@xxx`) and run
   `sudo docker start -ai xxx`


<h3>Building front-end</h3>

Run inside the container (`npm run build` runs on image build):

```
$ cd frontend

# will watch for changes made to the frontend source code and re-build automatically:
frontend $ npm run dev
```

<h3>Running back-end</h3>

Run inside the container to launch the server, and the jupyter notebook:


```
(venv-tournesol) $ ./launch_debug.sh
```

Now you can navigate to http://127.0.0.1:8000 to view the development website, and to http://127.0.0.1:8899 to view the Jupyter notebook

When running integration tests, you can connect to 127.0.0.1 via VNC (port 5900) to see Firefox

Auxiliary commands:

```
(venv-tournesol) $ . ./debug_export.sh # to set env vars, done automatically in Docker
# cd backend

# create the test database
(venv-tournesol) backend $ python manage.py migrate

# (optional) run training
(venv-tournesol) backend $ python manage.py ml_train

# (optional) download latest video metadata
(venv-tournesol) backend $ python manage.py add_videos

# optional: create a user for yourself
(venv-tournesol) backend $ python manage.py createsuperuser
```



Note that creating a super user is highly recommended for testing the website locally and contributing to the codebase. 💯

<h3>Connecting to the website</h3>


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
