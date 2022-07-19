"""
Utils methods for Tournesol's core app
"""

from django.forms import ValidationError


def validate_avatar(fieldfile_obj, mb_limit=5):
    """Check avatar size.

    https://stackoverflow.com/questions/6195478/max-image-size-on-file-upload.
    """
    # print("VALIDATION", fieldfile_obj, fieldfile_obj.size)
    filesize = fieldfile_obj.size
    if filesize > mb_limit * 1024 * 1024:
        raise ValidationError({"avatar": f"Max file size is {mb_limit} MB"})
