from django.contrib import admin
from django.urls import path
from django.utils import timezone

from tech_school_backend.settings import EMAIL_HOST_USER

from .models import *
from .views import *


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'survey_type',
        'number_in_survey'
    )
    list_filter = (
        'survey_type',
    )
    ordering = (
        'survey_type',
        'number_in_survey'
    )


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = (
        'who',
        'group',
        'is_active',
        'created_at'
    )

    list_filter = (
        'who',
        'group',
        'is_active',
        'created_at',
    )

    readonly_fields = (
        'created_at',
    )

    def get_readonly_fields(self, request, obj=None):
        """
        Функция, не позволяющая редактировать поля "who" и "group".
        """
        if obj:
            return ['who', 'group']
        return self.readonly_fields

    def get_urls(self):
        """
        Функция, добавляющее расширенное окно в админ-панели для данной модели.
        """
        urls = super().get_urls()
        return urls + [path("surveyresults_view", SurveyResultView.as_view(), name="surveyresults_view"),]
    

@admin.register(InSurvey)
class InSurveyAdmin(admin.ModelAdmin):
    list_display = (
        'survey',
        'question'
    )
    list_filter = (
        'survey',
    )


@admin.register(SurveyWho)
class SurveyWhoAdmin(admin.ModelAdmin):
    list_display =(
        'student',
        'worker',
        'survey'
    )
    list_filter = (
        'survey',
        'worker',
        'student'
    )


@admin.register(Slug)
class SlugAdmin(admin.ModelAdmin):
    list_display = (
        'surveywho',
        'slug',
        'link',
        'created_at',
        'if_sent',
        'sent_at'
    )
    list_filter = (
        'surveywho',
        'created_at',
        'if_sent',
        'sent_at'
    )
    readonly_fields = (
        'slug',
        'link',
        'created_at',
        'if_sent',
        'sent_at'
    )
    actions = [
        'to_send_selected',
    ]
    
    def has_delete_permission(self, request, obj=None):
        """
        Функция, запрещающая удалять записи самостоятельно.
        Они удаляются автоматически при изменении статуса опроса на "не активен".
        """
        return False

    @admin.action(description='Отправить рассылку')
    def to_send_selected(self, request, queryset):
        """
        Функция, отправляющая рассылку лицам, которые должны пройти опрос,
        вместе с индивидуальной ссылкой на этот опрос.
        """
        for i in range(len(queryset)):
            slug = queryset.values()[i]
            if slug['if_sent']=='0':
                Slug.objects.filter(pk=slug['id']).update(if_sent = '1')
                Slug.objects.filter(pk=slug['id']).update(sent_at = timezone.now())
                surveywho = SurveyWho.objects.filter(pk=slug['surveywho_id']).values()[0]
                print(surveywho['worker_id'])
                if surveywho['worker_id']==None:
                    student = Student.objects.filter(pk=surveywho['student_id']).values()[0]
                    pi = PersonalInfo.objects.filter(pk=student['personal_info_id']).values()[0]
                    title = 'Опрос от технической школы ГУП Петербургский Метрополитен'
                    text = 'Здравствуйте, '+str(pi['name'])+' '+str(pi['patronymic'])+'!\n\nПожалуйста, пройдите опрос по ссылке: '+slug['link']+'\n\nС уважением,\nАдминистратор\n"Техническая школа" ГУП "Петербургский Метрополитен"\n'+'techschool.backend@mail.ru'
                    send_mail(title, text, EMAIL_HOST_USER, [str(pi['email'])])
                else:
                    student = Student.objects.filter(pk=surveywho['student_id']).values()[0]
                    worker = Worker.objects.filter(pk=surveywho['worker_id']).values()[0]
                    pis = PersonalInfo.objects.filter(pk=student['personal_info_id']).values()[0]
                    piw = PersonalInfo.objects.filter(pk=worker['personal_info_id']).values()[0]
                    title = 'Опрос от технической школы ГУП Петербургский Метрополитен: оцените учащегося '+str(pis['surname'])+' '+str(pis['name'])+' '+str(pis['patronymic'])
                    text = 'Здравствуйте, '+str(piw['name'])+' '+str(piw['patronymic'])+'!\n\nПожалуйста, пройдите опрос об учащемся '+str(pis['surname'])+' '+str(pis['name'])+' '+str(pis['patronymic'])+'\nпо ссылке: '+slug['link']+'\n\nС уважением,\nАдминистратор\n"Техническая школа" ГУП "Петербургский Метрополитен"\n'+'techschool.backend@mail.ru'
                    send_mail(title, text, EMAIL_HOST_USER, [str(piw['email'])])
            

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        'surveywho',
        'question',
        'answer'
    )
    list_filter = (
        'surveywho',
        'question'
    )