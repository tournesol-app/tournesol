from backend.models import Video
from rest_framework import serializers


class VideoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Video
        fields = ['video_id']
