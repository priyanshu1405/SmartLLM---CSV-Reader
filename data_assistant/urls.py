from django.urls import path
from .views import CSVUploadView
from data_assistant.views import upload_view
from .views import upload_view, ask_question_view, clear_chat

urlpatterns = [
    path('upload/', upload_view, name='upload'),  # if you want this route
    path('upload/', CSVUploadView.as_view(), name='api-upload'),  # if this is the upload API
    path('ask/', ask_question_view, name='api-ask'),
    path('clear_chat/', clear_chat, name='clear_chat'),
]