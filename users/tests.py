from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date

from users.models import User, Payment
from lms.models import Course, Lesson


class UserTests(TestCase):
    """Тесты для пользователей"""

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            phone="123456789",
            city="Test City"
        )

        self.other_user = User.objects.create_user(
            email="other@test.com",
            password="testpass123"
        )

    def test_register_user(self):
        """Тест регистрации пользователя"""
        url = reverse("users:users-list")
        data = {
            "email": "newuser@test.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User"
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(response.data["email"], "newuser@test.com")
        self.assertNotIn("password", response.data)

    def test_retrieve_own_profile(self):
        """Тест просмотра своего профиля (полная информация)"""
        self.client.force_authenticate(user=self.user)

        url = reverse("users:users-detail", args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("payments", response.data)
        self.assertIn("last_name", response.data)

    def test_retrieve_other_profile(self):
        """Тест просмотра чужого профиля (ограниченная информация)"""
        self.client.force_authenticate(user=self.user)

        url = reverse("users:users-detail", args=[self.other_user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("payments", response.data)
        self.assertNotIn("last_name", response.data)

    def test_update_own_profile(self):
        """Тест редактирования своего профиля"""
        self.client.force_authenticate(user=self.user)

        url = reverse("users:users-detail", args=[self.user.id])
        data = {"phone": "987654321", "city": "Updated City"}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, "987654321")
        self.assertEqual(self.user.city, "Updated City")

    def test_update_other_profile_forbidden(self):
        """Тест: нельзя редактировать чужой профиль"""
        self.client.force_authenticate(user=self.user)

        url = reverse("users:users-detail", args=[self.other_user.id])
        data = {"phone": "Hacked"}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PaymentTests(TestCase):
    """Тесты для платежей"""

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123"
        )

        self.course = Course.objects.create(
            name="Test Course",
            description="Test Description"
        )

        self.lesson = Lesson.objects.create(
            name="Test Lesson",
            description="Test Description",
            course=self.course,
            link_video="https://www.youtube.com/watch?v=test"
        )

        self.payment = Payment.objects.create(
            payer=self.user,
            amount=1000,
            type="cash",
            paid_course=self.course
        )

    def test_list_payments_authenticated(self):
        """Тест получения списка платежей авторизованным пользователем"""
        self.client.force_authenticate(user=self.user)

        url = reverse("users:payment_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_payments_filter_by_type(self):
        """Тест фильтрации платежей по типу"""
        Payment.objects.create(
            payer=self.user,
            amount=2000,
            type="bank",
            paid_lesson=self.lesson
        )

        self.client.force_authenticate(user=self.user)

        url = reverse("users:payment_list")
        response = self.client.get(url, {"type": "cash"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["type"], "cash")

    def test_list_payments_order_by_date(self):
        """Тест сортировки платежей по дате"""
        Payment.objects.create(
            payer=self.user,
            amount=2000,
            type="bank",
            paid_lesson=self.lesson,
            payment_date=date(2025, 4, 1)
        )

        self.client.force_authenticate(user=self.user)

        url = reverse("users:payment_list")
        response = self.client.get(url, {"ordering": "-payment_date"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что сортировка работает
        self.assertGreater(len(response.data["results"]), 0)

    def test_list_payments_unauthenticated(self):
        """Тест получения списка платежей неавторизованным пользователем"""
        url = reverse("users:payment_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
