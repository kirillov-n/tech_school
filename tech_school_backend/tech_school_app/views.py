from django.shortcuts import render
from django.utils.safestring import mark_safe
from rest_framework.response import Response
from rest_framework import generics, viewsets, status

from .models import *
from .serializers import *

# authentification permissions
import calendar
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.contrib.admin.sites import site
from django.shortcuts import render
from datetime import datetime, date, timedelta


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


class WorkingDatesView(TemplateView):
    """
    Представление "Производственный календарь", расширяющее админ-панель.
    Служит для отображения производственного календаря в виде календаря.
    """
    template_name = "workingdates.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(site.each_context(self.request))

        context["headings"] = [
            'январь',
            'февраль',
            'март',
            'апрель',
            'май',
            'июнь',
            'июль',
            'август',
            'сентябрь',
            'октябрь',
            'ноябрь',
            'декабрь',
        ]

        dates = WorkingDates.objects.all().order_by('date')  # все даты

        months = []
        month_labels = []
        _month = {}
        for i in range(1, 13):
            _days = {}
            month = dates.filter(date__month=str(i))
            for j in range(len(month)):
                _days[j + 1] = getattr(month[j], 'date')
            _month[i] = _days
        months.append(_month)

        _month = {}
        for i in range(1, 13):
            _labels = {}
            month = dates.filter(date__month=str(i))
            for j in range(len(month)):
                _labels[j + 1] = getattr(month[j], 'if_working')
            _month[i] = _labels
        month_labels.append(_month)

        Jan_labels = []
        Feb_labels = []
        Mar_labels = []
        Apr_labels = []
        May_labels = []
        Jun_labels = []
        Jul_labels = []
        Aug_labels = []
        Sep_labels = []
        Oct_labels = []
        Nov_labels = []
        Dec_labels = []

        for i in range(len(month_labels[0][1])):
            Jan_labels.append(month_labels[0][1][i + 1])
        for i in range(len(month_labels[0][2])):
            Feb_labels.append(month_labels[0][2][i + 1])
        for i in range(len(month_labels[0][3])):
            Mar_labels.append(month_labels[0][3][i + 1])
        for i in range(len(month_labels[0][4])):
            Apr_labels.append(month_labels[0][4][i + 1])
        for i in range(len(month_labels[0][5])):
            May_labels.append(month_labels[0][5][i + 1])
        for i in range(len(month_labels[0][6])):
            Jun_labels.append(month_labels[0][6][i + 1])
        for i in range(len(month_labels[0][7])):
            Jul_labels.append(month_labels[0][7][i + 1])
        for i in range(len(month_labels[0][8])):
            Aug_labels.append(month_labels[0][8][i + 1])
        for i in range(len(month_labels[0][9])):
            Sep_labels.append(month_labels[0][9][i + 1])
        for i in range(len(month_labels[0][10])):
            Oct_labels.append(month_labels[0][10][i + 1])
        for i in range(len(month_labels[0][11])):
            Nov_labels.append(month_labels[0][11][i + 1])
        for i in range(len(month_labels[0][12])):
            Dec_labels.append(month_labels[0][12][i + 1])

        Jan = months[0][1]
        Jan = zip(Jan, Jan_labels)
        Feb = months[0][2]
        Feb = zip(Feb, Feb_labels)
        Mar = months[0][3]
        Mar = zip(Mar, Mar_labels)
        Apr = months[0][4]
        Apr = zip(Apr, Apr_labels)
        May = months[0][5]
        May = zip(May, May_labels)
        Jun = months[0][6]
        Jun = zip(Jun, Jun_labels)
        Jul = months[0][7]
        Jul = zip(Jul, Jul_labels)
        Aug = months[0][8]
        Aug = zip(Aug, Aug_labels)
        Sep = months[0][9]
        Sep = zip(Sep, Sep_labels)
        Oct = months[0][10]
        Oct = zip(Oct, Oct_labels)
        Nov = months[0][11]
        Nov = zip(Nov, Nov_labels)
        Dec = months[0][12]
        Dec = zip(Dec, Dec_labels)

        cal = {'jan': Jan,
               'feb': Feb,
               'mar': Mar,
               'apr': Apr,
               'may': May,
               'jun': Jun,
               'jul': Jul,
               'aug': Aug,
               'sep': Sep,
               'oct': Oct,
               'nov': Nov,
               'dec': Dec}
        context["cal"] = cal

        return context


"""
if the view shoud be closed:

    permission_classes = (IsTeacher, IsAdmin)

    def get_queryset(self):
        user = self.request.user
        
        if user.is_authenticated:
            return Executor.objects.filter(user=user)
        
        raise PermissionDenied()
"""
