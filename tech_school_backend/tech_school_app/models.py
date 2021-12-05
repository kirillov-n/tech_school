from django.db import models
from django.contrib.auth.models import User
import jsonfield
from django_lifecycle import LifecycleModel, hook, AFTER_UPDATE, AFTER_CREATE, BEFORE_UPDATE, BEFORE_CREATE
import datetime
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.db.models import Avg, Count, Q, Sum
from django.core.mail import send_mail
from django.conf import settings


class PersonalInfo(LifecycleModel):
    """Модель "Персональные данные" для хранения персональных данных студентов и сотрудников."""
    surname = models.CharField('Фамилия', max_length=200)
    name = models.CharField('Имя', max_length=200)
    patronymic = models.CharField('Отчество', max_length=200)
    phone = models.CharField('Телефон', max_length=14, blank=True, null=True)
    email = models.EmailField('Электронная почта', max_length=254, blank=True, null=True)
    birth_date = models.DateField('Дата рождения', blank=True, null=True)

    class Meta:
        verbose_name = 'Персональные данные человека'
        verbose_name_plural = 'Персональные данные'

    def __str__(self):
            return '{} {} {}, {}'.format(self.surname, self.name, self.patronymic, self.phone)

    @hook(AFTER_CREATE)
    @hook(AFTER_UPDATE)
    def update_personal_info_changes(self):
        """Добавляет в таблицу PersonalInfoChanges записи об изменениях в полях объектов PersonalInfo."""
        personal_info = PersonalInfo.objects.filter(pk=self.pk).values()[0]

        for field in personal_info:
            if self.has_changed(field):
                changes = PersonalInfoChanges(
                    personal_info=self,
                    field_name=field,
                    new_value=personal_info[field]
                )

                changes.save()


class Department(models.Model):
    """Класс "Подразделение". Каждый сотрудник относится к какому-либо подразделению."""
    name = models.CharField('Название подразделения', max_length=200)

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'

    def __str__(self):
        return 'Подразделение "{}"'.format(self.name)


class Worker(LifecycleModel):
    """Модель "Сотрудник". Все сотрудники (потенциальные преподаватели ТШ) относятся к данному классу."""
    personal_info = models.ForeignKey(PersonalInfo, on_delete=models.CASCADE, verbose_name='Персональные данные сотрудника')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Подразделение сотрудника')
    EDU_LEVELS = [
        ('0', 'Высшее'),
        ('1', 'СПО'),
        ('2', 'Среднее Общее')
    ]
    education_level = models.CharField('Уровень образования', max_length=1, choices=EDU_LEVELS, default='0')
    # education_date = models.DateField('Дата получения образования')
    last_training = models.DateField('Предыдущее обучение')
    next_training = models.DateField('Следующее обучение')
    notes = models.CharField('Заметки', max_length=400, blank=True)
    AVAILABILITY = [
        ('0', 'недоступен'),
        ('1', 'доступен')
    ]
    available = models.CharField('Доступен для преподавания', max_length=1, choices=AVAILABILITY, default='0')

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return '{}'.format(self.personal_info)

    def check_training(delta):
        """
        Принимает на вход число delta. Рассчитывает разницу (current delta) между текущей датой и той датой,
        в которую преподавателю необходимо пройти следующее обучение.
        Если разница меньше или равно delta, до даты обучения осталось меньше delta дней,
        а значит нужно организовать прохождение переобучения преподавателем.
        Возвращает queryset из преподавателей, которым осталось меньше delta дней до даты next_training.
        """
        current_date = datetime.datetime.now().date()

        queryset = []

        for row in Worker.objects.all():
            current_delta = row.next_training - current_date

            if current_delta.days <= delta:
                queryset.append(row)

        return queryset

    @hook(AFTER_CREATE)
    @hook(AFTER_UPDATE)
    def update_worker_changes(self):
        """Добавляет в таблицу WorkerChanges записи об изменениях в полях объектов Worker."""
        worker = Worker.objects.filter(pk=self.pk).values()[0]

        for field in worker:
            if self.has_changed(field):
                changes = WorkerChanges(
                    worker=self,
                    field_name=field,
                    new_value=worker[field]
                )

                changes.save()


class WorkerChanges(models.Model):
    """Модель "Изменения в данных сотрудника". Объекты класса -- автоматически добавляемые записи об изменениях в Worker."""
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=50)
    new_value = models.CharField(max_length=400)
    changed_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Изменение в данных сотрудника'
        verbose_name_plural = 'Изменения в данных сотрудников'
    
    def __str__(self):
        return "{}, изменено {}".format(self.worker, self.changed_at)


class PersonalInfoChanges(models.Model):
    """Модель "Изменения в персональных данных". Объекты класса -- автоматически добавляемые записи об изменениях в PersonalInfo."""
    personal_info = models.ForeignKey(PersonalInfo, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=50)
    new_value = models.CharField(max_length=400)
    changed_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Изменение в персональных данных'
        verbose_name_plural = 'Изменения в персональных данных'
    
    def __str__(self):
        return "{}, изменено {}".format(self.personal_info, self.changed_at)


