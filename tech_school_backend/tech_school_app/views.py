from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics

from .models import *
from .serializers import *

# authentification permissions
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

# admin has a permission
class IsAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


# teacher has a permission
class IsTeacher(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


"""
if the view shoud be closed:

    permission_classes = (IsTeacher, IsAdmin)

    def get_queryset(self):
        user = self.request.user
        
        if user.is_authenticated:
            return Executor.objects.filter(user=user)
        
        raise PermissionDenied()
"""