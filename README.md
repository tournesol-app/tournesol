# 🌻🌻🌻 Tournesol: Collaborative Content Recommendations
![Continuous Integration](https://github.com/tournesol-app/tournesol/workflows/Continuous%20Integration/badge.svg?branch=master)

This repository hosts the code of the platform 🌻[Tournesol.app](https://tournesol.app). See the wiki page [Contribute to Tournesol](https://wiki.tournesol.app/index.php/Contribute_to_Tournesol) for details.

![Home page of Tournesol.app](https://user-images.githubusercontent.com/10453308/115123905-9b6b4300-9fbf-11eb-8853-25552d13f7b0.png)

We use [TensorFlow](http://tensorflow.org/) to compute the aggregated scores,
[Django](https://www.djangoproject.com/) for the backend, and [React.js](https://reactjs.org/) for the front-end.

![image](https://user-images.githubusercontent.com/1012270/119049451-13a69900-b9b0-11eb-807f-25f2455f3d05.png)

## Development workflow
To contribute to the code base, you will need basic knowledge of the [Linux command line](https://ubuntu.com/tutorials/command-line-for-beginners#1-overview), [Git](https://product.hubspot.com/blog/git-and-github-tutorial-for-beginners) (specifically, branches) and GitHub [Pull Requests](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests).

❓ If unsure what to do, ask on [Discord](https://discord.gg/ajJYCsnQ).

- All development is done locally on developers' machines
- The `master` branch contains code that can be run without any tweaks or modifications. This branch is protected against direct commits. Each change needs to be done in a separate branch, which is then used in a Pull Request (PR). The PR needs to pass automated tests (Github Continuous Integration/CI), as well as a review from one of the members of the 🇨🇭[Tournesol Association](https://wiki.tournesol.app/index.php/Tournesol_Association).
- To run tests locally, run `$ ./tests.sh` (does the same as Github CI)

<details>
  <summary>⚙ <b>Setting up your development environment on your computer</b> (click to expand)</summary>
  
### Tested platforms  
**Docker setup on Ubuntu, Debian, Windows 10, Mac OS X, Mac OS X with the M1 chip**
    
For expert use without Docker, the setup was tested on WSL 2 from Windows 10 Preview (no Docker), Debian GNU/Linux 10 (buster) (no Docker), Ubuntu 20.04 and 18.04 (no Docker). Mac OS X setup without Docker is more complicated, as an X server is required for integration tests, as well as some linux-specific dependencies.

### Building the Docker image
First, clone this repo and `cd` to it.
You will need [Docker](https://docs.docker.com/get-docker/) installed and configured.
The final image size (`docker image ls`) is about 4GB, but during the installation it might take more space. The build takes about 9 minutes with a 1 GBit/sec Internet connection, during which it downloads 1.3GB.
  
**Notes on the Docker image:**
  1. Please make sure that the image has at least 4 GB of RAM
  2. On Macs with the [M1 chip](https://docs.docker.com/docker-for-mac/apple-silicon/), you will need to use the [`buildx` command](https://blog.jaimyn.dev/how-to-build-multi-architecture-docker-images-on-an-m1-mac/) for Docker with an architecture `linux/amd64`. The native M1 architecture currently does not have all of the Python dependencies used in the project.

  
**Building the image**
1. Inside the repository, run `sudo docker build -t tournesol-app/tournesol docker`
2. Run the container with `sudo docker run -p 8000:8000 -p 8899:8899 -p 5900:5900 -p 2222:22 -it tournesol-app/tournesol`. Running this command will create a new container with the same image every time. See below how to re-use a container. The `8000` port exposes the web server, the `8899` port exposes the jupyter notebook, `5900` is for VNC, and `2222` for ssh.
3. The container will print your SSH public key, like in the image below:
   
   ![image](https://user-images.githubusercontent.com/1012270/119053322-7189af80-b9b5-11eb-82e0-eb1f937451d2.png)
  
   Copy the ssh-rsa line (up until and including root@...) to your [GitHub account](https://github.com/settings/keys).
4. To run the same container again, remember the host name of the container (`root@xxx`) and run
   `sudo docker start -ai xxx`
5. If you are re-using one Docker image to work on multiple issues, you might need to `git pull` the recent changes. You might additionally need to install npm or python packages. If something doesn't work, you might want to consider re-builing the Docker image with `sudo docker build --no-cache -t tournesol-app/tournesol docker`. The `--no-cache` will disable re-using the image you have built before.

To edit Tournesol source code, start the container and connect via ssh to port 2222 (set up your password, or the public key via the container terminal).
The default root password is `tournesol`.


<h3>Building front-end</h3>

The code in the [frontend/](frontend/) folder needs to be bundled into a single `main.js` file that is then served to the browser of a visitor. This is called _building_. By-default, the Docker image builds front-end on the first run. If you make changes to the front-end code, you will need to re-build the `main.js`. The example below will _watch_ for any changes you make to the front-end code and re-build the `main.js` file automatically each time. Note that you need to refresh the page in your browser (Ctrl+R), or even do a [full refresh](https://www.getfilecloud.com/blog/2015/03/tech-tip-how-to-do-hard-refresh-in-browsers/) in order to see your changes, as the browser will not reload the `main.js` file automatically.

```shell
$ cd frontend
frontend $ npm run dev
```
  
To run this in background, you can use the [screen tool](https://linuxize.com/post/how-to-use-linux-screen/) already installed in the Docker image. The example below would start a `screen` with a name "npm_run_dev" in detached (background) mode, and it will run the command `npm run dev`:
```shell
frontend $ screen -Sdm "npm_run_dev" npm run dev
```

<h3>Running back-end</h3>

Run inside the container to launch the server, and the jupyter notebook:

```shell
(venv-tournesol) $ ./launch_debug.sh
```

Now you can navigate to http://127.0.0.1:8000 to view the development website, and to http://127.0.0.1:8899 to view the Jupyter notebook. The Django [admin site](https://docs.djangoproject.com/en/3.2/intro/tutorial07/) can be accessed at http://127.0.0.1:8000/admin/.

To run all tests, do
```shell
(venv-tournesol) $ ./tests.sh
```

Note that the backend needs to be started in a special mode for integration tests, so please close the previous one if you started it (see `screen -ls` and close the backend_server screen).
To see the Jupyter token, run `jupyter notebook list` inside the container.
When running integration tests, you can connect to 127.0.0.1 via VNC (port 5900) to see Firefox

Auxiliary commands:

```shell
# cd backend
  
# Create a user for yourself
# Note that creating a super user is highly recommended for testing the website locally and contributing to the codebase
(venv-tournesol) backend $ python manage.py createsuperuser 

# (optional) create the test database
(venv-tournesol) backend $ python manage.py migrate

# (optional) run training
(venv-tournesol) backend $ python manage.py ml_train

# to set env vars, done automatically in Docker
(venv-tournesol) $ . ./debug_export.sh
```  

<h3>Filling in the database</h3>
Sometimes, it is useful to have data in the backend to perform development, for example, it is useful to have videos to develop the Rate Later page. Currently, you can either add this data manually (using the website), or fill it in automatically using Django shell. Examples can be found in <a href="https://github.com/tournesol-app/tournesol/blob/f5000e3c85b4384c22afe2ca7ac62ec46898ccb2/integration_test/test_public_database.py#L16">integration</a> and <a href="https://github.com/tournesol-app/tournesol/blob/f5000e3c85b4384c22afe2ca7ac62ec46898ccb2/backend/backend/tests/test_api_v2.py#L707">backend</a> tests.

<h3>Editing the code</h3>
Several options are available to edit the code on the docker container. See the remote ssh connection details above.

- [Vim](https://en.wikipedia.org/wiki/Vim_(text_editor)) is pre-installed in the container. You can open a file in vim directly from the container terminal without any additional setup.
- [PyCharm](https://www.jetbrains.com/pycharm/) supports remote editing out-of-the box.
- [VSCode](https://code.visualstudio.com/). The [`remote-ssh`](https://code.visualstudio.com/docs/remote/ssh) extension can be used.

</details>

<details>
  <summary>⁉ The tests have failed and I don't know why (click to expand)</summary>
  
- Note that Python and JavaScript [linters](https://en.wikipedia.org/wiki/Lint_(software)) are enabled, which check for the correct numbers of white-spaces, double-vs-single quotes etc.
  
- Sometimes tests fail for a wrong reason -- either the tests themselves have bugs, or the GitHub infrastrucure is faulty (the script sometimes can't connect to Ubuntu APT repositories). If the error message is cryptic and unrelated to your changes, try re-running the tests.

- You can see the output of the automated tests on GitHub CI if you click on details (see the image below). Wait for the page to load and scroll down to the last line. It usually contains a description of what went wrong:

![image](https://user-images.githubusercontent.com/1012270/119043773-f28e7a00-b9a8-11eb-9f03-33352c2da6c8.png)
</details>

<details>
  <summary>Frequently asked questions</summary>
  
- Quality features are defined in [rating_fields.py](backend/backend/rating_fields.py), and the front-end counterpart [constants.js](frontend/src/constants.js) is generated from backend via running `python manage.py js_constants --file ../frontend/src/constants.js`.
- To re-generate API code and documentation, run `tournesol $ ./update_api.sh`
- The main React file is in [frontend/src/index.js](frontend/src/index.js)
- The template for the website layout (menu, top bar, ...) is defined in [frontend/src/components/App.js](frontend/src/components/App.js)
- Other React components: [Home page](frontend/src/components/Home.js), [Routes](frontend/src/components/Router.js), [Video information component](frontend/src/components/VideoCard.js), [Search page](frontend/src/components/UserInterface/index.js), [Rate page](frontend/src/components/ExpertInterface/index.js)
- Other back-end files: [Django settings](backend/django_react/settings.py), [backend routes](backend/frontend/urls.py), [main template for React](backend/frontend/templates/frontend/index.html), [database models](master/backend/backend/models.py), [backend views](backend/frontend/views.py), [database export](backend/backend/management/get_all_dataframes.py), [the train command code](backend/backend/management/commands/ml_train.py)
- For the description of the API, see the section "Tournesol API" below
- For the description of the ML model, see the section "Machine Learning model" below
  
</details>

## Tournesol API
<details>
  <summary>Click to expand</summary>

API is implemented in [Django-REST](https://www.django-rest-framework.org/) using [Spectacular](https://github.com/tfranzel/drf-spectacular) for annotations compliany with [OpenAPI 3.0](https://swagger.io/specification/):

* API is defined in [api_v2](backend/backend/api_v2), and it has a developer-friendly webpage running at [api/v2/](https://tournesol.app/api/v2/).
* The [OpenAPI 3](https://swagger.io/specification/) schema is available in [schema.json](backend/schema.json), [schema.yaml](backend/schema.yaml)
  and at [/schema/](https://tournesol.app/schema/)
* Auto-generated documentation is available as well:
  - Via Swagger: [/schema/swagger-ui/](https://tournesol.app/schema/swagger-ui/)
  - Via ReDoc: [/schema/redoc/](https://tournesol.app/schema/redoc/)
  
</details>

### Machine Learning model

<details>
  <summary>Click to expand</summary>

- The quality criteria fields (`reliability`, ...) are described in [rating_fields.py](backend/backend/rating_fields.py).
- The ML model transforms contributor's pairwise comparisons from the [`ExpertRating`](backend/backend/models.py) model into aggregated scores for each `Video`. Per-expert scores are written to the `VideoRating` model
- To run the model training, call `backend $ python manage.py ml_train`, this will run the [ml_train.py](backend/backend/management/commands/ml_train.py)
  * The script will save weights and plots to `backend/../.models/`. They can be accessed via the website at http://127.0.0.1:8000/files/ (superuser access is required)
  * The script will use the [default config file](backend/backend/ml_model/config/featureless_config.gin) specified by `--config`
  * To run hyperparameter tuning with [ray tune](https://docs.ray.io/en/latest/tune/index.html), add the `--tune` option and use a corresponding config file, such as
    [featureless_config_hparam_search.gin](backend/backend/ml_model/config/featureless_config_hparam_search.gin).
    The file will generate TensorBoard logs and best/worst predictions in `~/ray_results`.
- We use a ["featureless" model](https://www.overleaf.com/project/5f44dd8e84c8540001bf1552). For each video, each contributor and each quality criterion, there is a scalar variable. The variables are stored together in a 1D tensor with a dictionary coding for indices.
- Code structure for the ML models, see [backend/backend/ml_model](backend/backend/ml_model)
  1. [preference_aggregation.py](backend/backend/ml_model/preference_aggregation.py) defines the abstract preference aggregation model without application to Tournesol
     - Constructor creates the model, `fit()` trains it, `__call__()` is for prediction.
     - [preference_aggregation_featureless.py](backend/backend/ml_model/preference_aggregation_featureless.py) implements the Featureless model:
       - `AllRatingsWithCommon` defines the wrapper around the tensor with the data with user-friendly access (indices are converted into names and vice-versa), as well as with checkpointing
       - `FeaturelessPreferenceLearningModel` defines a wrapper around `AllRatingsWithCommon` which implements prediction for a particular user, and ratings storage
       - `FeaturelessMedianPreferenceAverageRegularizationAggregator` implements the losses, minibatch computation and the plotting of losses
     - [preference_aggregation_featureless_tf_sparse.py](backend/backend/ml_model/preference_aggregation_featureless_tf_sparse.py) defines the loss function currently used in the project. It uses a sparse tensor for aggregated and per-contributor scores.
     - [preference_aggregation_featureless_online.py](backend/backend/ml_model/preference_aggregation_featureless_online.py) defines the Online Updates model which uses the [Golden Ratio Search](https://en.wikipedia.org/wiki/Golden-section_search) with a small mini-batch of data. It is used on the website for the case when a rating is changed in the Video Details page to immediately update the video scores.
  2. [client_server/database_learner.py](backend/backend/ml_model/client_server/database_learner.py) Abstract class to load data to and from the database into the Preference Aggregation model
     - Constructor loads data, the `fit()` method trains the model, `update_features()` saves results. `load()` and `save()` are for checkpointing
     - [django_ml_featureless.py](backend/backend/ml_model/client_server/django_ml_featureless.py) Featureless implementation
  
For quick development, you can use Jupyter notebooks (see above for ports and launch instructions)

</details>

## Code documentation
- Backend documentation (Sphinx): [backend/doc/build/html/index.html](backend/doc/build/html/index.html)
- Re-generate by running `make`.

## Updating the website
Website is updated manually, please write on Discord if you want the changes from your merged Pull Request to appear on the website. First, the [staging](https://staging.tournesol.app/) version is updated, and only then the [main one](https://tournesol.app/).