class License(models.Model):
    """
    Модель "Лицензии". Объекты класса хранят мета-данные и файл скана лицензии об образовании / переподготовке сотрудника.
    У каждого сотрудника (Worker) может быть много релевантных и уже нерелевантных документов.
    """
    name = models.CharField('Название лицензии', max_length=200)
    upload_date = models.DateTimeField('Дата загрузки', auto_now_add=True, null=True)
    scan = models.FileField('Скан', upload_to=f'{settings.MEDIA_ROOT}/licenses')
    #image = models.ImageField('Изображение', upload_to=f'{settings.MEDIA_ROOT}/licenses')
    RELEVANCES = [
        ('0', 'нерелевантная'),
        ('1', 'релевантная')
    ]
    relevance = models.CharField(max_length=1, choices=RELEVANCES, default='1', verbose_name='Релевантность')
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, verbose_name='Сотрудник')
    doc_date = models.DateField('Дата из документа', blank=True, null=True)

    class Meta:
        verbose_name = 'Лицензия'
        verbose_name_plural= 'Лицензии'

    def __str__(self):
        return 'Лицензия {}, загруженная {}'.format(self.name, self.upload_date)


class Teacher(models.Model):
    """
    Класс "Преподаватель" -- те сотрудники, которые являются действующими преполдавателями ТШ,
    которым необходимо взаимодействовать с системой. Ассоциативная сущность, соединяющая User и Worker.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, verbose_name='Сотрудник')
    POSITIONS = [
        ('a', 'admin'),
        ('t', 'teacher')
    ]
    position = models.CharField('Позиция', max_length=1, choices=POSITIONS, default='t')
    ACTIVE = [
        ('0', 'неактивен'),
        ('1', 'активен')
    ]
    is_active = models.CharField('Активен ли пользователь', max_length=1, choices=ACTIVE, default='0')

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural= 'Преподаватели'

    def __str__(self):
        return 'Преподаватель {}, {}'.format(self.user, self.worker)


class Notification(LifecycleModel):
    """
    Модель "Уведомления". ОБъект класса представляет собой уведомление об актуальности данных сотрудника.
    Уведомления могут иметь различные степени важности.
    """
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, verbose_name='Сотрудник')
    text = models.CharField('Текст уведомления', max_length=400)
    created_at = models.DateTimeField('Создано', auto_now_add=True, null=True)
    STATUSES = [
        ('0', 'новое'),
        ('1', 'открытое')
    ]
    status = models.CharField('Статус', max_length=1, choices=STATUSES, default='0')
    IMPORTANCES = [
        ('0', 'низкая'),
        ('1', 'нейтральная'),
        ('2', 'высокая')
    ]
    importance = models.CharField('Степень важности', max_length=1, choices=IMPORTANCES, default='1')

    class Meta:
        verbose_name='Уведомление'
        verbose_name_plural='Уведомления'
        
    def __str__(self):
        return 'Уведомление от {}, важность {}'.format(self.created_at, self.get_importance_display())
    
    def same_today(self):
        """Проверяет, создавалось ли уже сегодня уведомление про конкретного сотрудника. Возвращает Boolean."""
        if not self.id and Notification.objects.filter(worker=self.worker, created_at__date=datetime.datetime.today()):
            return True
        else:
            return False
        
    def same_recent(self):
        """Проверяет, создавалось ли уже в последнюю неделю уведомление такой же степени важности про конкретного сотрудника. Возвращает Boolean."""
        week_before = datetime.datetime.today() - datetime.timedelta(days=7)
        if not self.id and Notification.objects.filter(importance=self.importance, worker=self.worker, created_at__date__gte=week_before):
            return True
        else:
            return False
    
    def opened_status(self):
        """Автоматически меняет статус уведомления на opened."""
        if self.id and self.status == '0':
            self.status = '1'
        return

    def save(self, *args, **kwargs):
        self.opened_status()
        if not self.same_today() and not self.same_recent():     
            super(Notification, self).save(*args, **kwargs)

    @hook(AFTER_CREATE)
    def send_notification(self):
        """
        Отправляет на email преподавателя-администратора письмо-уведомление при добавлении объекта Notification.
        """
        admin_mail = getattr(PersonalInfo.objects.filter(worker__teacher__position='a')[0], 'email')
        send_mail('Уведомление от Tech School App', f'Это уведомление важности {self.get_importance_display()} об актуальности данных {self.worker}. {self.text} Создано {self.created_at} (время сервера).', 'tech_sch@mail.ru', [admin_mail], fail_silently=False)


class Subject(models.Model):
    """Модель "Предмет". Объекты класса -- изучаемые предметы, дисциплины."""
    name = models.CharField('Название предмета', max_length=200)

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'

    def __str__(self):
        return 'Предмет "{}"'.format(self.name)

    
class Program(models.Model):
    """
    Модель "Программа". Объекты -- учебные программы, на основании которых обучаются группы в ТШ.
    Каждая программа содержит ряд предметов и вид обучения.
    """
    name = models.CharField('Название программы', max_length=200)
    subjects = models.ManyToManyField(Subject, through='InProgram', verbose_name='Предметы')
    course_type = models.ForeignKey('CourseType', on_delete=models.CASCADE, verbose_name='Тип обучения')

    class Meta:
        verbose_name = 'Программа'
        verbose_name_plural = 'Программы'

    def __str__(self):
        return 'Программа "{}"'.format(self.name)


class InProgram(models.Model):
    """Модель "Предмет в программе". Ассоциативная сущность, связывающая Subject и Program."""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, verbose_name='Программа')
    hours = models.IntegerField('Часы')

    class Meta:
        verbose_name = 'Предмет в программе'
        verbose_name_plural = 'Предметы в программах'

    def __str__(self):
        return '{} в {} ({} часов)'.format(self.subject, self.program, self.hours)


class CourseType(models.Model):
    """Модель "Тип обучения". Хранит типы программ: подготовка, повышение квалификации, инструктаж и т.д."""
    name = models.CharField('Название типа', max_length=200)

    class Meta:
        verbose_name = 'Тип обучения'
        verbose_name_plural = 'Типы обучения'

    def __str__(self):
        return '{}'.format(self.name)


class Student(models.Model):
    """Модель "Студент". Объекты класса -- студенты ТШ."""
    personal_info = models.ForeignKey(PersonalInfo, on_delete=models.CASCADE, verbose_name='Персональные данные студента')
    personnel_num = models.CharField('Табельный номер', max_length=6)
    EDU_STATUSES = [
        ('0', 'не обучается'),
        ('1', 'обучается')
    ]
    education_status = models.CharField('Статус обучения', max_length=1, choices=EDU_STATUSES, default='1')
    STAFF = [
        ('0', 'не из персонала'),
        ('1', 'из персонала')
    ]
    from_staff = models.CharField('Из персонала', max_length=1, choices=STAFF, default='0')

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'

    def __str__(self):
        return 'Студент {}, {}'.format(self.personnel_num, self.personal_info)

    @property
    def groups(self):
        """Получает список всех групп студента."""
        member = Membership.objects.filter(student=self)
        return member
    
    @property
    def recent_group(self):
        """Получает последнюю актуальную группу студента."""
        member = Membership.objects.filter(student=self).order_by("-registered_since")
        return member[0]


class Group(models.Model):
    """Модель "Группа". Основная единица учебного процесса. Объект класса содержит полную информацию об учебной группе."""
    program = models.ForeignKey(Program, on_delete=models.CASCADE, verbose_name='Программа')
    name = models.CharField('Название группы', max_length=200)
    start_theory = models.DateField('Начало теоретического обучения')
    end_theory = models.DateField('Конец теоретического обучения')
    start_practice = models.DateField('Начало практического обучения')
    end_practice = models.DateField('Конец практического обучения')
    STATUSES = [
        ('0', 'закрыта'),
        ('1', 'обучение продолжается')
    ]
    status = models.CharField('Статус группы', max_length=1, choices=STATUSES, default='1')
    EDU_LEVELS = [
        ('0', 'рабочие и учащиеся Технической школы'),
        ('1', 'руководители среднего звена, специалисты, служащие'),
        ('2', 'руководители подразделений')
    ]
    edu_level = models.CharField('Уровень образования', max_length=1, choices=EDU_LEVELS, default='1')
    students = models.ManyToManyField(Student, through='Membership', verbose_name='Студенты')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return 'Группа {}'.format(self.name)


class Membership(models.Model):
    """Модель "Студент в группе". Ассоциативная сущность, связывающая Student и Group. Объект определяет принадлежность студента к группе."""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Студент')
    registered_since = models.DateTimeField(auto_now_add=True, null=True, verbose_name='Числится с')

    class Meta:
        verbose_name = 'Студент в группе'
        verbose_name_plural = 'Студенты в группах'

    def __str__(self):
        return '{} в группе {}'.format(self.student, self.group)


class ClassType(models.Model):
    """
    Модель "Тип занятия". Объект класса представляет собой название типа занятия:
    'Экзамен', 'Консультация', 'Урок' и т.д.
    """
    name = models.CharField(max_length=10, verbose_name='Название')

    class Meta:
        verbose_name = 'Тип занятия'
        verbose_name_plural = 'Типы занятий'

    def __str__(self):
        return '{}'.format(self.name)


class Class(models.Model):
    """
    Модель "Занятие". Объект класса содержит полную информацию о занятии, в том числе
    информацию о группе, преподавателе, предмете, типе занятия.
    """
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='Преподаватель')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
    when = models.DateTimeField('Дата и время начала') # starts at
    hours = models.IntegerField('Длительность') # how long
    class_type = models.ForeignKey(ClassType, on_delete=models.CASCADE, verbose_name='Тип занятия')

    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'
        ordering = ['-id']

    def __str__(self):
        return '{} | {} | {} | {} | {}'.format(self.group, self.teacher, self.subject, self.when, self.class_type)

    def class_planned(self):
        """
        Проверяет, было ли занятие с такими параметрами в "учёте часов". Возвращает Boolean.
        """
        _date = self.when.date()
        _group = self.group
        _teacher = self.teacher
        _subject = self.subject
        th = TrainingHours.objects.filter(group=_group, teacher=_teacher, subject=_subject, date=_date)
        if th:
            return True
        else:
            return False

    def hours_match_limit(self):
        """
        Проверяет, что сумма часов добавляемых занятий не превышает лимит из "учета часов" Возвращает Boolean.
        """
        _date = self.when.date()
        _group = self.group
        _teacher = self.teacher
        _subject = self.subject
        th = TrainingHours.objects.filter(group=_group, teacher=_teacher, subject=_subject, date=_date)
        classes = Class.objects.filter(when=self.when)
        hours_th = th.aggregate(Sum('hours'))["hours__sum"]
        hours_classes = classes.aggregate(Sum('hours'))["hours__sum"]
        plus_hours = self.hours
        if not self.id:
            if hours_classes + plus_hours <= hours_th:
                return True
            else:
                return False
        if self.id:
            minus_hours = getattr(Class.objects.get(pk=self.id), 'hours')
            if hours_classes + plus_hours - minus_hours <= hours_th:
                return True
            else:
                return False

    def clean(self, *args, **kwargs):
        if not self.class_planned():
            raise ValidationError('Занятие с такими параметрами не было запланировано в учёте часов!')
        if not self.hours_match_limit():
            raise ValidationError('Сумма часов занятий превышает запланированную в учёте часов! Измените "Учёт часов" или "Занятия".')


class Comission(models.Model):
    """
    Модель "Комиссия". Класс предусмотрен для хранения информации о комисии занятий типа "Экзамен".
    Объект класса связывает экзамен (Class) и сотрудника (Worker).
    """
    exam = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name='Экзамен')
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, verbose_name='Сотрудник')

    class Meta:
        verbose_name = 'Член комиссии'
        verbose_name_plural = 'Члены комиссии'

    def __str__(self):
        return 'Сотрудник {} в комиссии экзамена {}'.format(self.worker, self.exam)


class Grade(models.Model):
    """
    Модель "Оценка". Объекты класса -- отметки оценки/ посещения, зависит от поля grade_type.
    Привязаны к занятию и студенту, имеют отметку об авторстве.
    Поля grade и attendance оба имеют значения по умолчанию, но в расчетах используется только одно.
    """
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name='Занятие')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Студент')
    GRADE_TYPES = [
        ('g', 'оценка'),
        ('a', 'посещение')
    ]
    grade_type = models.CharField('Оценка / Посещение', max_length=1, choices=GRADE_TYPES, default='g')
    grade = models.IntegerField('Оценка', blank=True, default=0)
    ATTENDANCES = [
        ('0', 'пропустил'),
        ('1', 'посетил')
    ]
    attendance = models.CharField('Посещение', max_length=1, choices=ATTENDANCES, default='0', blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор оценки')
    created_at = models.DateTimeField('Дата и время создания', auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'

    def __str__(self):
        return '{} за занятие {} студента {}'.format(self.get_grade_type_display(), self.class_id, self.student)
    
    def student_class_match(self):
        """Проверяет, относится ли студент к группе, для которой проводилось занятие."""
        _group = self.class_id.group
        _student = self.student
        _members = Student.objects.filter(membership__group=_group)
        if _student in _members:
            return True
        else:
            return False

    def attendance_exist(self):
        """Проверяет, проставлено ли уже посещение этого занятия студенту, чтобы не дублировать посещение."""
        _type = self.grade_type
        _student = self.student
        _class = self.class_id
        if _type == 'a' and not self.id:
            if Grade.objects.filter(grade_type=_type, student=_student, class_id=_class):
                return True

    def clean(self, *args, **kwargs):
        if not self.student_class_match():
            raise ValidationError('Выбранного студента нет в группе, у которой проводилось занятие!')
        if self.attendance_exist():
            raise ValidationError('Посещение этого занятия студентом уже отмечено!')


class TrainingHours(LifecycleModel):
    """
    Модель "Учёт часов", служит для планирования и отслеживания часов преподавания.
    Объект -- комбинация из группы, преподавателя, предмета, типа времени (рабочее / личное),
    даты, часов преподавания, отметки о редактировании. Также закрепляет преподавателя за группами и наоборот.
    """
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='Преподаватель')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
    TIME_TYPES = [
        ('w', 'рабочее'),
        ('p', 'личное')
    ]
    time_type = models.CharField(max_length=1, choices=TIME_TYPES, default='w', verbose_name='Тип времени')
    date = models.DateField('Дата')
    hours = models.IntegerField('Часы')
    created_at = models.DateTimeField('Дата и время создания', auto_now_add=True, null=True)
    who_changed_last = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name='Последний редактировал', null=True)

    class Meta:
        verbose_name = 'Учёт часов'
        verbose_name_plural = 'Учёт часов'

    def __str__(self):
        return '{}, {}, {} час.'.format(self.teacher, self.date, self.hours)
    
    @hook(AFTER_CREATE, when='created_at', has_changed=True)
    @hook(AFTER_UPDATE, when_any=['group', 'teacher', 'subject', 'time_type', 'date', 'hours'], has_changed=True)
    def traininghours_versions(self):
        """Добавляет версию объекта в формате json во вспомогательную таблицу при добавлении записи либо обновлении значащих полей."""
        th = TrainingHours.objects.get(pk=self.pk)
        serializer = TrainingHoursSerializer(th)
        changes = DraftTH(
            content=serializer.data,
            who_changed=self.who_changed_last,
            )
        changes.save()

    def subject_in_program(self):
        """Проверяет, чтобы предмет и группа согласовались."""
        _program = self.group.program
        if InProgram.objects.filter(program=_program, subject=self.subject):
            return True
        else:
            return False

    def check_working_dates(self):
        """Проверяет соответсвие часов преполдавания производственному календарю (WorkingDates)."""
        _date = self.date
        _teacher = self.teacher
        norm_hours = getattr(WorkingDates.objects.filter(date=_date)[0], 'in_hours')
        th = TrainingHours.objects.filter(teacher=_teacher, date=_date)
        hours_th = th.aggregate(Sum('hours'))["hours__sum"] if th.aggregate(Sum('hours'))["hours__sum"] else 0
        plus_hours = self.hours
        if not self.id:
            if hours_th + plus_hours <= norm_hours:
                return True
            else:
                return False
        if self.id:
            minus_hours = getattr(TrainingHours.objects.get(pk=self.id), 'hours')
            if hours_th + plus_hours - minus_hours <= norm_hours:
                return True
            else:
                return False

    def clean(self, *args, **kwargs):
        if not self.subject_in_program():
            raise ValidationError('Такого предмета нет в программе у выбранной группы!')
        if not self.check_working_dates():
            raise ValidationError('Сумма часов преподавания данного преподавателя превышает нормативную ("Производственный календарь") для выбранной даты!')


class CalendarPlan(models.Model):
    """
    Модель "Календарный план". Объекты класса -- календарные планы, а именно -- основная информация о плане.
    Календарный план  состоит из трёх моделей (CalendarPLan, InCP, CPDetails), что моделирует структуру оригинального документа.
    """
    year = models.CharField('Год', max_length=4)
    RELEVANCES = [
        ('0', 'нерелевантный'),
        ('1', 'релевантный')
    ]
    relevance = models.CharField('Релевантность', max_length=1, choices=RELEVANCES, default='1')
    created_at = models.DateTimeField('Дата и время создания', auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Календарный план'
        verbose_name_plural = 'Календарные планы'
        ordering = ['-created_at']

    def __str__(self):
        return 'Календарный план {}, {}'.format(self.year, self.get_relevance_display())

    def one_relevant(self):
        """Проверяет, что в таблице существует только один объект релевантного календарного плана."""
        relevant_plans = CalendarPlan.objects.filter(relevance='1')
        if self.relevance == '1':
            if not self.id:
                if len(relevant_plans) == 0:
                    return True
                else:
                    return False
            elif self.id:
                if self.id == relevant_plans[0].id:
                    return True
                else:
                    return False
        else:
            return True

    def clean(self, *args, **kwargs):
        if not self.one_relevant():
            raise ValidationError('Может существовать только один релевантный календарный план. Измените relevance текущего релевантного плана.')


class InCP(models.Model):
    """
    Модель "Календарный план (элемент). Объект класса содержит информацию об одной программе из календарного плана,
    по сути -- строка из плана, но без деталей по месяцам. Один CalendarPlan содержит много InCP.
    """
    program = models.ForeignKey(Program, on_delete=models.CASCADE, verbose_name='Программа')
    calendarplan = models.ForeignKey(CalendarPlan, on_delete=models.CASCADE, verbose_name='Календарный план')
    people_number = models.IntegerField('Число людей')
    groups_number = models.IntegerField('Число групп')

    class Meta:
        verbose_name = 'Календарный план (элемент)'
        verbose_name_plural = 'Календарные планы (элементы)'
        ordering = ['-id']

    def __str__(self):
        return '{}, {}, {}, ({})'.format(self.program, self.people_number, self.groups_number, self.calendarplan)
    
    def program_once(self):
        """Проверяет, что программа из календарного плана не дублируется."""
        cp = self.calendarplan
        existing_incps = InCP.objects.filter(calendarplan=cp)
        if not self.id and existing_incps.filter(program=self.program):
            return False
        else:
            return True

    def clean(self, *args, **kwargs):
        if not self.program_once():
            raise ValidationError('В данном календарном плане уже была указана эта программа.')
        if self.calendarplan.relevance == '0':
            raise ValidationError('Вы пытаетесь добавить запись в нерелевантный план.')


class CPDetails(models.Model):
    """
    Модель "Календарный план (детали)". Каждый объект класса детализирует какой-либо элемент (InCP) календарного плана,
    то есть содержит информацию о числе групп по программе в определенный месяц.
    """
    incp = models.ForeignKey(InCP, on_delete=models.CASCADE, verbose_name='Соответствующий элемент плана')
    MONTHS = [
        ('1', 'Январь'),
        ('2', 'Февраль'),
        ('3', 'Март'),
        ('4', 'Апрель'),
        ('5', 'Май'),
        ('6', 'Июнь'),
        ('7', 'Июль'),
        ('8', 'Август'),
        ('9', 'Сентябрь'),
        ('10', 'Октябрь'),
        ('11', 'Ноябрь'),
        ('12', 'Декабрь')
    ]
    month = models.CharField('Месяц', max_length=2, choices=MONTHS, default='1')
    groups_number = models.IntegerField('Число групп')

    class Meta:
        verbose_name = 'Календарный план (детали)'
        verbose_name_plural = 'Календарные планы (детали)'
        ordering = ['-id']

    def __str__(self):
        return 'Детали: {}, {} групп ({})'.format(self.get_month_display(), self.groups_number, self.incp)

    def month_once(self):
        """Проверяет, что каждый месяц в CPDetails, относящихся к одному InCP, упомянут единожды."""
        incp = self.incp
        existing_cpds = CPDetails.objects.filter(incp=incp)
        if not self.id and existing_cpds.filter(month=self.month):
            return False
        else:
            return True
    
    def clean(self, *args, **kwargs):
        if not self.month_once():
            raise ValidationError('Для данной программы в плане уже указано число групп в этом месяце.')
        if self.incp.calendarplan.relevance == '0':
            raise ValidationError('Вы пытаетесь добавить запись в нерелевантный план.')


class TrainingPlan(LifecycleModel):
    """
    Модель "Учебный план". Объекты класса -- учебные планы, а именно -- основная информация о плане.
    Учебный план  состоит из трёх моделей (TrainingPLan, InTP, TPDetails), что моделирует структуру оригинального документа.
    """
    year = models.CharField('Год', max_length=4)
    STATUSES = [
        ('0', 'неактивен'),
        ('1', 'активен')
    ]
    status = models.CharField('Статус', max_length=1, choices=STATUSES, default='1')
    RELEVANCES = [
        ('0', 'черновик'),
        ('1', 'утверждённый')
    ]
    relevance = models.CharField('Релевантность', max_length=1, choices=RELEVANCES, default='0')
    created_at = models.DateTimeField('Дата и время создания', auto_now_add=True, null=True)
    calendarplan = models.ForeignKey(CalendarPlan, on_delete=models.CASCADE, verbose_name='Календарный план')
    who_changed_last = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name='Последний редактировал', null=True)

    class Meta:
        verbose_name = 'Учебный план'
        verbose_name_plural = 'Учебные планы'
        ordering = ['-created_at']

    def __str__(self):
        return 'Учебный план {}, {}, {}'.format(self.year, self.get_relevance_display(), self.get_status_display())

    @hook(AFTER_CREATE, when='created_at', has_changed=True)
    @hook(AFTER_UPDATE, when_any=['year', 'status', 'relevance', 'calendarplan'], has_changed=True)
    def trainingplan_versions(self):
        """Добавляет версию объекта в формате json во вспомогательную таблицу при добавлении записи либо обновлении значащих полей."""
        tp = TrainingPlan.objects.get(pk=self.pk)
        serializer = TrainingPlanSerializer(tp)
        changes = DraftTP(
            content=serializer.data,
            who_changed=self.who_changed_last,
            )
        changes.save()


class InTP(LifecycleModel):
    """
    Модель "Учебный план (элемент). Объект класса содержит информацию об одной группе из учебного плана
    (совокупность объектов -- список конкретных групп). Один TrainingPlan содержит много InTP.
    """
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа')
    trainingplan = models.ForeignKey(TrainingPlan, on_delete=models.CASCADE, verbose_name='Учебный план')
    created_at = models.DateTimeField('Дата и время создания', auto_now_add=True, null=True)
    who_changed_last = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name='Последний редактировал', null=True)

    class Meta:
        verbose_name = 'Учебный план (элемент)'
        verbose_name_plural = 'Учебные планы (элементы)'
        ordering = ['-created_at']

    def __str__(self):
        return '{}, {} ({})"'.format(self.group, self.group.program, self.trainingplan)
    
    @hook(AFTER_CREATE, when='created_at', has_changed=True)
    @hook(AFTER_UPDATE, when_any=['group', 'trainingplan'], has_changed=True)
    def intp_versions(self):
        """Добавляет версию объекта в формате json во вспомогательную таблицу при добавлении записи либо обновлении значащих полей."""
        intp = InTP.objects.get(pk=self.pk)
        serializer = InTPSerializer(intp)
        changes = DraftInTP(
            content=serializer.data,
            who_changed=self.who_changed_last,
            )
        changes.save()

    def program_in_CP(self):
        """Проверяет, что программа, добавляемая в учебный план, существует в соответствующем календарном."""
        program = self.group.program.id
        cp = self.trainingplan.calendarplan
        incps = InCP.objects.filter(calendarplan=cp)
        programs = incps.values('program')
        programs_id = [i["program"] for i in programs]
        if program in programs_id:
            return True
        else:
            return False
    
    def program_n_times(self):
        """Проверяет, что число добавленных групп одной программы не превышает нормативное."""
        program = self.group.program.id
        cp = self.trainingplan.calendarplan
        incps = InCP.objects.filter(calendarplan=cp)
        intps = InTP.objects.filter(trainingplan=self.trainingplan)
        n = getattr(incps.filter(program=program)[0], 'groups_number') # нормативное число групп для программы
        m = len(intps.filter(group__program__id=program)) # сколько уже групп этой программы
        if not self.id:
            if m + 1 <= n:
                return True
            else:
                return False
        else:
            return True

    def clean(self, *args, **kwargs):
        if not self.program_in_CP():
            raise ValidationError('Вы пытаетесь добавить в учебный план группу с программой, которая не предусмотрена в календарном плане.')
        if not self.program_n_times():
            raise ValidationError('Нельзя добавить в учебный план больше групп этой программы, чем есть в календарном плане.')


class TPDetails(LifecycleModel):
    """
    Модель "Учебный план (детали)". Каждый объект класса детализирует какой-либо элемент (InTP) учебного плана,
    то есть содержит информацию о числе часов обучения у группы в определенный месяц.
    """
    intp = models.ForeignKey(InTP, on_delete=models.CASCADE, verbose_name='Соответствующий элемент плана')
    MONTHS = [
        ('1', 'Январь'),
        ('2', 'Февраль'),
        ('3', 'Март'),
        ('4', 'Апрель'),
        ('5', 'Май'),
        ('6', 'Июнь'),
        ('7', 'Июль'),
        ('8', 'Август'),
        ('9', 'Сентябрь'),
        ('10', 'Октябрь'),
        ('11', 'Ноябрь'),
        ('12', 'Декабрь')
    ]
    month = models.CharField('Месяц', max_length=2, choices=MONTHS, default='1')
    hours = models.IntegerField('Часы')
    created_at = models.DateTimeField('Дата и время создания', auto_now_add=True, null=True)
    who_changed_last = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name='Последний редактировал', null=True)

    class Meta:
        verbose_name = 'Учебный план (детали)'
        verbose_name_plural = 'Учебные планы (детали)'
        ordering = ['-created_at']

    def __str__(self):
        return 'Детали: {}, {} час. ({})'.format(self.month, self.hours, self.intp)

    @hook(AFTER_CREATE, when='created_at', has_changed=True)
    @hook(AFTER_UPDATE, when_any=['intp', 'month', 'hours'], has_changed=True)
    def tpdetails_versions(self):
        """Добавляет версию объекта в формате json во вспомогательную таблицу при добавлении записи либо обновлении значащих полей."""
        tpd = TPDetails.objects.get(pk=self.pk)
        serializer = TPDetailsSerializer(tpd)
        changes = DraftTPDetails(
            content=serializer.data,
            who_changed=self.who_changed_last,
            )
        changes.save()


### Таблицы для хранения версий учебных планов и учёта часов в JSON и сериализаторы для заполнения content

class DraftTP(models.Model):
    """Объекты класса DraftTP-- версии объектов класса TrainingPlan в формате json."""
    created_at = models.DateTimeField('Дата и время создания', auto_now_add=True, null=True)
    content = jsonfield.JSONField()
    who_changed = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name='Последний редактировал')
    
    class Meta:
        verbose_name = 'Версия учебного плана'
        verbose_name_plural = 'Версии учебных планов'


class DraftInTP(models.Model):
    """Объекты класса DraftInTP-- версии объектов класса InTP в формате json."""
    created_at = models.DateTimeField('Дата и время создания', auto_now_add=True)
    content = jsonfield.JSONField()
    who_changed = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name='Последний редактировал')

    class Meta:
        verbose_name = 'Версия элемента учебного плана'
        verbose_name_plural = 'Версии элементов учебных планов'


class DraftTPDetails(models.Model):
    """Объекты класса DraftTPDetails-- версии объектов класса TPDetails в формате json."""
    created_at = models.DateTimeField('Дата и время создания', auto_now_add=True)
    content = jsonfield.JSONField()
    who_changed = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name='Последний редактировал')
    
    class Meta:
        verbose_name = 'Версия деталей учебного плана'
        verbose_name_plural = 'Версии деталей учебных планов'


class DraftTH(models.Model):
    """Объекты класса DraftTH-- версии объектов класса TrainingHours в формате json."""
    created_at = models.DateTimeField('Дата и время создания', auto_now_add=True)
    content = jsonfield.JSONField()
    who_changed = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name='Последний редактировал')

    class Meta:
        verbose_name = 'Версия учёта часов'
        verbose_name_plural = 'Версии учёта часов'


class TrainingPlanSerializer(serializers.ModelSerializer):
     class Meta:
        model = TrainingPlan
        fields = '__all__'


class InTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = InTP
        fields = '__all__'


class TPDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TPDetails
        fields = '__all__'


class TrainingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingHours
        fields = '__all__'

###


class ScolarshipNorm(models.Model):
    """
    Модель "Норма стипендии". Объект класса содержит информацию о соответствии параметров, которые влияют на стипендию,
    и суммы стипендии, которая полагается студенту, соответствующему условиям.
    При расчётах параметры из нормы сравниваются с записями из Ejournal и Group.
    """
    lower = models.FloatField('Нижняя граница балла', blank=True, default=0.0)
    higher = models.FloatField('Верхняя граница балла', blank=True, default=0.0)
    amount = models.IntegerField('Количество руб./мес.')
    description = models.CharField('Описание из документа', max_length=400, blank=True)
    VALID = [
        ('0', 'не валидна'),
        ('1', 'валидна')
    ]
    if_valid = models.CharField(max_length=1, choices=VALID, default='1', verbose_name="Валидность")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, verbose_name='Программа')
    PERIOD_TYPES = [
        ('t', 'теория'),
        ('p', 'практика')
    ]
    period = models.CharField(max_length=1, choices=PERIOD_TYPES, default='t', verbose_name='Период обучения')

    class Meta:
        verbose_name = 'Норма стипендии'
        verbose_name_plural = 'Нормы стипендий'


class SalaryNorm(models.Model):
    """
    Модель "Норма зарплаты". Объект класса сопоставляет значащие параметры и тариф зарплаты преподавателя при таких параметрах.
    При расчётах параметры из нормы сравниваются с записями из TrainingHours и Worker.
    """
    TIME_TYPES = [
        ('w', 'рабочее'),
        ('p', 'личное')
    ]
    time_type = models.CharField(max_length=1, choices=TIME_TYPES, default='w', verbose_name='Тип времени')
    EDU_LEVELS = [
        ('0', 'Высшее'),
        ('1', 'СПО'),
        ('2', 'Среднее Общее')
    ]
    education_level = models.CharField('Уровень образования', max_length=1, choices=EDU_LEVELS, default='0')
    STUDENTS = [
        ('0', 'рабочие и учащиеся Технической школы'),
        ('1', 'руководители среднего звена, специалисты, служащие'),
        ('2', 'руководители подразделений')
    ]
    students = models.CharField(max_length=1, choices=STUDENTS, default='0', verbose_name='Контингент учащихся')
    amount = models.IntegerField('Тариф руб./ч.')
    VALID = [
        ('0', 'не валидна'),
        ('1', 'валидна')
    ]
    if_valid = models.CharField(max_length=1, choices=VALID, default='1', verbose_name='Валидность')

    class Meta:
        verbose_name = 'Норма зарплаты'
        verbose_name_plural = 'Нормы зарплат'


class HoursNorm(models.Model):
    """Модель "Норма часов". Объект хранит нормы часов преподавания в различные промежутки времени.
    Например, 8 часов в день -- норма часов для дня. На данный момент TrainingHours не валидируется по HoursNorm, а только по WorkingDates."""
    PERIODS = [
        ('y', 'год'),
        ('m', 'месяц'),
        ('d', 'день')
    ]
    period = models.CharField(max_length=1, choices=PERIODS, default='d')
    amount = models.IntegerField()

    class Meta:
        verbose_name = 'Норма часов'
        verbose_name_plural = 'Нормы часов'


class WorkingDates(LifecycleModel):
    """Модель "Производственный календарь". Хранит информацию обо всемх рабочих и нерабочих датах, а также эквиваленты в часах для каждого дня."""
    date = models.DateField()
    WORKING = [
        ('Пр', 'праздник'), 
        ('Сб', 'выходная суббота'),
        ('Вх', 'выходной/воскресенье'),
        ('8', 'полный рабочий день'),
        ('7', 'сокращенный рабочий день')
    ]
    if_working = models.CharField(max_length=2, choices=WORKING)
    in_hours = models.IntegerField(blank=True, default=0)

    class Meta:
        verbose_name = 'День в календаре'
        verbose_name_plural = 'Производственный календарь'
        ordering = ['-date']
    
    @hook(BEFORE_CREATE, when='if_working', has_changed=True)
    @hook(BEFORE_UPDATE, when='if_working', has_changed=True)
    def add_hours_eqv(self):
        """Автоматически добавляет эквивалент в часах в зависимости от выбранного значения "if_working" """
        if self.if_working == '8':
            self.in_hours = 8
        elif self.if_working == '7':
            self.in_hours = 7
        else:
            self.in_hours == 0
