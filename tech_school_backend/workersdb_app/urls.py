from django.urls import path, include

from .views import *

urlpatterns = [
    path('workers/all', WorkerViewSet.as_view({"get": "list"})),
    path('workers/<int:pk>', WorkerViewSet.as_view({"get": "retrieve"})),
    path('workers/update/<int:pk>', WorkerViewSet.as_view({"patch": "partial_update"})),
    path('workers/create', WorkerViewSet.as_view({"post": "create"})),
    path('teachers/all', TeacherViewSet.as_view({"get": "list"})),
    path('teachers/<int:pk>', TeacherViewSet.as_view({"get": "retrieve"})),
    path('teachers/update/<int:pk>', TeacherViewSet.as_view({"patch": "partial_update"})),
    path('teachers/create', TeacherViewSet.as_view({"post": "create"})),
    path('wchanges/<int:worker>', WorkerChangesView.as_view()),
    path('pchanges/<int:worker>', PersonalInfoChangesView.as_view()),
    path('personalinfo/update/<int:pk>', PersonalInfoViewSet.as_view({"patch": "partial_update"})),
    path('personalinfo/create', PersonalInfoViewSet.as_view({"post": "create"})),
    path('departments/update/<int:pk>', DepartmentViewSet.as_view({"patch": "partial_update"})),
    path('departments/create', DepartmentViewSet.as_view({"post": "create"})),
    path('workers/check/<int:delta>', CheckWorkersDataView.as_view()),
    path('workers/filter', FilterWorkersView.as_view()),
    path('workers/notifications/create', CreateNotificationView.as_view()),
    path('workers/license/all', FilterLicensesView.as_view()),
    path('workers/license/update/<int:pk>', LicenseViewSet.as_view({"patch": "partial_update"})),
    path('workers/license/create', LicenseViewSet.as_view({"post": "create"})),


]