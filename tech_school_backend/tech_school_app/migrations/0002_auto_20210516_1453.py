# Generated by Django 3.2 on 2021-05-16 14:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tech_school_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salarynorm',
            name='course_type',
        ),
        migrations.AddField(
            model_name='salarynorm',
            name='salary_level',
            field=models.IntegerField(choices=[(1, '1 level'), (2, '2 level'), (3, '3 level'), (4, '4 level')], default=1),
        ),
        migrations.AddField(
            model_name='scolarshipnorm',
            name='period',
            field=models.CharField(choices=[('t', 'theory'), ('p', 'practice')], default='t', max_length=1),
        ),
        migrations.AddField(
            model_name='scolarshipnorm',
            name='program',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tech_school_app.program'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='workingdates',
            name='in_hours',
            field=models.IntegerField(blank=True, default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='workingdates',
            name='if_working',
            field=models.CharField(choices=[('Пр', 'праздник'), ('Сб', 'выходная суббота'), ('Вх', 'выходной/воскресенье'), ('8', 'полный рабочий день'), ('7', 'сокращенный рабочий день')], max_length=2),
        ),
    ]
