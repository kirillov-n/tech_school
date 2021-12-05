from rest_framework import serializers
from tech_school_app.models import *
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'


class DetailProgramSerializer(ProgramSerializer):
    subjects = SubjectSerializer(read_only=True, many=True)


class InProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = InProgram
        fields = '__all__'


class DetailInProgramSerializer(InProgramSerializer):
    subject = SubjectSerializer(read_only=True)
    program = ProgramSerializer(read_only=True)


class CourseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseType
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInfo
        fields = '__all__'


class DetailStudentSerializer(StudentSerializer):
    personal_info = PersonalInfoSerializer(read_only=True)
    education_status = serializers.CharField(source="get_education_status_display")
    from_staff = serializers.CharField(source="get_from_staff_display")


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class DetailGroupSerializer(GroupSerializer):
    program = DetailProgramSerializer(read_only=True)
    status = serializers.CharField(source="get_status_display")
    edu_level = serializers.CharField(source="get_edu_level_display")
    students = DetailStudentSerializer(read_only=True, many=True)


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = '__all__'


class DetailMembershipSerializer(MembershipSerializer):
    group = DetailStudentSerializer(read_only=True)
    student = DetailStudentSerializer(read_only=True)


class CalendarPlanSerializer(serializers.ModelSerializer):
     class Meta:
        model = CalendarPlan
        fields = '__all__'


class DetailCalendarPlanSerializer(CalendarPlanSerializer):
    relevance = serializers.CharField(source="get_relevance_display")


class InCPSerializer(serializers.ModelSerializer):
    class Meta:
        model = InCP
        fields = '__all__'


class DetailInCPSerializer(InCPSerializer):
    program = DetailProgramSerializer(read_only=True)
    #calendarplan = DetailCalendarPlanSerializer(read_only=True)


class CPDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPDetails
        fields = '__all__'


class DetailCPDetailsSerializer(CPDetailsSerializer):
    incp = InCPSerializer(read_only=True)
    month = serializers.CharField(source="get_month_display")


class TrainingPlanSerializer(serializers.ModelSerializer):
     class Meta:
        model = TrainingPlan
        fields = '__all__'


class DetailTrainingPlanSerializer(TrainingPlanSerializer):
    status = serializers.CharField(source="get_status_display")
    relevance = serializers.CharField(source="get_relevance_display")
    calendarplan = DetailCalendarPlanSerializer(read_only=True)
    who_changed_last = UserSerializer(read_only=True)


class InTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = InTP
        fields = '__all__'


class DetailInTPSerializer(InTPSerializer):
    group = GroupSerializer(read_only=True)
    #trainingplan = DetailTrainingPlanSerializer(read_only=True)


class TPDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TPDetails
        fields = '__all__'


class DetailTPDetailsSerializer(TPDetailsSerializer):
    intp = InTPSerializer(read_only=True)
    month = serializers.CharField(source="get_month_display")


