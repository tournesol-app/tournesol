Tournesol ML algorithm
===

Calculating video scores from users' comparisons.


# Utilisation

* install the ml requirements ``pip install -r ml/ml_requirements.txt``

## Production mode

* Define hyperparameters in hyperparameters.gin.

* Use the training command to train and save results in database
``python manage.py ml_train``

## Development mode

* Set ENV variable TOURNESOL_DEV to 1.

* Define hyperparameters in hyperparameters.gin.

* Edit dev/experiments.py run_experiment() to choose input data and output prints.

* Use the dev training command to run dev.experiments.run_experiment
``python manage.py ml_train_dev``

→ You will get some plots in ml/plots/

# Organisation

* dev/ contains modules unused in production.

* management/commands/ contains ml_train.py and ml_train_dev.py, which are the two Django command modules, one for production and one for dev

* ml_train.py contains fetch_data() and save_data(), which are respectively used to get data from the database and to save it back after training.

* ML testing module is tests/ml_tests.py. It contains mainly unit tests and can be called using pytest.
``python -m pytest ml/tests/ml_tests.py``

## The other production modules are directly in ml/

* The output of fetch_data() is to be used through core.ml_run(), which both trains (according to hyperparameters defined in hyperparameters.gin) and outputs resulting video scores (both global and local).

* handle_data.py uses data_utility.py and provides functions used in core.py to shape data to required format before and after training.

* In between lies the training structure: the Licchavi() class in licchavi.py. The Licchavi class provides the methods set_allnodes(), load_and_update(), output_scores(), save_models() and train() which are called during ml_run().
core.ml_run() creates a Licchavi object and initializes it with the input data (users' comparisons) using set_allnodes() or load_and_update(), then it trains using train(), and finally outputs using output_scores(). It can optionally save the training status with save_models() to resume later from it.

* Licchavi objects store the distributed data inside a dictionary of Node() objects. The Node class is defined in nodes.py.<br />
A Node() contains all user data needed (comparisons, local model, local s parameter, ...).<br />
Apart from the nodes, a Licchavi object contains a global model for global scores and a history of training monitoring metrics.

* During training, Licchavi.train() calls functions from losses.py and metrics.py.<br />
The training phase consists in a parameterizable (in hyperparameters.gin) number of epochs. Each epoch is divided in a local step (fitting step), during which all training data is used and a global step, using no input data. The first is an iteration of gradient descent on local parameters, and the second an iteration on global parameters.<br />
The gradient descent is done wrt the comparison-Licchavi loss (see paper).

## The other development modules are in ml/dev/

* experiments.py is used to customize what we want to test, it is made to be edited.

* fake_data.py is used to generate artificial data using random "realistic" distributions. It allows to have "ground truths" to check the quality of the ml algorithm.

* licchavi_dev.py defines LicchaviDev(Licchavi) class allowing, inter alia, to use ground truths of generated data to compute an "error" metric.

* ml_benchmark.py is meant to test the time taken by the different parts of the code, it isn't very developed for now.

* plots.py is used to save plots in ml/plots/ at the end of training. Plots are describing the training history or the result repartition.

* visualisation.py is a bunch of utility functions to be used mainly directly in experiments.py or calling plot.py module.

# Notations:
- node = user : contributor
- vid = vID : video, video ID
- rating : rating provided by a contributor between 2 videos, in [-10,10] or [-1,1]
- score : score of a video outputted by the algorithm
- glob, loc : global, local
- idx, vidx : index, video index
- l_something : list of something
- arr : numpy array
- tens : torch tensor
- dic : dictionary
- verb : verbosity level
- VARIABLE_NAME : global variable
