"""doctool URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from trim import urls as trims

from . import views

urlpatterns = [

]

urlpatterns += trims.paths_dict(views, {
        'GenericFileView':('file', 'view/file/<str:pk>/'),
        'GenericDirView':('dir', 'view/dir/<str:pk>/'),
        'ProjectListView': ('project-list', ''),
        'ProjectDetailView': ('project-detail', 'project/<str:pk>/'),
    },
    safe_prefix=False
)
