from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeliveryPartnerViewSet

router = DefaultRouter()
router.register(r'partner', DeliveryPartnerViewSet, basename='delivery-partner')

urlpatterns = [
    path('', include(router.urls)),
]
