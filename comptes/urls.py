from django.urls import path
from . import views

app_name = 'comptes'

urlpatterns = [
    # Your URL patterns

    path('', views.HomeView.as_view(), name='home'),
]