from django.test import TestCase
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from users.models import User
from lms.models import Course, Lesson, Subscription


class LessonTests(TestCase):
    """Тесты для CRUD уроков"""

    def setUp(self):
        """Подготовка тестовых данных"""
        # Создаем клиент
        self.client = APIClient()

        # Создаем пользователей
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )

        self.moderator = User.objects.create_user(
            email="moderator@test.com",
            password="testpass123",
            first_name="Moderator",
            last_name="User"
        )

        # Создаем группу модераторов и добавляем пользователя
        moderator_group, _ = Group.objects.get_or_create(name="moderators")
        self.moderator.groups.add(moderator_group)

        self.other_user = User.objects.create_user(
            email="other@test.com",
            password="testpass123",
            first_name="Other",
            last_name="User"
        )

        # Создаем курс
        self.course = Course.objects.create(
            name="Test Course",
            description="Test Description",
            owner=self.user
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            name="Test Lesson",
            description="Test Lesson Description",
            course=self.course,
            link_video="https://www.youtube.com/watch?v=abc123",
            owner=self.user
        )

        # Создаем второй урок для другого пользователя
        self.other_lesson = Lesson.objects.create(
            name="Other Lesson",
            description="Other Lesson Description",
            course=self.course,
            link_video="https://www.youtube.com/watch?v=xyz789",
            owner=self.other_user
        )

    def test_create_lesson_authenticated(self):
        """Тест создания урока авторизованным пользователем"""
        self.client.force_authenticate(user=self.user)

        url = reverse("lms:lesson_create")
        data = {
            "name": "New Lesson",
            "description": "New Description",
            "course": self.course.id,
            "link_video": "https://www.youtube.com/watch?v=new123"
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 3)
        self.assertEqual(response.data["owner"], self.user.id)

    def test_create_lesson_unauthenticated(self):
        """Тест создания урока неавторизованным пользователем"""
        url = reverse("lms:lesson_create")
        data = {
            "name": "New Lesson",
            "description": "New Description",
            "course": self.course.id,
            "link_video": "https://www.youtube.com/watch?v=new123"
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_lesson_moderator_forbidden(self):
        """Тест: модератор не может создавать уроки"""
        self.client.force_authenticate(user=self.moderator)

        url = reverse("lms:lesson_create")
        data = {
            "name": "Moderator Lesson",
            "description": "Moderator Description",
            "course": self.course.id,
            "link_video": "https://www.youtube.com/watch?v=mod123"
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_lesson_invalid_youtube_link(self):
        """Тест создания урока с недопустимой ссылкой"""
        self.client.force_authenticate(user=self.user)

        url = reverse("lms:lesson_create")
        data = {
            "name": "Invalid Link Lesson",
            "description": "Test",
            "course": self.course.id,
            "link_video": "https://rutube.ru/video/123"
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("link_video", response.data)

    def test_list_lessons_authenticated(self):
        """Тест получения списка уроков авторизованным пользователем"""
        self.client.force_authenticate(user=self.user)

        url = reverse("lms:lesson_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Пользователь должен видеть только свои уроки
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Test Lesson")

    def test_list_lessons_moderator(self):
        """Тест получения списка уроков модератором (видит все)"""
        self.client.force_authenticate(user=self.moderator)

        url = reverse("lms:lesson_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Модератор видит все уроки
        self.assertEqual(len(response.data["results"]), 2)

    def test_retrieve_lesson_owner(self):
        """Тест просмотра урока владельцем"""
        self.client.force_authenticate(user=self.user)

        url = reverse("lms:lesson_detail", args=[self.lesson.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Lesson")

    def test_retrieve_lesson_other_user(self):
        """Тест просмотра чужого урока обычным пользователем"""
        self.client.force_authenticate(user=self.other_user)

        url = reverse("lms:lesson_detail", args=[self.lesson.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_lesson_moderator(self):
        """Тест просмотра урока модератором (видит любой)"""
        self.client.force_authenticate(user=self.moderator)

        url = reverse("lms:lesson_detail", args=[self.lesson.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Lesson")

    def test_update_lesson_owner(self):
        """Тест обновления урока владельцем"""
        self.client.force_authenticate(user=self.user)

        url = reverse("lms:lesson_update", args=[self.lesson.id])
        data = {"name": "Updated Lesson Name"}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, "Updated Lesson Name")

    def test_update_lesson_other_user(self):
        """Тест обновления чужого урока обычным пользователем"""
        self.client.force_authenticate(user=self.other_user)

        url = reverse("lms:lesson_update", args=[self.lesson.id])
        data = {"name": "Hacked Lesson"}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_lesson_moderator(self):
        """Тест обновления урока модератором (имеет право)"""
        self.client.force_authenticate(user=self.moderator)

        url = reverse("lms:lesson_update", args=[self.lesson.id])
        data = {"name": "Moderator Updated"}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, "Moderator Updated")

    def test_delete_lesson_owner(self):
        """Тест удаления урока владельцем"""
        self.client.force_authenticate(user=self.user)

        url = reverse("lms:lesson_delete", args=[self.lesson.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.filter(id=self.lesson.id).count(), 0)

    def test_delete_lesson_other_user(self):
        """Тест удаления чужого урока обычным пользователем"""
        self.client.force_authenticate(user=self.other_user)

        url = reverse("lms:lesson_delete", args=[self.lesson.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_moderator_forbidden(self):
        """Тест: модератор не может удалять уроки"""
        self.client.force_authenticate(user=self.moderator)

        url = reverse("lms:lesson_delete", args=[self.lesson.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTests(TestCase):
    """Тесты для функционала подписки"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.client = APIClient()

        # Создаем пользователей
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123"
        )
        self.other_user = User.objects.create_user(
            email="other@test.com",
            password="testpass123"
        )

        # Создаем курсы
        self.course1 = Course.objects.create(
            name="Course 1",
            description="Description 1"
        )
        self.course2 = Course.objects.create(
            name="Course 2",
            description="Description 2"
        )

    def test_add_subscription(self):
        """Тест добавления подписки"""
        self.client.force_authenticate(user=self.user)

        url = reverse("lms:subscriptions")
        data = {"course_id": self.course1.id}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertTrue(response.data["is_subscribed"])
        self.assertEqual(Subscription.objects.count(), 1)

    def test_remove_subscription(self):
        """Тест удаления подписки"""
        # Сначала создаем подписку
        Subscription.objects.create(user=self.user, course=self.course1)

        self.client.force_authenticate(user=self.user)

        url = reverse("lms:subscriptions")
        data = {"course_id": self.course1.id}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertFalse(response.data["is_subscribed"])
        self.assertEqual(Subscription.objects.count(), 0)

    def test_subscription_without_course_id(self):
        """Тест подписки без указания course_id"""
        self.client.force_authenticate(user=self.user)

        url = reverse("lms:subscriptions")
        data = {}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_subscription_nonexistent_course(self):
        """Тест подписки на несуществующий курс"""
        self.client.force_authenticate(user=self.user)

        url = reverse("lms:subscriptions")
        data = {"course_id": 999}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscription_unauthenticated(self):
        """Тест подписки неавторизованным пользователем"""
        url = reverse("lms:subscriptions")
        data = {"course_id": self.course1.id}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_subscriptions_list(self):
        """Тест получения списка подписок пользователя"""
        # Создаем подписки
        Subscription.objects.create(user=self.user, course=self.course1)
        Subscription.objects.create(user=self.user, course=self.course2)

        self.client.force_authenticate(user=self.user)

        url = reverse("lms:subscriptions")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_is_subscribed_field_in_course(self):
        """Тест наличия поля is_subscribed в сериализаторе курса"""
        # Создаем подписку
        Subscription.objects.create(user=self.user, course=self.course1)

        self.client.force_authenticate(user=self.user)

        url = reverse("lms:courses-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Находим нужный курс в ответе
        courses = response.data["results"]
        for course in courses:
            if course["pk"] == self.course1.id:
                self.assertTrue(course["is_subscribed"])
            if course["pk"] == self.course2.id:
                self.assertFalse(course["is_subscribed"])


class CourseTests(TestCase):
    """Тесты для курсов (CRUD)"""

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123"
        )

        self.moderator = User.objects.create_user(
            email="moderator@test.com",
            password="testpass123"
        )
        moderator_group, _ = Group.objects.get_or_create(name="moderators")
        self.moderator.groups.add(moderator_group)

        self.other_user = User.objects.create_user(
            email="other@test.com",
            password="testpass123"
        )

        self.course = Course.objects.create(
            name="Test Course",
            description="Test Description",
            owner=self.user
        )

    def test_create_course_authenticated(self):
        """Тест создания курса авторизованным пользователем"""
        self.client.force_authenticate(user=self.user)

        url = reverse("lms:courses-list")
        data = {
            "name": "New Course",
            "description": "New Description"
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["owner"], self.user.id)

    def test_create_course_moderator_forbidden(self):
        """Тест: модератор не может создавать курсы"""
        self.client.force_authenticate(user=self.moderator)

        url = reverse("lms:courses-list")
        data = {
            "name": "Moderator Course",
            "description": "Test"
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_course_owner(self):
        """Тест обновления курса владельцем"""
        self.client.force_authenticate(user=self.user)

        url = reverse("lms:courses-detail", args=[self.course.id])
        data = {"name": "Updated Course Name"}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, "Updated Course Name")

    def test_update_course_moderator(self):
        """Тест обновления курса модератором"""
        self.client.force_authenticate(user=self.moderator)

        url = reverse("lms:courses-detail", args=[self.course.id])
        data = {"name": "Moderator Updated"}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, "Moderator Updated")

    def test_delete_course_owner(self):
        """Тест удаления курса владельцем"""
        self.client.force_authenticate(user=self.user)

        url = reverse("lms:courses-detail", args=[self.course.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.filter(id=self.course.id).count(), 0)

    def test_delete_course_moderator_forbidden(self):
        """Тест: модератор не может удалять курсы"""
        self.client.force_authenticate(user=self.moderator)

        url = reverse("lms:courses-detail", args=[self.course.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)