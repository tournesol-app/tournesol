from solidago.functions.poll_function import PollFunction
from solidago.poll.poll_tables import User
from solidago.primitives.time import Date, DateInput


class CustomizablePollFunction(PollFunction):
    def __init__(self, receiver: User | None = None, date: DateInput | None = None):
        self.receiver = receiver
        self.date = None if date is None else Date(date)