from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, viewsets, status, permissions
from django.views.generic import TemplateView
from django.contrib.admin.sites import site

from tech_school_app.models import *
from .serializers import *


class WorkerViewSet(viewsets.ModelViewSet):
    '''ModelViewSet для модели Worker. List и Retrieve используют расширенный сериализатор.'''
    queryset = Worker.objects.all()

    def get_serializer_class(self):

        if self.action in ["list", "retrieve"]:

            return DetailWorkerSerializer
        
        return WorkerSerializer


class TeacherViewSet(viewsets.ModelViewSet):
    '''ModelViewSet для модели Teacher. List и Retrieve используют расширенный сериализатор.'''
    queryset = Teacher.objects.all()

    def get_serializer_class(self):

        if self.action in ["list", "retrieve"]:

            return DetailTeacherSerializer
        
        return TeacherSerializer


class LicenseViewSet(viewsets.ModelViewSet):
    '''ModelViewSet для модели License. List и Retrieve используют расширенный сериализатор.'''
    queryset = License.objects.all()
    
    def get_serializer_class(self):

        if self.action in ["list", "retrieve"]:

            return DetailLicenseSerializer
        
        return LicenseSerializer


class FilterLicensesView(generics.ListAPIView):
    '''
    ListAPIView для фильтрации лицензий при просмотре (License).
    Параметры:
        name -- название лицензии
        dd1 -- нижняя граница даты doc_date
        dd2 -- верхняя граница даты doc_date
        relevance -- релеантность лицензии
        worker -- сотрудник, которому принадлежит лицензия
    '''
    serializer_class = DetailLicenseSerializer

    def get_queryset(self):
        queryset = License.objects.all()

        params = self.request.query_params

        name = params.get('name', None)
        dd1 = params.get('dd1', None)
        dd2 = params.get('dd2', None)
        relevance = params.get('relevance', None)
        worker = params.get('worker', None)

        if name:
            queryset = queryset.filter(name__contains=name)

        if dd1: # doc_date после этой даты
            queryset = queryset.filter(doc_date__gte=dd1)

        if dd2: # doc_date до этой даты
            queryset = queryset.filter(doc_date__lte=dd2)

        if relevance:
            queryset = queryset.filter(relevance=relevance)
        
        if worker:
            queryset = queryset.filter(worker__id=worker)

        return queryset


class DepartmentViewSet(viewsets.ModelViewSet):
    '''ModelViewSet для модели Department.'''
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class PersonalInfoViewSet(viewsets.ModelViewSet):
    '''ModelViewSet для модели PersonalInfo.'''
    queryset = PersonalInfo.objects.all()
    serializer_class = PersonalInfoSerializer


class PersonalInfoChangesView(generics.ListAPIView):
    '''ListAPIView для PersonalInfoChanges (изменения в PersonalInfo).
    Просмотр с возможностью фильтрации по сотруднику (параметр worker).'''
    queryset = PersonalInfoChanges.objects.all()
    serializer_class = DetailWorkerChangesSerializer

    def get(self, request, **kwargs):
        worker = kwargs.get('worker')

        queryset = self.queryset.filter(personal_info__worker=worker)

        serialized_data = [
            self.serializer_class(row).data for row in queryset
        ]

        return Response(data=serialized_data, status=status.HTTP_200_OK)


class WorkerChangesView(generics.ListAPIView):
    '''ListAPIView для WorkerChanges (изменения в Worker).
    Просмотр с возможностью фильтрации по сотруднику (параметр worker).'''
    queryset = WorkerChanges.objects.all()
    serializer_class = DetailWorkerChangesSerializer

    def get(self, request, **kwargs):
        worker = kwargs.get('worker')

        queryset = self.queryset.filter(worker=worker)

        serialized_data = [
            self.serializer_class(row).data for row in queryset
        ]

        return Response(data=serialized_data, status=status.HTTP_200_OK)


class CheckWorkersDataView(generics.ListAPIView):
    '''
    ListAPIView для получения и просмотра списка сотрудников, у которых подходит дата next_training.
    delta -- число дней, которое используется для проверки условия в методе check_training модели Worker.
    '''
    queryset = Worker.objects.all()
    serializer_class = DetailWorkerSerializer
    # чтобы не авторизовываться
    permission_classes = [permissions.AllowAny]

    def get(self, request, **kwargs):
        delta = kwargs.get('delta')

        queryset = Worker.check_training(delta)

        serialized_data = [
            self.serializer_class(row).data for row in queryset
        ]

        return Response(data=serialized_data, status=status.HTTP_200_OK)


class CreateNotificationView(generics.CreateAPIView):
    '''CreateAPIView для создания уведомлений (Notification) об актуальности данных сотрудников.'''
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    # чтобы не авторизовываться
    permission_classes = [permissions.AllowAny]


class FilterWorkersView(generics.ListAPIView):
    '''
    ListAPIView для фильтрации сотрудников при просмотре (Worker).
    Параметры:
        person (int) -- персональные данные, pk
        surname (str) -- фамилия
        name (str) -- имя
        patronymic (str) -- отчество
        department (int) -- подразделение, pk
        level (str) -- уровень образования, choices
        available (str) -- доступен ли, choices
        lt1 (date) -- нижняя граница даты last_training
        lt2 (date) -- верхняя граница даты last_training
        nt1 (date) -- нижняя граница даты next_training
        nt2 (date) -- верхняя граница даты next_training
        note (str) -- подстрока в поле notes
    '''
    serializer_class = DetailWorkerSerializer

    def get_queryset(self):
        queryset = Worker.objects.all()

        params = self.request.query_params

        person = params.get('person', None)
        surname = params.get('surname', None)
        name = params.get('name', None)
        patronymic = params.get('patronymic', None)
        department = params.get('department', None)
        level = params.get('level', None)
        available = params.get('available', None)
        lt1 = params.get('lt1', None)
        lt2 = params.get('lt2', None)
        nt1 = params.get('nt1', None)
        nt2 = params.get('nt2', None)
        note = params.get('note', None)

        if person:
            queryset = queryset.filter(personal_info__id=person)

        if surname:
            queryset = queryset.filter(personal_info__surname=surname)

        if name:
            queryset = queryset.filter(personal_info__name=name)

        if patronymic:
            queryset = queryset.filter(personal_info__patronymic=patronymic)

        if department:
            queryset = queryset.filter(department__id=department)

        if level:
            queryset = queryset.filter(education_level=level)

        if available:
            queryset = queryset.filter(available=available)

        if lt1: # last_training после этой даты
            queryset = queryset.filter(last_training__gte=lt1)

        if lt2: # last_training до этой даты
            queryset = queryset.filter(last_training__lte=lt2)

        if nt1: # next_training после этой даты
            queryset = queryset.filter(next_training__gte=nt1)

        if nt2: # next_training до этой даты
            queryset = queryset.filter(next_training__lte=nt2)

        if note:
            queryset = queryset.filter(notes__contains=note)

        return queryset


