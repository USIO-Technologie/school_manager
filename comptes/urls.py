from django.urls import path
from . import views

app_name = 'comptes'

urlpatterns = [
    # Your URL patterns

    path('', views.HomeView.as_view(), name='home'),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("choisir-ecole/", views.ChoisirEcoleView.as_view(), name="choisir_ecole"),
]