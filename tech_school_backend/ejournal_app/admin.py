from django.contrib import admin
from tech_school_app.models import *
from django.contrib.auth.models import User
from django.urls import path
from .views import EjournalView, ClassesView
from django import forms


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    fieldsets = (
        ("main", {"fields": ("class_id", "student", "grade_type", "user")}),
        ("grade", {"fields": ("grade",)}),
        ("attendance", {"fields": ("attendance",)})
    )

    list_filter = (
        "class_id",
        "student",
        "grade_type",
        "created_at",
        "class_id__subject"
    )

    readonly_fields = ('user',)

    date_hierarchy = 'class_id__when'

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        return urls + [path("ejournal_view", EjournalView.as_view(), name="ejournal_view")]

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = (
        'group',
        'teacher',
        'subject',
        'when',
        'hours',
        'class_type',
    )
    list_filter = (
        'group',
        'teacher',
        'subject',
        'when',
        'class_type',
    )

    date_hierarchy = 'when'

    def get_urls(self):
        urls = super().get_urls()
        return urls + [path("classes_view", ClassesView.as_view(), name="classes_view")]

@admin.register(Comission)
class ComissionAdmin(admin.ModelAdmin):
    list_display = (
        'exam',
        'worker',
    )

    list_filter = (
        'exam',
        'worker',
    )

@admin.register(ClassType)
class ClassTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name', )