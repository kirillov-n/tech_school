from django.urls import path, include
from hours_app import views
from .views import *

urlpatterns = [
    path('download/', views.download_file, name='download_file'),
]
