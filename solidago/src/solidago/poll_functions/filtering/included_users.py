from solidago.poll.poll import Poll
from solidago.poll_functions.filtering.filtering import Filtering
from solidago.poll_functions.poll_function import PollFunction


class IncludedUsersOnly(PollFunction):
    def __init__(self, column: str = "included"):
        self.column = column

    def fn(self, poll: Poll) -> Poll:
        usernames = {u.name for u in poll.users if u[self.column]}
        return Filtering(usernames)(poll)