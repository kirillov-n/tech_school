from django.shortcuts import render
from django.db.models import Avg, Count, Q, Sum
from tech_school_app.models import *
from django.views.generic import TemplateView
from django.contrib.admin.sites import site
from datetime import datetime

class SalaryCountView(TemplateView):
    """
    Представление, расширяющее админ-панель.
    Служит для отображения всех параметров, влияющих на зарплату преподавателя, подбора подходящих норм оплаты преподавания и расчёта суммы зарплаты за месяц.
    Что влияет: тип времени преподавания (личное/рабочее), уровень образования (Высшее/СПО), контингент учащихся группы, число часов.
    Два обязательных параметра для фидьтрации:
        teacher (int) -- преподаватель (pk)
        date (date) -- дата, используются только месяц и год
    Данные условно делятся на три блока:
    1) Общая сводка по преподавателю (и полная сумма зарплаты)
    2) Рабочее время (и подытог зарплаты)
    3) Личное время (с подытогом)
    """
    template_name = "salary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(site.each_context(self.request))

        context["headings1"] = [
            "личные часы",
            "рабочие часы",
            "сумма личных часов",
            "сумма рабочих часов",
            "всего часов",
            "рассчитанная зарплата, руб."
        ]

        context["headings2"] = [
            "группа",
            "уровень студентов",
            "сумма часов",
            "подходящая норма",
            "Итог по строке, руб."
        ]


        teachers = Teacher.objects.filter(is_active='1') # все активные преподаватели
        context["teachers"] = teachers

        norms = SalaryNorm.objects.filter(if_valid='1') # все валидные нормы зарплаты
        context["norms"] = norms

        date = self.request.GET.get("date")
        teacher = self.request.GET.get("teacher")

        queryset = TrainingHours.objects.all() # queryset: все объекты таблицы "учёт часов"

        if teacher and date:
            year, month, _ = date.split('-') # год и месяц
            queryset = queryset.filter(teacher__id=teacher, date__year=year, date__month=month)
            
            th_working = queryset.filter(time_type='w')
            th_personal = queryset.filter(time_type='p')

            sum_working = th_working.aggregate(Sum('hours'))["hours__sum"]
            sum_personal = th_personal.aggregate(Sum('hours'))["hours__sum"]
            if not sum_working:
                sum_working = 0
            if not sum_personal:
                sum_personal = 0

            sum_total = sum_working + sum_personal

            context['th_working'] = th_working
            context['th_personal'] = th_personal

            context["sum_working"] = sum_working
            context["sum_personal"] = sum_personal
            context["sum_total"] = sum_total

            rows_working = th_working.values('group', 'group__edu_level').annotate(Sum('hours')) # записи за рабочее время
            rows_personal = th_personal.values('group', 'group__edu_level').annotate(Sum('hours')) # записи за личное время
            
            worker = Worker.objects.get(teacher__id=teacher)
            teacher_level = getattr(worker, "education_level") # уровень образования преподавателя
            
            # объект из записей за рабочее время
            data_working = []
            for row in rows_working:
                _row = {}
                _row["group"] = Group.objects.get(pk=row['group'])
                _row["students_level"] = row["group__edu_level"]
                _row["sum"] = row["hours__sum"]
                matching_norm = norms.filter(education_level=teacher_level, students=row["group__edu_level"], time_type='w')
                _row["norm"] = matching_norm[0] if matching_norm else None
                _row["mult"] = _row["sum"] * getattr(_row["norm"], 'amount') if _row["norm"] else 0
                data_working.append(_row)
            
            # расчёт подытога за рабочее время
            salary_working = 0
            for row in data_working:
                salary_working += row["mult"]
                if row["mult"] == 0:
                    context["no_norm"] = 'Итог=0, так как норма зарплаты не найдена, добавьте её в "Нормы зарплат"!'

            # объект из записей за личное время
            data_personal = []
            for row in rows_personal:
                _row = {}
                _row["group"] = Group.objects.get(pk=row['group'])
                _row["students_level"] = row["group__edu_level"]
                _row["sum"] = row["hours__sum"]
                matching_norm = norms.filter(education_level=teacher_level, students=row["group__edu_level"], time_type='w')
                _row["norm"] = matching_norm[0] if matching_norm else None
                _row["mult"] = _row["sum"] * getattr(_row["norm"], 'amount') if _row["norm"] else 0
                data_personal.append(_row)
            
            # расчёт подытога за личное время
            salary_personal = 0
            for row in data_personal:
                salary_personal += row["mult"]
                if row["mult"] == 0:
                    context["no_norm"] = 'Итог=0, так как норма зарплаты не найдена, добавьте её в "Нормы зарплат"!'

            salary_total = salary_personal + salary_working # полная сумма зарплаты

            context['data_working'] = data_working
            context['salary_working'] = salary_working

            context['data_personal'] = data_personal
            context['salary_personal'] = salary_personal

            context['salary_total'] = salary_total

            context['info'] = {'teacher': worker, 'month': month, 'year': year}
            context['alert'] = 'Чтобы выбрать нового преподавателя и период, нажмите "Сброс".'
        else:
            context['alert'] = 'Введите оба фильтра!'

        return context


