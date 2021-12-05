from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.admin.sites import site
from django.forms import modelformset_factory

from tech_school_app.models import *
from .models import *


def record_answer(request, pk, slug):
    """
    Функция, отвечающая за составление формы для опроса.
    Информация о том, кто и какой опрос проходит, получается из индивидуальной ссылки.
    Соответственно, поля с опросом и самими вопросами предзаполняются автоматически,
    а пользователь вносит только ответы из выпадающего списка.
    Все записи вносятся в таблицу Answer.
    """
    context = {}
    slug = Slug.objects.filter(id=pk).values()[0]
    surveywho = SurveyWho.objects.filter(id=slug['surveywho_id']).values()[0]
    student = Student.objects.filter(pk=surveywho['student_id']).values()[0]
    survey = Survey.objects.filter(pk=surveywho['survey_id']).values()[0]
    if survey['who']=='t':
        worker = Worker.objects.filter(pk=surveywho['worker_id']).values()[0]
        context["worker"] = Worker.objects.filter(pk=surveywho['worker_id'])[0]
    insurvey = InSurvey.objects.filter(survey_id=survey['id']).values()
    questions = []
    for ins in insurvey:
        questions.append(Question.objects.filter(id=ins['question_id']).order_by('survey_type','number_in_survey').values()[0])
    
    context["survey"] = Survey.objects.filter(pk=surveywho['survey_id'])[0]
    context["student"] = Student.objects.filter(pk=surveywho['student_id'])[0]
    context["questions"] = questions
    
    prefill = []
    surveywho_instance = SurveyWho.objects.get(id=surveywho['id'])
    for q in questions:
        prefill_dict = {
            'surveywho':'',
            'question':''
        }
        question_instance = Question.objects.get(id=q['id'])
        prefill_dict.update({
            'surveywho': surveywho_instance,
            'question': question_instance
        })
        prefill.append(prefill_dict)
        print(prefill)

    AnswerModelFormSet = modelformset_factory(Answer, fields='__all__', extra=len(questions))
    formset = AnswerModelFormSet(
        queryset=Answer.objects.none(),
        initial=prefill
    )
    for form in formset:
        form.fields['surveywho'].widget.attrs['readonly'] = 'readonly'
        form.fields['question'].widget.attrs['readonly'] = 'readonly'
    
    if request.method == 'POST':
        formset = AnswerModelFormSet(request.POST, initial = prefill)
        if formset.is_valid():
            formset.save()

    context['formset'] = formset
    
    return render(request, 'recordanswer.html', context)


