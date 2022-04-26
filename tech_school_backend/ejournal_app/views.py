from django.shortcuts import render
from django.db.models import Avg, Count, Q, Sum
from tech_school_app.models import *
from django.views.generic import TemplateView
from django.contrib.admin.sites import site
from datetime import datetime
from rest_framework import generics, viewsets, status, permissions
from .serializers import *
from rest_framework.response import Response


class EjournalView(TemplateView):
    """
    Представление "Средние баллы и посещаемость", расширяющее админ-панель.
    Служит для отображения и фильтрации данных электронного журнала, а именно -- средних баллов и процента посещаемости студентов.
    Обязательные параметры для фильтрации: group (pk) и date. В date используются только месяц и год.
    Все отображаемые данные условно деляется на три блока: средние оценки, посещаемость, итоговые значения.
    """
    template_name = "ejournal.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(site.each_context(self.request))

        context["headings1"] = [  # таблица средних баллов
            'студент',
            'предмет',
            'средний балл',
        ]

        context["headings2"] = [  # таблица посещаемости
            'студент',
            'предмет',
            'present',
            'absent',
            '% present',
        ]

        context["headings3"] = [  # таблица totals
            'студент',
            'часов посетил',
            'всего часов',
            '% часов',
            'средние оценки',
            'среднее по всем оценкам'
        ]

        # получаем от пользователя
        date = self.request.GET.get("date")
        group = self.request.GET.get("group")

        groups = Group.objects.all()  # все группы
        context["groups"] = groups

        queryset = Grade.objects.all()  # queryset: все оценки

        # информация отображается только если выбрана группа и дата
        if group and date:
            year, month, _ = date.split('-')  # год и месяц
            queryset = queryset.filter(class_id__when__year=year, class_id__when__month=month,
                                       class_id__group__id=group)

            classes = Class.objects.filter(group__id=group, when__year=year, when__month=month)  # занятия группы
            total_hours = classes.aggregate(total=Sum('hours'))[
                "total"]  # сколько всего часов занятий у группы в указанный период

            grades_queryset = queryset.filter(grade_type="g")  # только оценки
            attendance_queryset = queryset.filter(grade_type="a")  # только посещения

            # средние баллы по каждому предмету для каждого студента (складываются из всех оценок за период)
            avg_grades = grades_queryset.values('class_id__subject', 'student').order_by().annotate(Avg('grade'))

            # % посещаемости по каждому предмету для каждого студента без учёта длительности занятий, только соотношение отметок "present" и "absent"
            present_count = Count('grade', filter=Q(attendance='1'))
            absent_count = Count('grade', filter=Q(attendance='0'))
            avg_attendance = attendance_queryset.values('class_id__subject', 'student').order_by().annotate(
                present=present_count).annotate(absent=absent_count)

            avg = []  # приведение средних баллов к наглядному виду, который можно вывести в таблице
            for row in avg_grades:
                _row = {}
                _row["student"] = Student.objects.get(pk=row['student'])
                _row["subject"] = Subject.objects.get(pk=row['class_id__subject'])
                _row["avg_point"] = round(row['grade__avg'], 2)  # округление до сотых
                avg.append(_row)

            att = []  # приведение посещаемости к наглядному виду, который можно вывести в таблице
            for row in avg_attendance:
                _row = {}
                _row["student"] = Student.objects.get(pk=row['student'])
                _row["subject"] = Subject.objects.get(pk=row['class_id__subject'])
                _row["present"] = row['present']
                _row["absent"] = row['absent']
                _row["percent"] = round(row['present'] / (row['present'] + row['absent']),
                                        2)  # получение и округление процента
                att.append(_row)

            totals = {}

            for row in queryset:
                if not totals.get(row.student.pk):
                    totals[row.student.pk] = {}
                    totals[row.student.pk]["data"] = {"avgs": []}
                    totals[row.student.pk]["student"] = row.student

            for row in avg:
                key = row["student"].id
                totals[key]["data"]["avgs"].append(row["avg_point"])

            for key in totals.keys():
                _student = totals[key]["student"]
                _attendance = attendance_queryset.filter(student=_student.id).values('class_id__hours', 'attendance')
                _present = sum([i["class_id__hours"] * int(i["attendance"]) for i in _attendance])  # посетил в часах
                _percent = round(_present / total_hours, 2) if total_hours != 0 else None  # % от общего числа часов
                totals[key]["data"]["present"] = _present
                totals[key]["data"]["percent"] = _percent

            # получение итоговой средней оценки по всем средним баллам
            for key in totals.keys():
                totals[key]["data"]["total_avg"] = round(
                    sum(totals[key]["data"]["avgs"]) / len(totals[key]["data"]["avgs"]), 2) if totals[key]["data"][
                    "avgs"] else None

            totals_data = []
            for key in totals.keys():
                totals_data.append(totals[key])

            context["avg"] = avg
            context["att"] = att
            context['total_hours'] = total_hours
            context['totals'] = totals_data
            context['alert'] = 'Чтобы выбрать новую группу и период, нажмите "Сброс".'
        else:
            context['alert'] = 'Введите оба фильтра!'
        return context


