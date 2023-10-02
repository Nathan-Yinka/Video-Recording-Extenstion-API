import mimetypes
import os
import tempfile
from rest_framework.reverse import reverse

from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from moviepy.editor import VideoFileClip, clips_array, concatenate_videoclips
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Video, VideoChunk
from .serializers import (VideoChunkSerializer, VideoSerializer,
                          VideoTrannscriptSerializer)

import os
import tempfile

from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import VideoChunk  # Import your VideoChunk model here
from .models import Video
from .serializers import VideoChunkSerializer
import io
import os
import subprocess
import tempfile

from django.conf import settings
from django.http import HttpResponse, StreamingHttpResponse
from django.views import View
from moviepy.editor import VideoFileClip, clips_array
import os
import subprocess

from django.http import FileResponse, HttpResponse
from django.views import View
from io import BytesIO

# gettig the transipt
import openai



# Create your views here.
# view to start the record, it create a video file in the database which takes serveral chunks togther
class StartVideoView(generics.CreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    
    def save_video_to_file(self,video_id, filename):
        file_extension = ".mp4"  # Change this to the appropriate file extension
        # Concatenate the extra data to the filename
        temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension, dir=settings.MEDIA_ROOT, prefix=f"{filename}_video{video_id}_")
        temp_video_path = temp_video_file.name
        temp_video_file.close()
        return temp_video_path
    
    def post(self, request):
        data = request.data
        filename = data.get("filename")
        if filename:
            video=Video.objects.create(filename=filename)
            
            chunk_data_filename = self.save_video_to_file(video.id,filename)
            video.video_file_path = chunk_data_filename
            video.filename = f'{filename}{video.id}'
            video.save()
            
            serializer = self.get_serializer(video)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        
        return Response({"error":"file name is required"})
    
class ListVideoView(APIView):
    def get (self ,request,pk=None):
        if pk is not None:
            video = Video.objects.get(id=pk)
            
            file_path = video.video_file_path  # Replace with your actual attribute

            response = HttpResponse(video.video_data, content_type='video/webm') 
            return response
        
        videos = Video.objects.all().order_by('-created')
        serializer = VideoSerializer(videos,many=True,context={'request': request})
        
        return Response(serializer.data,status=status.HTTP_200_OK)


class ListVideoTranscriptView(APIView):
    def get (self ,request,pk=None):
        if pk is not None:
            video = Video.objects.get(id=pk)
            
            file_path = video.video_file_path  # Replace with your actual attribute

            response = HttpResponse(video.transcript_data, content_type='text') 
            return response
        
        videos = Video.objects.all().order_by('-created')
        serializer = VideoTrannscriptSerializer(videos,many=True,context={'request': request})
        
        return Response(serializer.data,status=status.HTTP_200_OK)
    



