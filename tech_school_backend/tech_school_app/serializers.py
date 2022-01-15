from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class WorkingDatesCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingDates
        fields = '__all__'
