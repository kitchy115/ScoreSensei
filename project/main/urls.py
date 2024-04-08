from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('showcase/', views.showcase, name='showcase'),
]
