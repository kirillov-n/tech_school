from rest_framework import serializers
from tech_school_app.models import *
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer): # для просмотра поля у Teacher
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInfo
        fields = ['surname', 'name', 'patronymic', 'phone']


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'


class DetailWorkerSerializer(WorkerSerializer): # расширенный Worker
    personal_info = PersonalInfoSerializer(read_only=True)


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'


class DetailTeacherSerializer(TeacherSerializer): # Teacher в контексте электронного журнала
    user = UserSerializer(read_only=True)
    worker = WorkerSerializer(read_only=True)
    # position = serializers.CharField(source="get_position_display")
    is_active = serializers.CharField(source="get_is_active_display")


class ClassTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassType
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
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
    program = ProgramSerializer(read_only=True)
    status = serializers.CharField(source="get_status_display")
    edu_level = serializers.CharField(source="get_edu_level_display")
    students = DetailStudentSerializer(read_only=True, many=True)


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'


class DetailClassSerializer(ClassSerializer):
    group = GroupSerializer(read_only=True)
    teacher = DetailTeacherSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    class_type = ClassTypeSerializer(read_only=True)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class DetailGroupSerializer(GroupSerializer):
    program = ProgramSerializer(read_only=True)
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


class ComissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comission
        fields = '__all__'


class DetailComissionSerializer(ComissionSerializer):
    exam = DetailClassSerializer(read_only=True)
    worker = DetailWorkerSerializer(read_only=True)


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'


class DetailGradeSerializer(GradeSerializer):
    class_id = DetailClassSerializer(read_only=True)
    student = DetailStudentSerializer(read_only=True)
    grade_type = serializers.CharField(source="get_grade_type_display")
    attendance = serializers.CharField(source="get_attendance_display")