class SurveyResultView(TemplateView):
    """
    Результаты опросов.
    Все полученные ответы обрабатываются в соответствии с методиками опросов,
    результаты выводятся по шкалам психологических и профессиональных факторов.
    Считаются средние для каждого студента и каждого результата.
    Определяются отстающие студенты, чьи результаты ниже нормы или ниже среднего.
    """
    template_name = "surveyresult.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(site.each_context(self.request))

        context['headings_CLEI'] = [
            'CLEI',
            'SE',
            'TO',
            'AS',
            'CI',
            'ER',
            'CC',
            'Среднее'
        ]
        context['description_CLEI'] = 'SE – Академическая самоэффективность; TO – Управление временем и самоорганизация; AS – Управление академическим стрессом; CI – Участие в жизни ТШ; ER – Эмоциональная реакция на учёбу в ТШ; CC – Общение в классе'
        context['headings_Big5'] = [
            'Big5 Преподаватель',
            'Студент',
            'Привязанность — Обособленность',
            'Самоконтроль – Импульсивность',
            'Эмоциональная неустойчивость – Устойчивость',
            'Экспрессия – Практичность',
            'Среднее'
        ]
        context['headings_360'] = [
            '360 Преподаватель',
            'Студент',
            'P1',
            'P2',
            'P3',
            'P4',
            'P5',
            'P6',
            'P7',
            'P8',
            'P9',
            'среднее'
        ]
        context['description_360'] = 'P1 – Целеустремлённость; P2 – Инициативность; P3 – Исполнительность; P4 – Гибкость; P5 – Лояльность к ТШ; P6 – Командная работа; P7 – Интерес к работе; P8 – Организованность и пунктуальность; P9 – Постановка и контроль задач'

        # результаты выводятся только после вбыора пользователем группы
        group = self.request.GET.get("group")
        groups = Group.objects.all()
        context["groups"] = groups

        queryset = Survey.objects.all()
        if group:
            context['group'] = group
            context['group_name'] = Group.objects.filter(id=group).values()[0]['name']

            # заданные нормы CLEI
            norms = {
                'SE': 0.7556,
                'TO': 0.4230,
                'AS': 0.4286,
                'CI': 0.5234,
                'ER': 0.6336,
                'CC': 0.5140,
                'mean': 0.5514,
            }
            context['norms'] = norms

            queryset = queryset.filter(group__id=group)
            members = Membership.objects.filter(group__id=group).values()
            surveys = Survey.objects.filter(group_id=group).values()
            
            CLEI = []
            Big5 = []
            PROF = []

            for survey in surveys:
                # если опрос для преподавателя
                if survey['who']=='t':
                    surveywho = SurveyWho.objects.filter(survey_id = survey['id']).values()
                    
                    for sw in surveywho:
                        Big5_values = {
                            'worker':'',
                            'student':'',
                            'A':'',
                            'C':'',
                            'N':'',
                            'O':'',
                            'mean':''
                        }
                        PROF_values = {
                            'worker':'',
                            'student':'',
                            'P1':'',
                            'P2':'',
                            'P3':'',
                            'P4':'',
                            'P5':'',
                            'P6':'',
                            'P7':'',
                            'P8':'',
                            'P9':'',
                            'mean':''
                        }
                        student = Student.objects.filter(id = sw['student_id']).values()[0]
                        worker = Worker.objects.filter(id = sw['worker_id']).values()[0]
                        personal_info_s = PersonalInfo.objects.filter(id = student['personal_info_id']).values()[0]
                        personal_info_w = PersonalInfo.objects.filter(id = worker['personal_info_id']).values()[0]
                        answers = Answer.objects.filter(surveywho_id = sw['id']).values()

                        A, C, N, O = [], [], [], []
                        for answer in answers:
                            questions = Question.objects.filter(id = answer['question_id']).values()

                            for question in questions:
                                # опросник Big Five
                                if question['survey_type'] == '1':
                                    if int(question['number_in_survey']) in [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60]:
                                        if answer['question_id']==question['id']:
                                            A.append(6 - int(answer['answer']))
                                    if int(question['number_in_survey']) in [1, 5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53, 57]:
                                        if answer['question_id']==question['id']:
                                            C.append(6 - int(answer['answer']))
                                    if int(question['number_in_survey']) in [2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 50, 54, 58]:
                                        if answer['question_id']==question['id']:
                                            N.append(6 - int(answer['answer']))
                                    if int(question['number_in_survey']) in [3, 7, 11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59]:
                                        if answer['question_id']==question['id']:
                                            O.append(6 - int(answer['answer']))

                                # опросник CLEI
                                if question['survey_type'] == '2':
                                    if int(question['number_in_survey']) in [1]:
                                        if answer['question_id']==question['id']:
                                            P1 = int(answer['answer'])
                                    if int(question['number_in_survey']) in [2]:
                                        if answer['question_id']==question['id']:
                                            P2 = int(answer['answer'])
                                    if int(question['number_in_survey']) in [3]:
                                        if answer['question_id']==question['id']:
                                            P3 = int(answer['answer'])
                                    if int(question['number_in_survey']) in [4]:
                                        if answer['question_id']==question['id']:
                                            P4 = int(answer['answer'])
                                    if int(question['number_in_survey']) in [5]:
                                        if answer['question_id']==question['id']:
                                            P5 = int(answer['answer'])
                                    if int(question['number_in_survey']) in [6]:
                                        if answer['question_id']==question['id']:
                                            P6 = int(answer['answer'])
                                    if int(question['number_in_survey']) in [7]:
                                        if answer['question_id']==question['id']:
                                            P7 = int(answer['answer'])
                                    if int(question['number_in_survey']) in [8]:
                                        if answer['question_id']==question['id']:
                                            P8 = int(answer['answer'])
                                    if int(question['number_in_survey']) in [9]:
                                        if answer['question_id']==question['id']:
                                            P9 = int(answer['answer'])
                                
                        A_value = (sum(A)/15 - 1) / 4
                        A_value = round(A_value, 4)
                        C_value = (sum(C)/15 - 1) / 4
                        C_value = round(C_value, 4)
                        N_value = (sum(N)/15 - 1) / 4
                        N_value = round(N_value, 4)
                        O_value = (sum(O)/15 - 1) / 4
                        O_value = round(O_value, 4)
                        student_str = str(student['personnel_num'])+' '+str(personal_info_s['surname'])+' '+str(personal_info_s['name'])+' '+str(personal_info_s['patronymic'])
                        worker_str = str(personal_info_w['surname'])+' '+str(personal_info_w['name'])+' '+str(personal_info_w['patronymic'])
                        if (A_value > 0):
                            # подсчёт среднего для полученных результатов студента
                            Big5_mean = (A_value + C_value + N_value + O_value) / 4
                            Big5_mean = round(Big5_mean, 4)
                            Big5_values.update({
                                'worker': worker_str,
                                'student': student_str,
                                'A': A_value,
                                'C': C_value,
                                'N': N_value,
                                'O': O_value,
                                'mean': Big5_mean
                            })
                            Big5.append(Big5_values)
                            PROF_mean = (P1 + P2 + P3 + P4 + P5 + P6 + P7 + P8 + P9) / 9
                            PROF_mean = round(PROF_mean, 4)
                            PROF_values.update({
                                'worker': worker_str,
                                'student': student_str,
                                'P1': P1,
                                'P2': P2,
                                'P3': P3,
                                'P4': P4,
                                'P5': P5,
                                'P6': P6,
                                'P7': P7,
                                'P8': P8,
                                'P9': P9,
                                'mean': PROF_mean
                            })
                            PROF.append(PROF_values)

                # если опрос был для студента      
                if survey['who']=='s':
                    surveywho = SurveyWho.objects.filter(survey_id = survey['id']).values()
                    for sw in surveywho:
                        CLEI_values = {
                            'student':'',
                            'SE':'',
                            'TO':'',
                            'AS':'',
                            'CI':'',
                            'ER':'',
                            'CC':'',
                            'mean':''
                        }
                        student = Student.objects.filter(id = sw['student_id']).values()[0]
                        personal_info = PersonalInfo.objects.filter(id = student['personal_info_id']).values()[0]
                        answers = Answer.objects.filter(surveywho_id = sw['id']).values()

                        SE, TO, AS, CI, ER, CC = [], [], [], [], [], []
                        for answer in answers:
                            questions = Question.objects.filter(id = answer['question_id']).values()
                            for question in questions:
                                # подсчёт CLEI
                                if int(question['number_in_survey']) in [4, 5, 22, 23, 27, 28, 30, 51, 52, 54, 57, 60]:
                                    if answer['question_id']==question['id']:
                                        SE.append(int(answer['answer']))
                                if int(question['number_in_survey']) in [6, 31, 34, 46, 50, 56, 59]:
                                    if answer['question_id']==question['id']:
                                        SE.append(6 - int(answer['answer']))
                                if int(question['number_in_survey']) in [2, 7, 35, 37, 38, 61]:
                                    if answer['question_id']==question['id']:
                                        TO.append(int(answer['answer']))
                                if int(question['number_in_survey']) in [1, 11, 24, 29, 33, 58, 62]:
                                    if answer['question_id']==question['id']:
                                        TO.append(6 - int(answer['answer']))
                                if int(question['number_in_survey']) in [3, 8, 15, 39, 43, 44]:
                                    if answer['question_id']==question['id']:
                                        AS.append(6 - int(answer['answer']))
                                if int(question['number_in_survey']) in [10, 12, 13, 17, 19, 36, 41, 48, 49]:
                                    if answer['question_id']==question['id']:
                                        CI.append(int(answer['answer']))
                                if int(question['number_in_survey']) in [16, 21, 32, 47]:
                                    if answer['question_id']==question['id']:
                                        ER.append(int(answer['answer']))
                                if int(question['number_in_survey']) in [14, 18, 20, 25, 45]:
                                    if answer['question_id']==question['id']:
                                        ER.append(6 - int(answer['answer']))
                                if int(question['number_in_survey']) in [40]:
                                    if answer['question_id']==question['id']:
                                        CC.append(int(answer['answer']))
                                if int(question['number_in_survey']) in [9, 26, 42, 53, 55]:
                                    if answer['question_id']==question['id']:
                                        CC.append(6 - int(answer['answer']))
                            
                        SE_value = (sum(SE)/19 - 1) / 4
                        SE_value = round(SE_value, 4)
                        TO_value = (sum(TO)/13 - 1) / 4
                        TO_value = round(TO_value, 4)
                        AS_value = (sum(AS)/6 - 1) / 4
                        AS_value = round(AS_value, 4)
                        CI_value = (sum(CI)/9 - 1) / 4
                        CI_value = round(CI_value, 4)
                        ER_value = (sum(ER)/9 - 1) / 4
                        ER_value = round(ER_value, 4)
                        CC_value = (sum(CC)/6 - 1) / 4
                        CC_value = round(CC_value, 4)
                        student_str = str(student['personnel_num'])+' '+str(personal_info['surname'])+' '+str(personal_info['name'])+' '+str(personal_info['patronymic'])
                        if (SE_value > 0):
                            # подсчёт среднего для полученных результатов студента
                            CLEI_mean = (SE_value+TO_value+AS_value+CI_value+ER_value+CC_value) / 6
                            CLEI_mean = round(CLEI_mean, 4)
                            CLEI_values.update({
                                'student': student_str,
                                'SE': SE_value,
                                'TO': TO_value,
                                'AS': AS_value,
                                'CI': CI_value,
                                'ER': ER_value,
                                'CC': CC_value,
                                'mean': CLEI_mean
                            })
                            CLEI.append(CLEI_values)

            context['CLEI'] = sorted(CLEI, key=lambda k: k['student'])
            context['Big5'] = sorted(Big5, key=lambda k: k['student'])
            context['PROF'] = sorted(PROF, key=lambda k: k['student'])

            if (len(CLEI) != 0):
                # подсчёт средних по группе по шкалам
                CLEI_group_SE, CLEI_group_TO, CLEI_group_AS, CLEI_group_CI, CLEI_group_ER, CLEI_group_CC = [], [], [], [], [], [] 
                CLEI_group = {
                    'SE':'',
                    'TO':'',
                    'AS':'',
                    'CI':'',
                    'ER':'',
                    'CC':''
                }         
                for i in range(len(CLEI)):
                    CLEI_group_SE.append(CLEI[i]['SE'])
                    CLEI_group_TO.append(CLEI[i]['TO'])
                    CLEI_group_AS.append(CLEI[i]['AS'])
                    CLEI_group_CI.append(CLEI[i]['CI'])
                    CLEI_group_ER.append(CLEI[i]['ER'])
                    CLEI_group_CC.append(CLEI[i]['CC'])
                
                CLEI_group.update({
                    'SE': round((sum(CLEI_group_SE)/len(CLEI)), 4),
                    'TO': round((sum(CLEI_group_TO)/len(CLEI)), 4),
                    'AS': round((sum(CLEI_group_AS)/len(CLEI)), 4),
                    'CI': round((sum(CLEI_group_CI)/len(CLEI)), 4),
                    'ER': round((sum(CLEI_group_ER)/len(CLEI)), 4),
                    'CC': round((sum(CLEI_group_CC)/len(CLEI)), 4)
                })

                context['CLEI_group'] = CLEI_group

                ave_clei_mean = []
                i = 0
                for clei_ins in CLEI:
                    ave_clei_mean.append(clei_ins['mean'])
                    i += 1
                ave_clei_mean = round(sum(ave_clei_mean) / i, 4)

                context['CLEI_ave'] = ave_clei_mean

                # поиск отстающих по CLEI
                clei_bad_norm_students = []
                clei_bad_group_students = []
                for clei_ins in CLEI:
                    if clei_ins['mean'] < norms['mean']:
                        clei_bad_norm_students.append(clei_ins['student'])
                    if clei_ins['mean'] < ave_clei_mean:
                        clei_bad_group_students.append(clei_ins['student'])
                
                context['clei_bad_norm'] = clei_bad_norm_students
                context['clei_bad_group'] = clei_bad_group_students

            if (len(Big5) != 0):
                # подсчёт средних по группе по шкалам
                Big5_group_A, Big5_group_C, Big5_group_N, Big5_group_O = [], [], [], []
                Big5_group = {
                    'A':'',
                    'C':'',
                    'N':'',
                    'O':''
                }         
                for i in range(len(Big5)):
                    Big5_group_A.append(Big5[i]['A'])
                    Big5_group_C.append(Big5[i]['C'])
                    Big5_group_N.append(Big5[i]['N'])
                    Big5_group_O.append(Big5[i]['O'])
            
                Big5_group.update({
                    'A': round((sum(Big5_group_A)/len(Big5)), 4),
                    'C': round((sum(Big5_group_C)/len(Big5)), 4),
                    'N': round((sum(Big5_group_N)/len(Big5)), 4),
                    'O': round((sum(Big5_group_O)/len(Big5)), 4)
                })

                context['Big5_group'] = Big5_group

                ave_big5_mean = []
                i = 0
                for big5_ins in Big5:
                    ave_big5_mean.append(big5_ins['mean'])
                    i += 1
                ave_big5_mean = round(sum(ave_big5_mean) / i, 4)

                context['Big5_ave'] = ave_big5_mean
                
                # поиск отстающих по Big Five
                big5_bad_group_students = []
                for big5_ins in Big5:
                    if big5_ins['mean'] < ave_big5_mean:
                        big5_bad_group_students.append(big5_ins['student'])
                
                big5_bad_group_unique = []
                for bad in big5_bad_group_students:
                    if bad not in big5_bad_group_unique:
                        big5_bad_group_unique.append(bad)

                context['big5_bad_group'] = big5_bad_group_unique

            if (len(PROF) != 0):
                # подсчёт средних по группе по шкалам
                PROF_group_1, PROF_group_2, PROF_group_3, PROF_group_4, PROF_group_5, PROF_group_6, PROF_group_7, PROF_group_8, PROF_group_9 = [], [], [], [],[], [], [], [], []
                PROF_group = {
                    'P1':'',
                    'P2':'',
                    'P3':'',
                    'P4':'',
                    'P5':'',
                    'P6':'',
                    'P7':'',
                    'P8':'',
                    'P9':''
                }         
                for i in range(len(PROF)):
                    PROF_group_1.append(PROF[i]['P1'])
                    PROF_group_2.append(PROF[i]['P2'])
                    PROF_group_3.append(PROF[i]['P3'])
                    PROF_group_4.append(PROF[i]['P4'])
                    PROF_group_5.append(PROF[i]['P5'])
                    PROF_group_6.append(PROF[i]['P6'])
                    PROF_group_7.append(PROF[i]['P7'])
                    PROF_group_8.append(PROF[i]['P8'])
                    PROF_group_9.append(PROF[i]['P9'])

                PROF_group.update({
                    'P1': round((sum(PROF_group_1)/len(PROF)), 4),
                    'P2': round((sum(PROF_group_2)/len(PROF)), 4),
                    'P3': round((sum(PROF_group_3)/len(PROF)), 4),
                    'P4': round((sum(PROF_group_4)/len(PROF)), 4),
                    'P5': round((sum(PROF_group_5)/len(PROF)), 4),
                    'P6': round((sum(PROF_group_6)/len(PROF)), 4),
                    'P7': round((sum(PROF_group_7)/len(PROF)), 4),
                    'P8': round((sum(PROF_group_8)/len(PROF)), 4),
                    'P9': round((sum(PROF_group_9)/len(PROF)), 4)
                })

                context['PROF_group'] = PROF_group

                ave_prof_mean = []
                i = 0
                for prof_ins in PROF:
                    ave_prof_mean.append(prof_ins['mean'])
                    i += 1
                ave_prof_mean = round(sum(ave_prof_mean) / i, 4)
                
                context['PROF_ave'] = ave_prof_mean

                # поиск отстающих по методике 360 градусов
                prof_bad_group_students = []
                for prof_ins in PROF:
                    if prof_ins['mean'] < ave_prof_mean:
                        prof_bad_group_students.append(prof_ins['student'])
                
                prof_bad_group_unique = []
                for bad in prof_bad_group_students:
                    if bad not in prof_bad_group_unique:
                        prof_bad_group_unique.append(bad)

                context['prof_bad_group'] = prof_bad_group_unique
        
        return context