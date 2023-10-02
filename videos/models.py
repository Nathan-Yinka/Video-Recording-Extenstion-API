from django.db import models
from rest_framework.reverse import reverse


# Create your models here.
class Video(models.Model):
    filename = models.CharField(max_length=255)
    video_data = models.BinaryField(blank=True,null= True)
    video_file_path = models.URLField(blank=True,null=True)
    completed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    transcript = models.TextField(null=True,blank=True)
    transcript_path =  models.URLField(blank=True,null=True)
    transcript_data = models.BinaryField(blank=True,null= True)
    
    

class VideoChunk(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='video_chunks')
    chunk_data_path = models.CharField(max_length=255)  # Path to the chunk data file
    chunk_index = models.IntegerField()  # Index of the chunk
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Chunk {self.chunk_index} of Video {self.video.id}"
    
    
