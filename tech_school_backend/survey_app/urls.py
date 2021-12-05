from django.urls import path, include

from .views import *


urlpatterns = [
    path('<int:pk>-<str:slug>/', record_answer, name='record_answer'),
]