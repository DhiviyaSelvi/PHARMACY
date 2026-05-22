from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from orders.models import Order
from .services import RazorpayService

class CreateRPOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            rp_order = RazorpayService.create_razorpay_order(order)
            return Response(rp_order)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

class VerifyPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        rp_order_id = request.data.get('razorpay_order_id')
        rp_payment_id = request.data.get('razorpay_payment_id')
        rp_signature = request.data.get('razorpay_signature')

        if RazorpayService.verify_payment(rp_order_id, rp_payment_id, rp_signature):
            return Response({"status": "success"})
        return Response({"status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
