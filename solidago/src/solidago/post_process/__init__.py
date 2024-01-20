""" Step 6 of the pipeline.
    
Post-process modifies the user and global models, typically with the goal
of yielding more human-readible scores.
"""

from .base import PostProcess
from .squash import Squash
