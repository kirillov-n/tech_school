from django.contrib import admin
from tech_school_app.models import *
from django.contrib.auth.models import User
from django.urls import path
from .views import SalaryCountView, ScholarshipCountView
from django import forms

@admin.register(ScolarshipNorm)
class ScolarshipNormAdmin(admin.ModelAdmin):
    list_display = (
        'program',
        'lower',
        'higher',
        'amount',
        'if_valid',
        'period',
        'description',
    )

    list_filter = (
        'program',
        'lower',
        'higher',
        'amount',
        'if_valid',
        'period',
        'description',
    )

    def get_urls(self):
        urls = super().get_urls()
        return urls + [path("scholarshipcount_view", ScholarshipCountView.as_view(), name="scholarshipcount_view")]


@admin.register(SalaryNorm)
class SalaryNormAdmin(admin.ModelAdmin):
    list_display = (
        'time_type',
        'education_level',
        'students',
        'amount',
        'if_valid',
    )

    list_filter = (
        'time_type',
        'education_level',
        'students',
        'amount',
        'if_valid',
    )

    def get_urls(self):
        urls = super().get_urls()
        return urls + [path("salarycount_view", SalaryCountView.as_view(), name="salarycount_view")]
