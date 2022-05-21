import pandas as pd
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.admin.sites import site
from tech_school_app.models import *
from django.db.models import Sum
import mimetypes
import os
from django.http.response import HttpResponse


class HoursView(TemplateView):
    """
    Представление "Учёт часов (группа, месяц)", расширяющшее админ-панель.
    Служит для формирования ведомости учета часов преподавания.
    Параметры для фильтрации:
        date (date) -- дата (используются месяц и год)
        group (int) -- группа (pk)
    Оригинальный документ формируется по группе за месяц и содержит информацию о часах преподавания в этот периодд у этой группы.
    """
    template_name = "hours.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(site.each_context(self.request))

        date = self.request.GET.get("date")
        group = self.request.GET.get("group")

        context["headings"] = [
            'преподаватель',
            'детали',
            'личные часы',
            'рабочие часы',
            'всего'
        ]

        groups = Group.objects.all()  # все группы
        context["groups"] = groups

        queryset = TrainingHours.objects.all().order_by(
            "teacher")  # queryset: все объекты таблицы "учёт часов", упорядоченные по преподавателю

        if date:
            year, month, _ = date.split('-')
            queryset = queryset.filter(date__year=year, date__month=month)

        if group:
            queryset = queryset.filter(group__id=group)

        # расчёт трёх сумм часов (всего, рабочее время, личное время) по каждому преподавателю

        teachers_group = {}

        for row in queryset:
            if not teachers_group.get(row.teacher.pk):
                teachers_group[row.teacher.pk] = {}
                teachers_group[row.teacher.pk]["data"] = []
                teachers_group[row.teacher.pk]["teacher"] = row.teacher

            teachers_group[row.teacher.pk]["data"].append(row)

        for key in teachers_group.keys():
            row = teachers_group[key]

            teachers_group[key]["sum_working"] = 0
            teachers_group[key]["sum_personal"] = 0
            teachers_group[key]["sum_total"] = 0

            for _row in row["data"]:
                teachers_group[key]["sum_total"] += _row.hours
                if _row.time_type == 'w':
                    teachers_group[key]["sum_working"] += _row.hours
                elif _row.time_type == 'p':
                    teachers_group[key]["sum_personal"] += _row.hours

        teachers_groups = []

        for key in teachers_group.keys():
            teachers_groups.append(teachers_group[key])

        # суммы по строкам и столбцам в таблице
        total_p = queryset.filter(time_type="p").aggregate(Sum('hours'))["hours__sum"]
        total_w = queryset.filter(time_type="w").aggregate(Sum('hours'))["hours__sum"]
        total = queryset.aggregate(Sum('hours'))["hours__sum"]

        totals = {'total_p': total_p, "total_w": total_w, "total": total}

        context["training_hours"] = teachers_groups
        context["totals"] = totals

        return context


class HoursYearView(TemplateView):
    """
    Представление "Учёт часов (год)", расширяющшее админ-панель.
    Служит для формирования ведомости учета часов преподавания.
    Параметр для фидьтрации date -- дата, из которой используется год
    Оригинальный документ формируется раз в год по всем преподавателям и содержит информацию о часах преподавания за этот период.
    """
    template_name = "hoursyear.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(site.each_context(self.request))

        context['headings'] = [
            'преподаватель',
            'итого за год',
            'в личное время',
            'в рабочее время'
        ]

        date = self.request.GET.get("date")

        queryset = TrainingHours.objects.all().order_by(
            "teacher")  # queryset: все объекты таблицы "учёт часов", упорядоченные по преподавателю

        if date:
            year, _, _ = date.split('-')
            queryset = queryset.filter(date__year=year)
            context['year'] = year

        # расчёт трёх сумм часов (всего, рабочее время, личное время) по каждому преподавателю

        data = []

        teachers = list(set([i['teacher'] for i in queryset.values('teacher')]))
        for teacher_id in teachers:
            _row = {}
            _row['teacher'] = Teacher.objects.get(pk=teacher_id)
            teacher_queryset = queryset.filter(teacher__id=teacher_id)

            th_working = teacher_queryset.filter(time_type='w')  # записи в рабочее время
            th_personal = teacher_queryset.filter(time_type='p')  # записи в личное время

            sum_working = th_working.aggregate(Sum('hours'))["hours__sum"]
            sum_personal = th_personal.aggregate(Sum('hours'))["hours__sum"]

            if not sum_working:
                sum_working = 0
            if not sum_personal:
                sum_personal = 0

            sum_total = sum_working + sum_personal

            _row['sum_working'] = sum_working
            _row['sum_personal'] = sum_personal
            _row['sum_total'] = sum_total
            data.append(_row)

        context["data"] = data
        context["queryset"] = queryset

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filename = 'out.xlsx'
        filepath = BASE_DIR + '/hours_app/download_files/' + filename
        df = pd.DataFrame(data)
        df['teacher'] = df['teacher'].astype(str)
        df[['trash', 'teacher']] = df['teacher'].str.split(',', 1, expand=True)
        df[['teacher', 'trash']] = df['teacher'].str.split(',', 1, expand=True)
        df = df.drop(columns='trash')
        df = df.rename(columns={"teacher": "Преподователь", "sum_working": "в рабочее время", "sum_personal": "в личное время", "sum_total": "итого за год"})
        df.to_excel(filepath, encoding="utf-8")

        return context


def download_file(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filename = 'out.xlsx'
    filepath = BASE_DIR + '/hours_app/download_files/' + filename
    path = open(filepath, 'rb')
    mime_type, _ = mimetypes.guess_type(filepath)
    response = HttpResponse(path, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response
