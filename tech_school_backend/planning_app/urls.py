from django.urls import path, include

from .views import *

urlpatterns = [
    path('programs/all', ProgramViewSet.as_view({"get": "list"})),
    path('programs/<int:pk>', ProgramViewSet.as_view({"get": "retrieve"})),
    path('programs/update/<int:pk>', ProgramViewSet.as_view({"patch": "partial_update"})),
    path('programs/create', ProgramViewSet.as_view({"post": "create"})),

    path('students/all', StudentViewSet.as_view({"get": "list"})),
    path('students/<int:pk>', StudentViewSet.as_view({"get": "retrieve"})),
    path('students/update/<int:pk>', StudentViewSet.as_view({"patch": "partial_update"})),
    path('students/create', StudentViewSet.as_view({"post": "create"})),

    path('groups/all', GroupViewSet.as_view({"get": "list"})),
    path('groups/<int:pk>', GroupViewSet.as_view({"get": "retrieve"})),
    path('groups/update/<int:pk>', GroupViewSet.as_view({"patch": "partial_update"})),
    path('groups/create', GroupViewSet.as_view({"post": "create"})),

    path('cps/all', CalendarPlanViewSet.as_view({"get": "list"})),
    path('cps/create', CalendarPlanViewSet.as_view({"post": "create"})),
    path('cps/update/<int:pk>', CalendarPlanViewSet.as_view({"patch": "partial_update"})),
    path('cps/in/<int:cp>', InCPsView.as_view()),
    path('cps/in/create', InCPViewSet.as_view({"post": "create"})),
    path('cps/in/update/<int:pk>', InCPViewSet.as_view({"patch": "partial_update"})),
    path('cps/details/<int:cp>', CPDetailsView.as_view()),
    path('cps/details/create', CPDetailsViewSet.as_view({"post": "create"})),
    path('cps/details/update/<int:pk>', CPDetailsViewSet.as_view({"patch": "partial_update"})),
    
    path('tps/all', TrainingPlanViewSet.as_view({"get": "list"})),
    path('tps/create', TrainingPlanViewSet.as_view({"post": "create"})),
    path('tps/update/<int:pk>', TrainingPlanViewSet.as_view({"patch": "partial_update"})),
    path('tps/in/<int:tp>', InTPsView.as_view()),
    path('tps/in/create', InTPViewSet.as_view({"post": "create"})),
    path('tps/in/update/<int:pk>', InTPViewSet.as_view({"patch": "partial_update"})),
    path('tps/details/<int:tp>', TPDetailsView.as_view()),
    path('tps/details/create', TPDetailsViewSet.as_view({"post": "create"})),
    path('tps/details/update/<int:pk>', TPDetailsViewSet.as_view({"patch": "partial_update"})),
]