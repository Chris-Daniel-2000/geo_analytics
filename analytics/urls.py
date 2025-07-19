from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Homepage
    path('process', views.process_file, name='process_file'),  # File processing
    path('procedures/', views.procedures, name='procedures'),  
]
