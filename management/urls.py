from django.urls import path
from . import views

urlpatterns = [
    #upon entering main page show calendar
    path('', views.calendar_view, name='calendar'),
]