from django.urls import path
from .views import CreateRPOrderView, VerifyPaymentView

urlpatterns = [
    path('create-order/<int:order_id>/', CreateRPOrderView.as_view(), name='payment_create_order'),
    path('verify/', VerifyPaymentView.as_view(), name='payment_verify'),
]
