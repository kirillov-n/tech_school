from django.db import models
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.text import slugify

from django_lifecycle import LifecycleModel, hook, AFTER_UPDATE, AFTER_CREATE

from tech_school_app.models import *
from .utils import random_string_generator

class Question(models.Model):
    """
    Модель таблицы вопросов.
    Содержит в себе текст вопроса,
    тип опроса, к которому относится,
    а также номер данного вопроса в опроснике.
    """
    text = models.TextField('Текст вопроса', blank=True)
    SURVEYS = [
        ('0', 'CLEI'),
        ('1', 'Big5'),
        ('2', '360')
    ]
    survey_type = models.CharField('Тип опроса', max_length=1, choices=SURVEYS)
    number_in_survey = models.IntegerField('Номер в опроснике')

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return '{} (№{} в {})'.format(self.text, self.number_in_survey, self.get_survey_type_display())


class Survey(LifecycleModel):
    """
    Модель таблицы опросов.
    Содержит в себе информацию о том, кому предназначается опрос,
    номер группы, студенты которой оцениваются,
    статус опроса – активен или не активен.
    """
    ROLES = [
        ('t', 'сотруднику'),
        ('s', 'учащемуся')
    ]
    who = models.CharField('Кому предназначен', max_length=1, choices=ROLES, default='s')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, verbose_name='Группа')
    ACTIVE = [
        ('0', 'не активен'),
        ('1', 'активен')
    ]
    is_active = models.CharField('Активен ли', max_length=1, choices=ACTIVE, default='1')
    created_at = models.DateTimeField('Создан', auto_now_add=True, null=True)
    questions = models.ManyToManyField(Question, through='InSurvey', verbose_name='Вопросы')

    class Meta:
        verbose_name = 'Опрос'
        verbose_name_plural = 'Опросы'

    def __str__(self):
        return 'Опрос о группе "{}" {} от {}'.format(self.group, self.get_who_display(), self.created_at)

    @hook(AFTER_CREATE)
    def create_survey_question_relation(self):
        """
        Функция соотнесение созданного опроса с вопросами,
        если опрос предназначен учащимся, то подтягиваются вопросы из CLEI,
        если опрос предназначен преподавателям, то подтягиваются вопросы из Big Five и 360.
        """
        survey = Survey.objects.filter(pk=self.pk).values()[0]

        if self.who=='t':
            questions = Question.objects.filter(survey_type__in=['1','2'])
            for q in questions:
                in_survey = InSurvey(
                    survey = self,
                    question = q
                )
                in_survey.save()
        
        if self.who=='s':
            questions = Question.objects.filter(survey_type='0')
            for q in questions:
                in_survey = InSurvey(
                    survey = self,
                    question = q
                )
                in_survey.save()
    
    @hook(AFTER_CREATE)
    def create_surveywho_relations(self):
        """
        Функция соотнесения опроса и лиц, которые должны его пройти.
        Если опрос предназначен учащимся, то создаётся связь между опросом
        и каждым членом группы через ассоциативную сущность Membership (tech_school_app).
        Если опрос предназначен преподавателю, то создаётся связь между опросом,
        каждым студентом из группы через ассоциативную сущность Membership (tech_school_app)
        и каждым преподавателем из таблицы TrainingHours (tech_school_app).
        """
        survey = Survey.objects.filter(pk=self.pk).values()[0]
        
        if self.who=='t':
            training_hours = TrainingHours.objects.filter(group=self.group).values()
            for th in training_hours:
                teacher = Teacher.objects.filter(pk=th['teacher_id']).values()[0]
                worker = Worker.objects.filter(pk=teacher['worker_id'])
                for w in worker:
                    membership = Membership.objects.filter(group=self.group).values()
                    for ms in membership:
                        student = Student.objects.filter(pk=ms['student_id'])
                        for s in student:
                            surveywho = SurveyWho(
                                student = s,
                                worker = w,
                                survey = self
                            )
                            surveywho.save()
        
        if self.who=='s':
            membership = Membership.objects.filter(group=self.group).values()
            for ms in membership:
                student = Student.objects.filter(pk=ms['student_id'])
                for s in student:
                    surveywho = SurveyWho(
                        student = s,
                        survey = self
                    )
                    surveywho.save()

    @hook(AFTER_UPDATE, when='is_active', was='1', is_now='0')
    def delete_survey_slugs(self):
        """
        Функция удаления индивидуальных ссылок на опрос после завершения опроса.
        """
        survey = Survey.objects.filter(pk=self.pk).values()[0]
        surveywho = SurveyWho.objects.filter(survey=self.pk).values()
        for sw in surveywho:
            Slug.objects.filter(surveywho=sw['id']).delete()


