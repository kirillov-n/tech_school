import pandas as pd
from tech_school_app.models import *
from django.core.files import File

"""Скрипт для единоразового запуска в shell, чтобы спарсить данные преподавателей и загрузить их в БД."""

df = pd.read_excel('row/workers.xlsx')

def parse_dates(row):
    pp_last, pq_last = row["pp_last"], row["pq_last"]
    if (pp_last is not pd.NaT) and (pq_last is not pd.NaT):
        last_date = max(pp_last, pq_last)
    else:
        last_date = pq_last if pq_last is not pd.NaT else pp_last
    
    pp_next, pq_next = row["pp_next"], row["pq_next"]
    if (pp_next is not pd.NaT) and (pq_next is not pd.NaT):
        next_date = min(pp_next, pq_next)
    else:
        next_date = pq_next if pq_next is not pd.NaT else pp_next
    
    return last_date, next_date


def parse_info(i):
    row = df.iloc[i]
    _department = row["department"]
    if not Department.objects.filter(name=_department):
        d = Department(name=_department)
        d.save()
    _d = Department.objects.filter(name=_department)[0]
    _surname, _name, _patronymic = row["full_name"].split()
    if not PersonalInfo.objects.filter(surname=_surname, name=_name, patronymic=_patronymic):
        p = PersonalInfo(surname=_surname, name=_name, patronymic=_patronymic)
        p.save()
    _p = PersonalInfo.objects.filter(surname=_surname, name=_name, patronymic=_patronymic)[0]
    
    edu_dict = {'Высшее': '0', 'СПО': '1', 'Среднее Общее': '2'}

    level = row["education_level"]
    _notes = row["notes"]
    
    last_date, next_date = parse_dates(row)

    if not Worker.objects.filter(personal_info=_p.pk):
        w = Worker(personal_info=_p, department=_d, education_level=edu_dict[level], last_training=last_date, next_training=next_date, notes=_notes, available="1")
        w.save()
    _w = Worker.objects.filter(personal_info=_p.pk)[0]

    return _w


for i in range(len(df)):
    parse_info(i)


def parse_docs(i):
    row = df.iloc[i]

    _surname, _name, _patronymic = row["full_name"].split()
    print(f'Лицензии сотрудника {_surname} {_name} {_patronymic}')
    _p = PersonalInfo.objects.filter(surname=_surname, name=_name, patronymic=_patronymic)[0]
    _w = Worker.objects.filter(personal_info=_p.pk)[0]

    d_name, pp_name, pq_name = row["d_name"], row["pp_name"], row["pq_name"]

    PATHS = {
        'd': f'row/d/{d_name}',
        'pp': f'row/pp/{pp_name}',
        'pq': f'row/pq/{pq_name}'
    }

    TITLES = {
        'd': 'Диплом об образовании',
        'pp': "Диплом о переподготовке",
        'pq': "Удостоверение о повышении квалификации"
    }

    DATES = {
        'd': "",
        'pp': "pp_date",
        'pq': "pq_date"
    }

    def create_license(name, dtype, _w):
        f = ""
        try:
            f = open(PATHS[dtype], 'rb')
        except FileNotFoundError:
            print("File not found. FileNotFoundError occured.")
        if f:
            _scan = File(f)
            if DATES[dtype]:
                lcns = License(name=TITLES[dtype], scan=_scan, worker=_w, relevance="1", doc_date=row[DATES[dtype]])
            else:
                lcns = License(name=TITLES[dtype], scan=_scan, worker=_w, relevance="1")
            lcns.save()
            f.close()
            print(lcns)

    if type(d_name) == str:
        create_license(d_name, 'd', _w)
    
    if type(pp_name) == str:
        create_license(pp_name, 'pp', _w)
            
    if type(pq_name) == str:
        create_license(pq_name, 'pq', _w)
    
    return
