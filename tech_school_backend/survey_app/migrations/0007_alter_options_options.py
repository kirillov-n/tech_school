# Generated by Django 3.2 on 2021-05-24 19:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey_app', '0006_auto_20210524_1936'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='options',
            options={'verbose_name': 'Вариант ответа', 'verbose_name_plural': 'Варианты ответа'},
        ),
    ]
