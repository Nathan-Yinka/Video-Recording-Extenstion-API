from rest_framework import serializers
from .models import Video,VideoChunk


class VideoSerializer(serializers.ModelSerializer):
    video_url = serializers.HyperlinkedIdentityField(view_name="stream-video",lookup_field="pk")
    class Meta:
        model = Video
        exclude = ['video_data',"video_file_path","transcript_path", "transcript_data"]
        
class VideoTrannscriptSerializer(serializers.ModelSerializer):
    transcript_url = serializers.HyperlinkedIdentityField(view_name="video-transcript",lookup_field="pk")
    class Meta:
        model = Video
        fields = ["id","transcript","transcript_url"]
        
class VideoChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoChunk
        fields = "__all__"