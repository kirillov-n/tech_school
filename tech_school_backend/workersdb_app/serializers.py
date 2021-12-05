from rest_framework import serializers
from tech_school_app.models import *
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer): # для просмотра поля у Teacher
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInfo
        fields = '__all__'


class PersonalInfoChangesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInfoChanges
        fields = '__all__'


class DetailPersonalInfoChangesSerializer(PersonalInfoChangesSerializer): # расширенный PersonalInfoChanges
    personal_info = PersonalInfoSerializer(read_only=True)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'


class DetailWorkerSerializer(WorkerSerializer): # расширенный Worker
    personal_info = PersonalInfoSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    education_level = serializers.CharField(source="get_education_level_display")
    available = serializers.CharField(source="get_available_display")


class WorkerChangesSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerChanges
        fields = '__all__'


class DetailWorkerChangesSerializer(WorkerChangesSerializer): # расширенный WorkerChanges
    worker = WorkerSerializer(read_only=True)


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = '__all__'


class DetailLicenseSerializer(LicenseSerializer): # расширенный License
    relevance = serializers.CharField(source="get_relevance_display")
    worker = WorkerSerializer(read_only=True)


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'


class DetailTeacherSerializer(TeacherSerializer): # расширенный Teacher
    user = UserSerializer(read_only=True)
    worker = WorkerSerializer(read_only=True)
    position = serializers.CharField(source="get_position_display")
    is_active = serializers.CharField(source="get_is_active_display")


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class DetailNotificationSerializer(NotificationSerializer): # расширенный Notification
    status = serializers.CharField(source="get_status_display")
    importance = serializers.CharField(source="get_importance_display")

