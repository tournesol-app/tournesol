from solidago.poll.poll import Poll
from solidago.functions.filtering.filtering import Filtering
from solidago.functions.poll_function import PollFunction


class PositiveVotingRightOnly(PollFunction):
    def __init__(self, username: str | None = None, column: str = "voting_right"):
        self.column = column
        self.username = username

    def fn(self, poll: Poll) -> Poll:
        voting_rights = poll.voting_rights\
            .add_columns(positive=poll.voting_rights(self.column) > 0)\
            .filters(positive=True)
        usernames = set(voting_rights("username"))
        if self.username is not None:
            usernames.add(self.username)
        return Filtering(usernames)(poll)