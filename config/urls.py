"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path('admin/', admin.site.urls),
        path('api/v1/auth/', include('apps.accounts.urls')),
        path('api/v1/groceries/', include('apps.groceries.urls')),
        path('api/v1/items/', include('apps.items.urls')),
        path('api/v1/income/', include('apps.income.urls')),
        
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # ReDoc UI
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

]
