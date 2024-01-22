from django.urls import path
from rango import views

app_namr = 'rango'

urlpatterns = [
    path('', views.index, name='index')
]