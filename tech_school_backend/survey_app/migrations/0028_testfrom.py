# Generated by Django 3.2 on 2021-05-27 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey_app', '0027_auto_20210527_1906'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestFrom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('testfield', models.CharField(max_length=5)),
            ],
        ),
    ]
