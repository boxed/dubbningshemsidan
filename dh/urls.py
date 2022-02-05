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
from django.contrib import admin
from django.urls import path
from iommi import Table

from dh.base.models import (
    Actor,
    Show,
    Role,
    MetaDataObject,
)
from dh.views import (
    index,
    metadata_object,
    role,
    search,
    show,
)

urlpatterns = [
    path('', index),
    path('search/', search),
    path('actors/', Table(auto__model=Actor).as_view()),
    path(
        'actors/<actor_pk>/',
        Table(
            title=lambda params, **_: params.actor.name,
            auto__model=Role,
            rows=lambda params, **_: params.actor.roles.all(),
            columns__actor__include=False,
            columns__index__include=False,
        ).as_view()
    ),
    path('shows/', Table(auto__model=Show).as_view()),
    path('shows/<show_pk>/', show),
    path('shows/not-parsed/', Table(
        auto__rows=Show.objects.filter(successful_parse=False),
        columns__name__cell__url=lambda row, **_: row.get_absolute_url(),
    ).as_view()),
    path('roles/', Table(auto__model=Role).as_view()),
    path('roles/<role_pk>/', role),
    path('metadata/', Table(
        auto__model=MetaDataObject,
        columns__name__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__name__filter__include=True,
        columns__name__filter__freetext=True,
    ).as_view()),
    path('metadata/<meta_data_object_pk>/', metadata_object),
    path('admin/', admin.site.urls),
]
