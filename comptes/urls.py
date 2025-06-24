from django.urls import path
from . import views

app_name = 'comptes'

urlpatterns = [

    # path('', views.HomeView.as_view(), name='home'),
    path("", views.CustomLoginView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("choisir-ecole/", views.ChoisirEcoleView.as_view(), name="choisir_ecole"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("dashboard/data/", views.DashboardDataView.as_view(), name="dashboard_data"),
]