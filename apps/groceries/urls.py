from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroceryViewSet

router = DefaultRouter()
router.register(r'', GroceryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
