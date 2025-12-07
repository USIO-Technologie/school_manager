"""
URL configuration for school_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),  # Django JET URLS
    path("jiwe/", admin.site.urls),
    path("profiles/", include(("app_profile.urls", "app_profile"), namespace="app_profile")),
    path("academic/", include(("app_academic.urls", "app_academic"), namespace="app_academic")),
    path("grades/", include(("app_grades.urls", "app_grades"), namespace="app_grades")),
    path("attendance/", include(("app_attendance.urls", "app_attendance"), namespace="app_attendance")),
    # Redirection de la racine vers la landing page
    path("", RedirectView.as_view(url="/profiles/landing/", permanent=False), name="root"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
