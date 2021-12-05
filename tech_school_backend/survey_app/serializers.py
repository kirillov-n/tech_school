from rest_framework import serializers
from tech_school_app.models import *
from survey_app.models import *
from django.contrib.auth.models import User


# serializers for required tech_school_app models

class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalInfo
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class WorkerSerializer(serializers.ModelSerializer):
    personal_info = PersonalInfoSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    education_level = serializers.CharField(source = 'get_education_level_display')
    available = serializers.CharField(source = 'get_available_display')
    class Meta:
        model = Worker
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    personal_info = PersonalInfoSerializer(read_only=True)
    education_status = serializers.CharField(source = 'get_education_status_display')
    from_stuff = serializers.CharField(source = 'get_from_stuff_display')
    class Meta:
        model = Student
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    students = StudentSerializer(read_only=True, many=True)
    status = serializers.CharField(source = 'get_status_display')
    class Meta:
        model = Group
        fields = ['name', 'students', 'status']


# serializers for survey_app models

class QuestionSerializer(serializers.ModelSerializer):
    survey_type = serializers.CharField(source='get_survey_type_display')
    class Meta:
        model = Question
        fields = '__all__'


"""class AnswerSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    worker = WorkerSerializer(read_only=True)
    question = QuestionSerializer(read_only=True)
    answer = serializers.CharField(source='get_answer_display')
    class Meta:
        model = Answer
        fields = '__all__'


class CreateAnswerSerializer(serializers.Serializer):
    answers = serializers.JSONField()

    def validate_answers(self, answers):
        if not answers:
            raise serializers.Validationerror("Answers must be not null.")
        return answers

    def save(self):
        answers = self.data['answers']
        student = self.student
        worker = self.worker
        for question_id in answers:
            question = Question.objects.get(pk=question_id)
            choices = answers[question_id]
            for choice_id in choices:
                answer = self.answer
                Answer(student=student, worker=worker, question=question, answer=answer).save()
                user.is_answer = True
                user.save()


class CreateAnswerStudentSerializer(serializers.ModelSerializer):
    answer = serializers.CharField(source='get_answer_display')
    class Meta:
        model = Answer
        fields = '__all__'"""


class SurveySerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True)
    question = QuestionSerializer(read_only=True, many=True)
    who = serializers.CharField(source='get_who_display')
    is_active = serializers.CharField(source='get_is_active_display')
    class Meta:
        model = Survey
        fields = '__all__'


class CreateSurveySerializer(serializers.ModelSerializer):
    who = serializers.CharField(source='get_who_display')
    is_active = serializers.CharField(source='get_is_active_display')
    class Meta:
        model = Survey
        fields = '__all__'


class InSurveySerializer(serializers.ModelSerializer):
    survey = SurveySerializer(read_only=True)
    question = QuestionSerializer(read_only=True)
    class Meta:
        model = InSurvey
        fields = '__all__'


class CreateInSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = InSurvey
        fields = '__all__'
