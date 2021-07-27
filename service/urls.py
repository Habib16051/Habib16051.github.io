from django.urls import path
from service import views

urlpatterns = [
    path('service/', views.services, name='service'),
]