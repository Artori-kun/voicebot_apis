"""playground_site URL Configuration

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
# from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from .views.viewsets import *
from .views.user_feature_views import login2, tutorial_detail, tutorial_list, index, register, wall, success, reset


from rest_framework import routers

app_name = "main"

router = routers.DefaultRouter()
router.register('schedules', MyScheduleViewSet, 'schedules')
router.register('reminders', ReminderViewSet, 'reminders')
router.register('tasks', TaskViewSet, 'tasks')
router.register('schedule-exceptions', ScheduleInstanceExceptionViewSet, 'schedule-exceptions')
router.register('reminder-exceptions', ReminderInstanceExceptionViewSet, 'reminder-exceptions')

urlpatterns = [
    path('', include(router.urls)),
    url(r'^api/tutorials$', tutorial_list),
    url(r'^api/tutorials/(?P<pk>[0-9]+)$', tutorial_detail),
    url(r'^api/tutorials/login2', login2),
    url(r'^api/tutorials/register', register),

    url('index$', index),
    url('^register$', register),
    url('^success$', success),
    url('^reset$', reset),
    url('^wall$', wall),
]
