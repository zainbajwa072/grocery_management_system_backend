from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DailyIncomeViewSet

router = DefaultRouter()
router.register(r'', DailyIncomeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
