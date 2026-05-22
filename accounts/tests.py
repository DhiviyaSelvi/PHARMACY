from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAuthTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            role=User.Role.BUYER
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, User.Role.BUYER)
        self.assertTrue(user.check_password('testpassword123'))

    def test_create_pharmacist(self):
        user = User.objects.create_user(
            username='pharmacy_owner',
            password='password123',
            role=User.Role.PHARMACIST
        )
        self.assertEqual(user.role, User.Role.PHARMACIST)
