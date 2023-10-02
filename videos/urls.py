from django.urls import path
from . import views

urlpatterns = [
    path("",views.ListVideoView.as_view(),name="list-videos"),
    path("start/",views.StartVideoView.as_view(),name="start-video"),
    path("<int:pk>/",views.ListVideoView.as_view(),name="stream-video"),
    
    
    path("transcript/<int:pk>/",views.ListVideoTranscriptView.as_view(),name="video-transcript"),
    path("transcript/",views.ListVideoTranscriptView.as_view(),name="video-transcripts"),
    
    
    path("chunks/<int:pk>/",views.VideoChunkView.as_view(),name='send-chunk'),
    
    path("combine/<int:pk>/",views.VideoCombineView.as_view()),
    path('concatenate/<int:video_id>/', views.ConcatenateVideoView.as_view(), name='concatenate_video'),
    
    # test script for the blob data
    path("home/",views.home,name="test-script"),
]