class InSurvey(models.Model):
    """
    Ассоциативная сущность, содержания информацию об опросе и вопросах в нём.
    Заполняется автоматически с помощью LifeCycleModel и функции create_survey_question_relation.
    """
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name='Опрос')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')

    class Meta:
        verbose_name = 'Вопрос в опросе'
        verbose_name_plural = 'Вопросы в опросах'

    def __str__(self):
        return '"{}" находится в "{}"'.format(self.question, self.survey)


class SurveyWho(LifecycleModel):
    """
    Ассоциативная сущность, содержания информацию об опросе, кто должен его пройти
    и о ком (если опрос предназначен для преподавателя).
    Заполняется автоматически с помощью LifeCycleModel и функции create_ssurveywho_relations.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='студент')
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, verbose_name='преподаватель', blank=True, null=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name='опрос')

    class Meta:
        verbose_name = 'Кому'
        verbose_name_plural = 'Кому'

    def __str__(self):
        return 'Опрос {} о {}'.format(self.worker, self.student)

    @hook(AFTER_CREATE)
    def create_slug(self):
        """
        Функция автоматического создания индивидуальнных ссылок для каждого,
        кто должен пройти опрос.
        """
        surveywho = SurveyWho.objects.filter(pk=self.pk)[0]
        slug = Slug(
            surveywho = surveywho
        )
        slug.save()


class Slug(LifecycleModel):
    """
    Модель таблицы индивидуальных ссылок.
    Содержит информацию о том, какой опрос и кто должен пройти (из ассоциативной таблицы SurveyWho),
    сгенерированную строку и состоящию из id и неё индивидуальную ссылку на опрос,
    а также данные о времени создания, статус, отправлена ссылка или нет, дату отправления.
    """
    surveywho = models.ForeignKey(
        SurveyWho, 
        on_delete=models.CASCADE, 
        verbose_name='Опрос')
    slug = models.SlugField(
        default='',
        editable=False,
        max_length=15,
        verbose_name='персональный код'
    )
    link = models.CharField(
        blank=True,
        default='',
        editable=False,
        max_length=50,
        verbose_name='персональная ссылка'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        null=True,
        verbose_name='Создан'
    )
    STATUSES = [
        ('0', 'не отправлено'),
        ('1', 'отправлено')
    ]
    if_sent = models.CharField(
         max_length=1,
         choices=STATUSES,
         default='0',
         verbose_name='Cтатус отправления'
    )
    sent_at = models.DateTimeField(
        null=True,
        blank = True,
        verbose_name='Отправлен'
    )

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'

    def __str__(self):
        return 'Ссылка опроса {}'.format(self.surveywho)

    def get_absolute_url(self):
        """
        Функция для создания индивидуальной ссылки из двух полей: id и slug.
        """
        kwargs = {
            'pk': self.id,
            'slug': self.slug
        }
        return reverse('student-pk-slug-detail', kwargs=kwargs)

    def save(self, *args, **kwargs):
        """
        Функция, автоматически генерирующая строку в поле slug при создании записи в таблице.
        """
        value = random_string_generator()
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

    @hook(AFTER_CREATE)
    def add_link(self, *args, **kwargs):
        """
        Функция, записывающся полную ссылку на опрос для записи в таблице.
        """
        value = 'http://127.0.0.1:8000/survey/'+str(self.id)+'-'+str(self.slug)+'/'
        self.link = value
        super().save(*args, **kwargs)


class Answer(models.Model):
    """
    Модель таблицы ответов.
    Содержит в себе информацию о том, кто и какой опрос (и о ком) проходит,
    сам вопрос и ответ на него.
    """
    surveywho = models.ForeignKey(SurveyWho, on_delete=models.CASCADE, verbose_name='опрос')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='вопрос')
    CHOICES = [
        ('1', 1 ),
        ('2', 2 ),
        ('3', 3 ),
        ('4', 4 ),
        ('5', 5 )
    ]
    answer = models.CharField(max_length=1, choices=CHOICES, verbose_name='ответ')
    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return 'Ответ {} на вопрос {} – {}'.format(self.surveywho, self.question, self.answer)
