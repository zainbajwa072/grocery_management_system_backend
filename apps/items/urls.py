from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, ItemTypeViewSet

router = DefaultRouter()
router.register(r'types', ItemTypeViewSet)
router.register(r'', ItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
