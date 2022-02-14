from .video import VideoEntity

ENTITY_CLASSES = [VideoEntity]

ENTITY_TYPE_CHOICES = [
    (VideoEntity.name, 'Video'),
]

ENTITY_TYPE_NAME_TO_CLASS = {
    k.name: k for k in ENTITY_CLASSES
}