class ScholarshipCountView(TemplateView):
    """
    Представление, расширяющее админ-панель.
    Служит для отображения всех параметров, влияющих на стипендию студента, и расчёта суммы стипендии за месяц.
    Что влияет: средние баллы, % посещаемости, оценки за отдельные экзамены, учебная программа.
    Два обязательных параметра для фидьтрации:
        student (int) -- студент (pk)
        date (date) -- дата, используются только месяц и год
    Расчёт производится в полуавтоматическом режиме: норма выбирается в ручную из списка норм для программы с опорой на параметры.
    То есть дополнительно принимается параметр norm (norm) -- норма стипендии (pk).
    """
    template_name = "scholarship.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(site.each_context(self.request))

        context['headings'] = [
            'Оценки за экзамены',
            'Ср.баллы',
            'Общий средний балл',
            '% посещаемости',
            'Нормы программы',
            'Стипендия, руб.'
        ]

        date = self.request.GET.get("date")
        student = self.request.GET.get("student")
        norm = self.request.GET.get("norm")

        norms = ScolarshipNorm.objects.filter(if_valid='1') # все валидные нормы
        students = Student.objects.filter(education_status='1') # все обучающиеся студенты

        context["students"] = students

        if student and date:
            year, month, _ = date.split('-') # год и месяц
            
            _group = getattr(Student.objects.filter(id=student)[0].recent_group, 'group') # актуальная группа студента
            queryset = Grade.objects.filter(class_id__when__year=year, class_id__when__month=month, student__id=student, class_id__group=_group)
            norms = norms.filter(program=_group.program) # все нормы программы, по которой обучается студент (группа)
            
            context["norms"] = norms
            context["student"] = Student.objects.filter(id=student)[0]
            context["group"] = _group
            context["program"] = _group.program

            classes = Class.objects.filter(group__id=_group.id, when__year=year, when__month=month) # занятия группы
            total_hours = classes.aggregate(total=Sum('hours'))["total"] # сколько всего часов занятий у группы в указанный период

            grades_queryset = queryset.filter(grade_type="g") # только оценки
            attendance_queryset = queryset.filter(grade_type="a") # только посещения
            exams = queryset.filter(grade_type='g', class_id__class_type__name='Экзамен') # оценки за экзамены

            # средние баллы по каждому предмету выбранного студента
            avg_grades = grades_queryset.values('class_id__subject').order_by().annotate(Avg('grade'))

            avg = [] # приведение средних баллов к наглядному виду
            for row in avg_grades:
                _row = {}
                _row["subject"] = Subject.objects.get(pk=row['class_id__subject'])
                _row["avg_point"] = round(row['grade__avg'], 2) # округление до сотых
                avg.append(_row)
            
            total_grade = avg_grades.aggregate(Avg('grade__avg'))["grade__avg__avg"] # получение итоговой средней оценки по всем средним баллам

            # процент посещаемости
            _attendance = attendance_queryset.values('class_id__hours', 'attendance')
            _present = sum([i["class_id__hours"] * int(i["attendance"]) for i in _attendance]) # посетил в часах
            _percent = round( _present / total_hours, 2 ) if total_hours else None # % от общего числа часов
            avg_attendance = {'total_hours': total_hours, 'present': _present, 'percent': _percent}

            context["exams"] = exams
            context["total_grade"] = total_grade
            context["avg"] = avg
            context["att"] = avg_attendance

            # на основании выбранной нормы, рассчитывается итоговая сумма стипендии студента
            if norm:
                amount = getattr(norms.filter(id=norm)[0], 'amount')
                scholarship = amount * avg_attendance["percent"]
                context['scholarship'] = scholarship

        return context