class VideoChunkView(APIView):
    
    def save_chunk_to_file(self, video_binary, chunk_index):
        file_extension = ".mp4"  # Change this to the appropriate file extension
        temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension, dir=settings.MEDIA_ROOT)
        temp_video_file.write(video_binary)
        temp_video_path = temp_video_file.name
        temp_video_file.close()
        
        return temp_video_path

    def post(self, request, pk):
        data = request.data
        video_file = data.get("file")
        chunk_index = data.get("chunk_index")
        
        if not video_file or chunk_index is None:
            response = {
                "status": "error",
                "message": "Both video chunk and chunk index are required.",
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            video = Video.objects.get(id=pk)  # Retrieve the Video instance (You should replace 'Video' with your actual model name)
            video_binary = video_file.read()
            
            if video_binary:
                video_binary = str(video_binary)
                if video.video_data:
                    video_binary_bytes = str(video_binary)
                    video.video_data += video_binary_bytes
                else:
                    video.video_data = video_binary
                
                video.save()
                # Save the chunk data to a file with chunk index
                chunk_data_filename = self.save_chunk_to_file(video_binary, chunk_index)
                
                # Create and save VideoChunk instance with the file path and index
                chunk = VideoChunk.objects.create(video=video, chunk_data_path=chunk_data_filename, chunk_index=chunk_index)
                chunk.save()
                
                
                upload_path =video.video_file_path
                
                with open(upload_path, 'ab') as temp_file:
                    temp_file.write(video_binary)

                response = {
                    "status": "success",
                    "message": "Video chunk uploaded successfully",
                    "chunk_id": chunk.id
                }
                
                return Response(response, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Handle errors here
            response = {
                "status": "error",
                "message": "Error uploading video chunk.",
                "data": str(e)
            }
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # getting the audio in the file if the chunks as been sent totally
        video = Video.objects.get(id=pk)
        video_clip = VideoFileClip(video.video_file_path)
        audio_clip = video_clip.audio
        
        if video_clip.audio:
                # Create a temporary file to store the audio
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav",dir=settings.MEDIA_ROOT) as audio_temp_file:
                    audio_temp_file_path = audio_temp_file.name
                    # Write the audio to the temporary file
                    audio_clip = video_clip.audio
                    audio_clip.write_audiofile(audio_temp_file_path)
                    
                    
                    
                    transcript = transcribe_audio(audio_temp_file_path)
                    if transcript:    
                            
                        video.transcript = transcript
                        transcript_bytes = transcript.encode('utf-8')
                        video.transcript_data = transcript_bytes
                        video.completed = True
                        video.save()
                        
                        def get_absolute_url():
                            request = self.request
                            return reverse('stream-video', args=[pk],request=request)
                    if transcript:
                        data = {
                            "successful":True,
                            "transcript": True,
                            "url":get_absolute_url()
                            }

        return Response(data or {"success":True}, status=status.HTTP_200_OK)
            
    
    def get(self, request, pk):
        chunk_id = pk
        
        if chunk_id is not None:
            chunk = VideoChunk.objects.get(id=chunk_id)
            
            with open(chunk.chunk_data_path, 'rb') as chunk_data_file:
                response = HttpResponse(chunk_data_file.read(), content_type='video/mp4')
            
            return response
        return Response(
            {"status": "error", "message": "Chunk ID parameter is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

def transcribe_audio(audio_file_path, chunk_size=20000000):
    try:
        # Set your OpenAI API key
        api_key = "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"

        # Initialize the OpenAI API client
        openai.api_key = api_key

        # Initialize an empty transcript
        transcript = ""

        # Open the audio file in binary read mode
        with open(audio_file_path, "rb") as audio_file:
                # Read a 5MB chunk of the audio file
                chunk = audio_file.read(chunk_size)
                
                # If the chunk is empty, we've reached the end of the file
                if not chunk:
                    return ""

                # Wrap the chunk in a BytesIO object with a name attribute
                chunk_file = BytesIO(chunk)
                chunk_file.name = "audio_chunk.wav"

                # Call the Whisper ASR API to transcribe the chunk
                response = openai.Audio.transcribe("whisper-1", chunk_file)

                # Append the transcript for this chunk to the overall transcript
                

        return response.text
    except Exception as e:
        return ""




# view that takes the chunks from chrome and create it togther  
# class VideoChunkView(APIView):
    
#     def post(self, request,pk):
#         data = request.data
#         video_file = data.get("file")
        
#         if not (video_file):
#             response = {
#                 "status": "error",
#                 "message": "Both video ID and blob video are required.",
#             }
#             return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             video = Video.objects.get(id=pk)  # Retrieve the Video instance
#             video_binary = video_file.read()
#             if video_binary:
#                 chunk = VideoChunk.objects.create(video=video, chunk_data=video_binary)
#                 chunk.save()

#                 # Serialize the chunk data
#                 serializer = VideoChunkSerializer(chunk)

#                 response = {
#                     "status": "success",
#                     "message": "Video uploaded successfully",
#                     "data": serializer.data
#                 }
            
#         except Exception as e:
#             # Handle errors here
#             response = {
#                 "status": "error",
#                 "message": "Error uploading video chunks.",
#                 "data": str(e)
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response(response, status=status.HTTP_201_CREATED)
    
#     def get(self,request,pk):
#         chunk = VideoChunk.objects.get(id=pk)
#         response = HttpResponse(chunk.chunk_data, content_type='video/webm') 
#         return response
    



class VideoCombineView(View):
    
    def get(self, request, pk):
        try:
            # Retrieve the Video object with the given primary key (pk)
            video = Video.objects.get(id=pk)

            # Retrieve related video chunks (if using ForeignKey or ManyToManyField)
            chunk_list = video.video_chunk.all()

            # Create a list to store binary video data
            video_data_list = [chunk.chunk_data for chunk in chunk_list]

            # Create a list to store temporary video file paths
            temp_video_files = []

            try:
                # Create temporary video files and write binary data to them
                for idx, video_data in enumerate(video_data_list):
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                    temp_file.write(video_data)  # Read and write binary data
                    temp_file.close()
                    temp_video_files.append(temp_file.name)

                # Load the videos
                video_clips = [VideoFileClip(path) for path in temp_video_files]

                # Concatenate the videos sequentially
                final_video = concatenate_videoclips(video_clips, method="compose")

                response = HttpResponse(content_type="video/mp4")
                output_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

                # Write the combined video to the output file
                final_video.write_videofile(output_file_path, codec="libx264")

                # Open and read the output video file
                with open(output_file_path, 'rb') as video_file:
                    response.write(video_file.read())

                # Delete the temporary output file
                os.remove(output_file_path)

                return response

            finally:
                # Clean up temporary video files
                for temp_file_path in temp_video_files:
                    os.unlink(temp_file_path)

        except Video.DoesNotExist:
            return Response({"detail": "Video not found"}, status=404)

class ConcatenateVideoView(View):
    def get(self, request, video_id):
        try:
            # Query the database to retrieve the chunk paths associated with the specified video
            chunk_files = VideoChunk.objects.filter(video_id=video_id).values_list('chunk_data_path', flat=True)

            if not chunk_files:
                return HttpResponse('No chunk files found for the specified video', status=404)

            # Create a temporary directory for concatenated video
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            os.makedirs(temp_dir, exist_ok=True)

            # Concatenate the video chunks using FFmpeg
            output_path = os.path.join(temp_dir, 'concatenated.mp4')
            concat_command = [
                'ffmpeg',
                '-f', 'concat', '-safe', '0', '-i', 'concat.txt',
                '-c', 'copy', output_path,
            ]

            with open('concat.txt', 'w') as concat_file:
                for chunk_file in chunk_files:
                    concat_file.write(f"file '{chunk_file}'\n")

            subprocess.run(concat_command)

            # Return the concatenated video file as a response
            with open(output_path, 'rb') as video_file:
                response = FileResponse(video_file, content_type='video/mp4')
                response['Content-Disposition'] = 'attachment; filename="concatenated.mp4"'
                return response

        except Exception as e:
            return HttpResponse(f'Error: {str(e)}', status=500)
        


# tester
def home(request):
    return render(request,'index.html',{})