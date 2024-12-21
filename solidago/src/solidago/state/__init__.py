""" This defines the class State, which contains all updatable information by the pipeline. """

from .base import State

from .users import Users
from .vouches import Vouches
from .entities import Entities
from .privacy import Privacy
from .judgments import Judgments
from .voting_rights import VotingRights
from .models import ScoringModel, DirectScoring, ScaledModel, PostProcessedModel, SquashedModel

