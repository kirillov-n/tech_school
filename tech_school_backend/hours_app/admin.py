from django.contrib import admin
from tech_school_app.models import *
from django.urls import path

from tech_school_app.views import WorkingDatesView
from .views import *


@admin.register(TrainingHours)
class TrainingHoursAdmin(admin.ModelAdmin):
    list_display = (
        'group',
        'teacher',
        'subject',
        'time_type',
        'date',
        'hours',
        'created_at',
        'who_changed_last',
    )

    list_filter = (
        'group',
        'teacher',
        'subject',
        'time_type',
        'date',
    )

    readonly_fields = ('who_changed_last', 'created_at',)

    date_hierarchy = 'date'

    def save_model(self, request, obj, form, change):
        obj.who_changed_last = request.user
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        return urls + [path("hours_view", HoursView.as_view(), name="hours_view"),
                       path("hoursyear_view", HoursYearView.as_view(), name="hoursyear_view")]


@admin.register(DraftTH)
class DraftTHDetails(admin.ModelAdmin):
    list_display = (
        'content',
        'created_at',
        'who_changed',
    )

    list_filter = ('created_at', 'who_changed', 'content',)

    readonly_fields = (
        'content',
        'created_at',
        'who_changed',
    )


admin.site.register(HoursNorm)


@admin.register(WorkingDates)
class WorkingDatesAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'if_working',
        'in_hours',
    )

    list_filter = (
        'date',
        'if_working',
    )

    date_hierarchy = 'date'

    readonly_fields = ('in_hours',)

    def get_urls(self):
        urls = super().get_urls()
        return urls + [path("workingdates_view", WorkingDatesView.as_view(), name="workingdates_view")]
