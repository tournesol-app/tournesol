import random
import string


def generate_youtube_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=11))
