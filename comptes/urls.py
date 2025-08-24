from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import path
from .views import ResetPasswordRequestView, ResetPasswordConfirmView
#from .views import (
#    GenerateResetLinkView, PasswordResetDoneView,
#    CustomPasswordResetConfirmView
#)


app_name = 'comptes'

urlpatterns = [

    # path('', views.HomeView.as_view(), name='home'),
    path("", views.CustomLoginView.as_view(), name="login"),

    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("choisir-ecole/", views.ChoisirEcoleView.as_view(), name="choisir_ecole"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("dashboard/data/", views.DashboardDataView.as_view(), name="dashboard_data"),
    path('reset-password/', ResetPasswordRequestView.as_view(), name='reset-password-request'),
    path('reset-password-confirm/<uuid:token>/', ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
    
]