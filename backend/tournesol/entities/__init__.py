from .video import VideoEntity
from .candidate import CandidateEntity

ENTITY_CLASSES = [VideoEntity, CandidateEntity]

ENTITY_TYPE_CHOICES = [
    (VideoEntity.name, 'Video'),
    (CandidateEntity.name, 'Candidate (FR 2022)'),
]

ENTITY_TYPE_NAME_TO_CLASS = {
    k.name: k for k in ENTITY_CLASSES
}
