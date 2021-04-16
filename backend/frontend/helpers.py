from annoying.functions import get_object_or_None


def get_id_or_m1(*args, **kwargs):
    """Get ID of an object or -1. Exception if 2 objects are found."""
    obj = get_object_or_None(*args, **kwargs)
    if obj is None:
        return -1
    else:
        return obj.id


def get_user_id_or_m1(request):
    """Get DjangoUser ID or -1."""
    if not hasattr(request, 'user'):
        return -1
    if not hasattr(request.user, 'id'):
        return -1
    if request.user.id is None:
        return -1
    return int(request.user.id)
