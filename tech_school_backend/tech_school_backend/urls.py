"""tech_school_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('main/', include('tech_school_app.urls')),
    path('workersdb/', include('workersdb_app.urls')),
    path('planning/', include('planning_app.urls')),
    path('accounting/', include('accounting_app.urls')),
    path('docs/', include('docs_app.urls')),
    path('ejournal/', include('ejournal_app.urls')),
    path('survey/', include('survey_app.urls')),
    path('hours/', include('hours_app.urls')),
    path('dashboard/', include('dashboard_app.urls')),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)