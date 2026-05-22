from django.test import TestCase
from django.contrib.auth import get_user_model
from orders.models import Order
from pharmacies.models import Pharmacy
from .models import DeliveryPartner, DeliveryAssignment, DeliveryOTP, Zone
from .services import DeliveryService
from decimal import Decimal

User = get_user_model()

class DeliveryWorkflowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='buyer', password='password')
        self.owner = User.objects.create_user(username='owner', password='password')
        self.partner_user = User.objects.create_user(username='rider', password='password', role='DELIVERY')

        self.pharmacy = Pharmacy.objects.create(
            owner=self.owner, name='Test Pharm', slug='test-pharm',
            license_number='123', address='Addr', district='Chennai'
        )

        self.order = Order.objects.create(
            user=self.user, pharmacy=self.pharmacy, total_amount=Decimal('100.00'),
            status=Order.Status.PENDING
        )

        self.partner = DeliveryPartner.objects.create(
            user=self.partner_user, vehicle_number='TN-01-AB-1234'
        )

    def test_delivery_lifecycle(self):
        # 1. Assign
        assignment = DeliveryService.assign_partner(self.order)
        self.assertIsNotNone(assignment)
        self.assertEqual(assignment.partner, self.partner)

        # 2. Pickup
        DeliveryService.pickup_order(assignment)
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, DeliveryAssignment.Status.PICKED_UP)

        # 3. Out for Delivery
        DeliveryService.start_out_for_delivery(assignment)
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, DeliveryAssignment.Status.OUT_FOR_DELIVERY)
        self.assertTrue(hasattr(assignment, 'otp_verification'))

        # 4. Verify OTP and Complete
        otp = assignment.otp_verification.otp_code
        success = DeliveryService.verify_and_complete(assignment, otp)
        self.assertTrue(success)

        assignment.refresh_from_db()
        self.assertEqual(assignment.status, DeliveryAssignment.Status.DELIVERED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.DELIVERED)

        self.partner.refresh_from_db()
        self.assertTrue(self.partner.is_available)
