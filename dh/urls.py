"""dh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from iommi import Table

from dh.base.models import (
    Actor,
    Show,
    Role,
)
from dh.views import (
    actor,
    show,
    index,
)

urlpatterns = [
    path('', index),
    path('actors/', Table(auto__model=Actor).as_view()),
    path('actors/<int:pk>/', actor),
    path('shows/', Table(auto__model=Show).as_view()),
    path('shows/<int:pk>/', show),
    path('roles/', Table(auto__model=Role).as_view()),
    url(r'^admin/', admin.site.urls),
]
