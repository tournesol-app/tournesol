import logging.config
logging.config.fileConfig("tests/info.conf")

from solidago import *
poll = Poll.load("tests/test_poll")

recommenders.ChronoFair()(poll, 5, "alice", None, 100)