class ClassesView(TemplateView):
    """
    Представление "Карточки занятий", расширяющее админ-панель.
    Служит для отображения карточек занятий (объектов модели Class).
    Параметры для фидьтрации:
        date (date) -- точная дата занятия
        group (int) -- группа (pk)
        teacher (int) -- преподаватель (pk)
        ctype (int) -- тип занятия (pk)
    Помимо базовой информации о каждом занятии, получает список студентов и оценки, проставленные за занятие.
    """
    template_name = "classes.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(site.each_context(self.request))

        date = self.request.GET.get("date")
        group = self.request.GET.get("group")
        teacher = self.request.GET.get("teacher")
        ctype = self.request.GET.get("ctype")
        dfrom = self.request.GET.get("dfrom")
        dto = self.request.GET.get("dto")

        groups = Group.objects.filter(status='1')  # все активные группы
        context["groups"] = groups

        teachers = Teacher.objects.filter(is_active='1')  # все активные преподаватели
        context["teachers"] = teachers

        ctypes = ClassType.objects.all()  # все типы занятий
        context["ctypes"] = ctypes
        ctype = self.request.GET.get("ctype")

        queryset = Class.objects.all()

        if date:  # точная дата занятий
            year, month, day = date.split('-')
            queryset = queryset.filter(when__date__year=year, when__date__month=month, when__date__day=day)

        if group:
            queryset = queryset.filter(group__id=group)

        if teacher:
            queryset = queryset.filter(teacher__id=teacher)

        if ctype:
            queryset = queryset.filter(class_type=ctype)

        if dfrom:
            queryset = queryset.filter(when__date__gte=dfrom)

        if dto:
            queryset = queryset.filter(when__date__lte=dto)

        # наглядное отображение информации о занятиях, включая список студентов и оценки за это занятие
        classes = []
        for row in queryset:
            _row = {}
            _group = row.group
            _class = row
            _row["class"] = _class
            _row["when"] = _class.when.strftime("%Y-%m-%d %H:%M:%S")
            _members = Membership.objects.filter(group=_group)
            _row["members"] = []
            for member in _members:
                attendance = Grade.objects.filter(grade_type='a', student=member.student, class_id=_class)
                grades = Grade.objects.filter(grade_type='g', student=member.student, class_id=_class)
                _row["members"].append({"member": member.student,
                                        "grades": [g.grade for g in grades] if grades else 'Нет оценок.',
                                        "attendance": getattr(attendance[0],
                                                              'get_attendance_display') if attendance else 'Нужно отметить посещение!'})
            classes.append(_row)

        context['classes'] = classes
        # context['user'] = user

        return context
