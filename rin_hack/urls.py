"""rin_hack URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from web.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', main_page, name='main_page'),
    url(r'^statistic/$', statistic_page, name='statistic_page'),
    url(r'^map/$', map_page, name='map_page'),
    url(r'^api/location/$', location_json, name='location_json'),
    url(r'^api/insert/$', insert_record, name='insert_record'),
    url(r'^api/delete/$', delete_record, name='delete_record'),
]
