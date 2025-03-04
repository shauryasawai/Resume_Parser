from django.urls import path
from .views import upload_resume_and_send

urlpatterns = [
    path('', upload_resume_and_send, name='upload_resume'),
]
