import logging

import gin
from jsonrpcserver import method, dispatch as dispatch, serve
from tornado import web


# Server for DatabasePreferenceLearner
class MainHandler(web.RequestHandler):
    """Server which handles the connections."""

    def post(self):
        request = self.request.body.decode()
        logging.info(f"Got a request {request}")
        response = dispatch(request)
        logging.info(f"Sending a response {response}")
        if response.wanted:
            self.write(str(response))
        else:
            logging.warning(f"Unknown request {request}")


@gin.configurable
def run_server(port=5000, learner=None):
    """Run server."""

    logging.info("Listening on port %d" % port)

    web.Application([(r"/", MainHandler)])
    run_server.learner = learner()

    @method
    def reload():
        """Refresh data from the database."""
        # loading data from database
        run_server.learner = learner()

    @method
    def fit(*args, **kwargs):
        """Fit the model."""
        reload()
        # loading data from database
        return run_server.learner.fit(*args, **kwargs)

    @method
    def call(*args, **kwargs):
        return [float(x) for x in run_server.learner(*args, **kwargs)]

    serve(port=port)
