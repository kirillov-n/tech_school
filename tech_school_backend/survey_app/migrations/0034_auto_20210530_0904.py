# Generated by Django 3.2 on 2021-05-30 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey_app', '0033_auto_20210530_0844'),
    ]

    operations = [
        migrations.AddField(
            model_name='slug',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Создан'),
        ),
        migrations.AddField(
            model_name='slug',
            name='sent_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Отправлен'),
        ),
    ]
