from jsonrpcclient.clients.http_client import HTTPClient
from multiprocessing import Process
from backend.rating_fields import VIDEO_FIELDS
import numpy as np
import pickle
from time import time


def time_cache_wrapper(f, expire_sec=3600):
    """Decorator which caches results for some seconds."""
    # format pickle(x) -> (compute_time, value)
    cache = {}

    def wrapper(*args):
        x_str = pickle.dumps(args)
        if x_str in cache:
            if time() - cache[x_str][0] <= expire_sec:
                return cache[x_str][1]
        result = f(*args)
        cache[x_str] = (time(), result)
        return result
    return wrapper


class DatabaseLearnerCommunicator(object):
    """Communicate with training/inference workers."""

    def __init__(
            self,
            port_inference=5000,
            port_training=5001,
            host='localhost'):
        """Initialize (remember ports)."""
        self.port_inference = port_inference
        self.port_training = port_training
        self.host = host

    def build_client(self, port):
        """Return an http client pointing to the worker."""
        return HTTPClient("http://%s:%d" % (self.host, port))

    @time_cache_wrapper
    def __call__(self, x):
        """Transform embedding into preferences."""
        try:
            client = self.build_client(port=self.port_inference)
            return client.call([float(t) for t in x]).data.result
        except Exception as e:
            print(e)
            return np.zeros(len(VIDEO_FIELDS))

    def fit(self):
        """Fit on data from the dataset."""
        def fit_helper():
            client = self.build_client(port=self.port_training)
            client.fit()

            client_inference = self.build_client(port=self.port_inference)
            client_inference.reload()

        Process(target=fit_helper).start()
