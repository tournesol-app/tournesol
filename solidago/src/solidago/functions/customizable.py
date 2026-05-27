from solidago.functions.poll_function import PollFunction
from solidago.poll.poll_tables import User
from solidago.primitives.time import Date, DateInput


class CustomizablePollFunction(PollFunction):
    def __init__(self, username: str | None = None, date: DateInput | None = None):
        self.username = username
        self.date = None if date is None else Date(date)