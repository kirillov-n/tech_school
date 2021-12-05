# Generated by Django 3.2 on 2021-05-27 22:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tech_school_app', '0013_auto_20210526_1302'),
        ('survey_app', '0029_alter_testfrom_testfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='testfrom',
            name='pers',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tech_school_app.personalinfo'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='testfrom',
            name='testfield',
            field=models.CharField(choices=[('1', 1), ('2', 2), ('2', 2), ('2', 2), ('2', 2)], max_length=1),
        ),
    ]
