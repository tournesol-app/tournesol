import logging.config
logging.config.fileConfig("tests/info.conf")

from solidago import *
poll = Poll.load("tests/test_poll")

rec = recommenders.ChronoFair()
rec.customize("alice", 100)
p = rec.preprocess(poll)

entities = recommenders.ChronoFair()(poll, 5, "alice", None, 100)