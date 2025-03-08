from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_resume_and_review, name='upload_resume'),
    path('save-edited-data/', views.save_edited_resume, name='save_edited_resume'),
]
