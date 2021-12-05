from django.contrib import admin
from tech_school_app.models import *
from django.contrib.auth.models import User
from django.urls import path
from .views import CalendarPlanView, TrainingPlanView


@admin.register(CalendarPlan)
class CalendarPlanAdmin(admin.ModelAdmin):
    list_display = (
        'year',
        'relevance',
        'created_at',
    )

    readonly_fields = ('created_at',)

    list_filter = (
        'year',
        'relevance',
        'created_at',
    )

    def get_urls(self):
        urls = super().get_urls()
        return urls + [path("calendarplan_view", CalendarPlanView.as_view(), name="calendarplan_view")]


@admin.register(InCP)
class InCPAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'program',
        'calendarplan',
        'people_number',
        'groups_number',
    )

    list_filter = ('calendarplan',)


@admin.register(CPDetails)
class CPDetailsAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'incp',
        'month',
        'groups_number',
    )

    list_filter = (
        'incp',
        'incp__calendarplan',
    )



@admin.register(TrainingPlan)
class TrainingPlanAdmin(admin.ModelAdmin):
    list_display = (
        'year',
        'status',
        'relevance',
        'created_at',
        'calendarplan',
        'who_changed_last',
    )
    
    list_filter = (
        'year',
        'status',
        'relevance',
        'created_at',
        'calendarplan',
    )

    readonly_fields = ('created_at', 'who_changed_last',)

    def save_model(self, request, obj, form, change):
        obj.who_changed_last = request.user
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        return urls + [path("trainingplan_view", TrainingPlanView.as_view(), name="trainingplan_view")]


@admin.register(InTP)
class InTPAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'group',
        'trainingplan',
    )

    list_filter = ('trainingplan',)

    readonly_fields=('who_changed_last', 'created_at',)

    def save_model(self, request, obj, form, change):
        obj.who_changed_last = request.user
        super().save_model(request, obj, form, change)


@admin.register(TPDetails)
class TPDetailsAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'intp',
        'month',
        'hours',
    )

    list_filter = (
        'intp',
        'intp__trainingplan',
    )

    readonly_fields=('who_changed_last', 'created_at', )

    def save_model(self, request, obj, form, change):
        obj.who_changed_last = request.user
        super().save_model(request, obj, form, change)


@admin.register(DraftTP)
class DraftTPAdmin(admin.ModelAdmin):
    list_display = (
        'content',
        'created_at',
        'who_changed',
    )

    list_filter = ('created_at', 'who_changed', 'content', )

    readonly_fields = (
        'content',
        'created_at',
        'who_changed',
    )


@admin.register(DraftInTP)
class DraftInTPAdmin(admin.ModelAdmin):
    list_display = (
        'content',
        'created_at',
        'who_changed',
    )

    list_filter = ('created_at', 'who_changed', 'content', )

    readonly_fields = (
        'content',
        'created_at',
        'who_changed',
    )


@admin.register(DraftTPDetails)
class DraftTPDetails(admin.ModelAdmin):
    list_display = (
        'content',
        'created_at',
        'who_changed',
    )

    list_filter = ('created_at', 'who_changed', 'content', )

    readonly_fields = (
        'content',
        'created_at',
        'who_changed',
    )


admin.site.register(Subject)

admin.site.register(Program)

admin.site.register(InProgram)

admin.site.register(CourseType)

admin.site.register(Student)

admin.site.register(Group)

admin.site.register(Membership)