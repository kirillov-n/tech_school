from django.contrib import admin
from tech_school_app.models import *
from django.urls import path
from datetime import datetime, timedelta


@admin.register(PersonalInfo)
class PersonalInfoAdmin(admin.ModelAdmin):
    list_display = (
        'surname',
        'name',
        'patronymic',
        'phone',
        'email',
        'birth_date',
    )

    list_filter = (
        'surname',
        'name',
        'patronymic',
        'birth_date',
    )


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'worker',
        'position',
        'is_active',
    )
    list_filter = (
        'user',
        'worker',
        'position',
        'is_active',
    )


class NextTrainingFilter(admin.SimpleListFilter):
    """Собственный фильтр для даты следующего обучения (next_training) сотрудника."""
    title = 'Следующее обучение'
    parameter_name = 'next_training'

    def lookups(self, request, model_admin):
        return [
            ('expired', 'Дата уже прошла'),
            ('this_year', 'В этом году'),
            ('this_month', 'В этом месяце'),
            ('next_year', 'В следующем году'),
            ('next_6', 'В ближайшие полгода')
        ]
    def queryset(self, request, queryset):
        current_date = datetime.today()
        if self.value()=="expired":
            return queryset.filter(next_training__lt=current_date)
        if self.value()=="this_year":
            return queryset.filter(next_training__year=current_date.year)
        if self.value()=="this_month":
            return queryset.filter(next_training__month=current_date.month)
        if self.value()=="next_year":
            return queryset.filter(next_training__year=current_date.year+1)
        if self.value()=="next_6":
            return queryset.filter(next_training__lte=current_date+timedelta(days=180), next_training__gte=current_date)
        else:
            return queryset.all()


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = (
        'personal_info',
        'department',
        'education_level',
        'last_training',
        'next_training',
        'notes',
        'available'
    )
    list_filter = (
        'personal_info',
        'department__name',
        'education_level',
        'notes',
        'available',
        NextTrainingFilter,
    )


@admin.register(WorkerChanges)
class WorkerChangesAdmin(admin.ModelAdmin):
    readonly_fields = (
        '__str__',
        'worker',
        'field_name',
        'new_value',
        'changed_at',
    )
    list_filter = (
        'worker',
        'changed_at',
        'field_name',
    )


@admin.register(PersonalInfoChanges)
class PersonalInfoChangesAdmin(admin.ModelAdmin):
    readonly_fields = (
        '__str__',
        'personal_info',
        'field_name',
        'new_value',
        'changed_at',
    )
    list_filter = (
        'personal_info__worker',
        'changed_at',
        'field_name',
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'worker',
        'text',
        'created_at',
        'status',
        'importance',
    )
    list_filter = (
        'worker',
        'created_at',
        'status',
        'importance'
    )
    readonly_fields = (
        'worker',
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'upload_date',
        'scan',
        'relevance',
        'worker',
        'doc_date',
    )

    list_filter = (
        'name',
        'upload_date',
        'relevance',
        'worker',
        'doc_date',
    )