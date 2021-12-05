from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, viewsets, status
from django.views.generic import TemplateView
from django.contrib.admin.sites import site
from django.db.models import Avg, Count, Q, Sum

from tech_school_app.models import *
from .serializers import *


class ProgramViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet для модели Program. List и Retrieve используют расширенный сериализатор.
    """
    queryset = Program.objects.all()

    def get_serializer_class(self):

        if self.action in ["list", "retrieve"]:

            return DetailProgramSerializer
        
        return ProgramSerializer


class StudentViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet для модели Student. List и Retrieve используют расширенный сериализатор.
    """
    queryset = Student.objects.all()

    def get_serializer_class(self):

        if self.action in ["list", "retrieve"]:

            return DetailStudentSerializer
        
        return StudentSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet для модели Group. List и Retrieve используют расширенный сериализатор.
    """
    queryset = Group.objects.all()

    def get_serializer_class(self):

        if self.action in ["list", "retrieve"]:

            return DetailGroupSerializer
        
        return GroupSerializer


class CalendarPlanViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet для модели CalendarPlan. List и Retrieve используют расширенный сериализатор.
    """
    queryset = CalendarPlan.objects.all()

    def get_serializer_class(self):

        if self.action in ["list", "retrieve"]:

            return DetailCalendarPlanSerializer
        
        return CalendarPlanSerializer


class InCPsView(generics.ListAPIView): # InCP, относящиеся к CP
    """
    ListAPIView для просмотра записей InCP.
    Параметр cp (int) -- фильтрует записи InCP по принадлежности к CP.
    """
    queryset = InCP.objects.all()
    serializer_class = DetailInCPSerializer

    def get(self, request, **kwargs):
        cp = kwargs.get('cp')

        queryset = self.queryset.filter(calendarplan__id=cp)

        serialized_data = [
            self.serializer_class(row).data for row in queryset
        ]

        return Response(data=serialized_data, status=status.HTTP_200_OK)


class CPDetailsView(generics.ListAPIView): # CPDetails, относящиеся к CP
    """
    ModelViewSet для модели CPDetails. List и Retrieve используют расширенный сериализатор.
    Параметр cp (int) -- фильтрует записи CPDetails по принадлежности к CP.
    """
    queryset = CPDetails.objects.all()
    serializer_class = DetailCPDetailsSerializer

    def get(self, request, **kwargs):
        cp = kwargs.get('cp')

        queryset = self.queryset.filter(incp__calendarplan__id=cp)

        serialized_data = [
            self.serializer_class(row).data for row in queryset
        ]

        return Response(data=serialized_data, status=status.HTTP_200_OK)


class TrainingPlanViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet для модели TrainingPlan. List и Retrieve используют расширенный сериализатор.
    """
    queryset = TrainingPlan.objects.all()

    def get_serializer_class(self):

        if self.action in ["list", "retrieve"]:

            return DetailTrainingPlanSerializer
        
        return TrainingPlanSerializer


class InTPsView(generics.ListAPIView): # InTP, относящиеся к TP
    """
    ListAPIView для просмотра записей InTP.
    Параметр tp (int) -- фильтрует записи InTP по принадлежности к TP.
    """
    queryset = InTP.objects.all()
    serializer_class = DetailInTPSerializer
    
    def get(self, request, **kwargs):
        tp = kwargs.get('tp')

        queryset = self.queryset.filter(trainingplan__id=tp)

        serialized_data = [
            self.serializer_class(row).data for row in queryset
        ]

        return Response(data=serialized_data, status=status.HTTP_200_OK)


class TPDetailsView(generics.ListAPIView): # TPDetails, относящиеся к TP
    """
    ModelViewSet для модели TPDetails. List и Retrieve используют расширенный сериализатор.
    Параметр tp (int) -- фильтрует записи TPDetails по принадлежности к TP.
    """
    queryset = TPDetails.objects.all()
    serializer_class = DetailTPDetailsSerializer

    def get(self, request, **kwargs):
        tp = kwargs.get('tp')

        queryset = self.queryset.filter(intp__trainingplan__id=tp)

        serialized_data = [
            self.serializer_class(row).data for row in queryset
        ]

        return Response(data=serialized_data, status=status.HTTP_200_OK)


class InCPViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet для модели InCP. List и Retrieve используют расширенный сериализатор.
    """
    queryset = InCP.objects.all()

    def get_serializer_class(self):

        if self.action in ["list", "retrieve"]:

            return DetailInCPSerializer
        
        return InCPSerializer


class InTPViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet для модели InTP. List и Retrieve используют расширенный сериализатор.
    """
    queryset = InTP.objects.all()

    def get_serializer_class(self):

        if self.action in ["list", "retrieve"]:

            return DetailInTPSerializer
        
        return InTPSerializer


class CPDetailsViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet для модели CPDetails. List и Retrieve используют расширенный сериализатор.
    """
    queryset = CPDetails.objects.all()

    def get_serializer_class(self):

        if self.action in ["list", "retrieve"]:

            return DetailCPDetailsSerializer
        
        return CPDetailsSerializer


class TPDetailsViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet для модели TPDetails. List и Retrieve используют расширенный сериализатор.
    """
    queryset = TPDetails.objects.all()

    def get_serializer_class(self):

        if self.action in ["list", "retrieve"]:

            return DetailTPDetailsSerializer
        
        return TPDetailsSerializer


# Views для админ-панели
class CalendarPlanView(TemplateView):
    """
    Представление "Календарный план (Таблица)", расширяющее админ-панель.
    Служит для отображения составного календарного плана в виде общей таблицы.
    По умолчанию отображается последний релевантный план, но может быть выбран любой.
    Параметры для фильтрации:
        cplan (int) -- календарный план (pk)
        ctype (int) -- тип обучения (из программы) для фильтрации строк внутри плана
    """
    template_name = "calendarplan.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(site.each_context(self.request))

        context["headings"] = [
                'Программа',
                'Вид обучения',
                'Кол-во чел.',
                'Кол-во групп',
                'январь',
                'февраль',
                'март',
                'апрель',
                'май',
                'июнь',
                'июль',
                'август',
                'сентябрь',
                'октябрь',
                'ноябрь',
                'декабрь',
            ]
        
        plans = CalendarPlan.objects.all() # все календарные планы
        context["plans"] = plans   

        ctypes = CourseType.objects.all() # все типы занятий
        context["ctypes"] = ctypes

        cplan = self.request.GET.get("cplan")
        ctype = self.request.GET.get("ctype")

        calendarplans = CalendarPlan.objects.all()
        calendarplan = calendarplans.filter(relevance='1')[0] # последний релевантный календарный план

        if cplan:
            calendarplan = calendarplans.filter(id=cplan)[0]

        incps = InCP.objects.filter(calendarplan=calendarplan)

        if ctype:
            incps = incps.filter(program__course_type=ctype)
        
        # суммы столбцов в таблице, в том числе суммы по месяцам
        groups_sum = incps.aggregate(Sum("groups_number"))["groups_number__sum"]
        people_sum = incps.aggregate(Sum("people_number"))["people_number__sum"]
        months_sum = [{'month': f'{k}', 'sum': 0} for k in range(1, 13)]

        rows = []

        for incp in incps:
            _row = {}
            _row["incp"] = incp

            cpds = CPDetails.objects.filter(incp=incp).order_by('month')
            _row["cpds"] = []

            for m in range(1, 13):
                cpd = cpds.filter(month=str(m))
                num = getattr(cpd[0], 'groups_number') if cpd else 0
                months_sum[m-1]["sum"] += num
                _row["cpds"].append({'month': str(m), 'groups_number': num})

            rows.append(_row)
        
        plan = {'cp': calendarplan, 'people_sum': people_sum, 'groups_sum': groups_sum, 'months_sum': months_sum, 'rows': rows}
        context["plan"] = plan

        return context
    

class TrainingPlanView(TemplateView):
    """
    Представление "Учебный план (Таблица)", расширяющее админ-панель.
    Служит для отображения составного учебного плана в виде общей таблицы.
    По умолчанию отображается последний валидный план, но может быть выбран любой.
    Параметры для фильтрации:
        tplan (int) -- учебный план (pk)
        ctype (int) -- тип обучения (из программы) для фильтрации строк внутри плана
    """
    template_name = "trainingplan.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(site.each_context(self.request))

        context["headings"] = [
                'Программа',
                'Группа',
                'январь',
                'февраль',
                'март',
                'апрель',
                'май',
                'июнь',
                'июль',
                'август',
                'сентябрь',
                'октябрь',
                'ноябрь',
                'декабрь',
                'ИТОГО'
            ]

        plans = TrainingPlan.objects.all() # все учебные планы
        context["plans"] = plans

        ctypes = CourseType.objects.all() # все типы обучения
        context["ctypes"] = ctypes

        tplan = self.request.GET.get("tplan")
        ctype = self.request.GET.get("ctype")

        trainingplans = TrainingPlan.objects.all()
        trainingplan = trainingplans.filter(status='1')[0] # последний активный план

        if tplan:
            trainingplan = trainingplans.filter(id=tplan)[0]
        
        intps = InTP.objects.filter(trainingplan=trainingplan)

        if ctype:
            intps = intps.filter(group__program__course_type=ctype)

        # суммы столбцов в таблице, в том числе суммы по месяцам
        hours_sum = intps.values('group').annotate(x_sum=Sum('tpdetails__hours'))
        months_sum = [{'month': f'{k}', 'sum': 0} for k in range(1, 13)]
        total_sum = intps.aggregate(total=Sum('tpdetails__hours'))["total"]

        rows = []

        for intp in intps:
            _row = {}
            _row["intp"] = intp
            _row["x_sum"] = hours_sum.filter(group=intp.group)[0]['x_sum']

            tpds = TPDetails.objects.filter(intp=intp).order_by('month')
            _row["tpds"] = []

            for m in range(1, 13):
                tpd = tpds.filter(month=str(m))
                num = getattr(tpd[0], 'hours') if tpd else 0
                months_sum[m-1]["sum"] += num
                _row["tpds"].append({'month': str(m), 'hours': num})

            rows.append(_row)
        
        plan = {'tp': trainingplan, 'months_sum': months_sum, 'total_sum': total_sum, 'rows': rows}
        context['plan'] = plan

        return context   
