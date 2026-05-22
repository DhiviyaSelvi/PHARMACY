from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicineViewSet, InventoryViewSet

router = DefaultRouter()
router.register(r'list', MedicineViewSet)
router.register(r'inventory', InventoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
