from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from lms.models import Course, Lesson, Subscription
from lms.serializers import CourseSerializer, LessonSerializer
from lms.permissions import IsModerator, IsOwner, IsOwnerOrReadOnly

from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from lms.serializers import SubscriptionSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()

    def get_permissions(self):
        if self.action == "create":
            # Создавать могут только не-модераторы
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ["update", "partial_update"]:
            # Редактировать могут модераторы или владельцы
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == "destroy":
            # Удалять могут только владельцы (модераторам запрещено)
            self.permission_classes = [IsAuthenticated, ~IsModerator, IsOwner]
        else:
            # Просмотр доступен всем авторизованным
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator]

    def get_queryset(self):
        return Lesson.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moderators").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moderators").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]

    def get_queryset(self):
        return Lesson.objects.all()


class LessonDeleteAPIView(generics.DestroyAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator, IsOwner]

    def get_queryset(self):
        return Lesson.objects.all()


class SubscriptionAPIView(APIView):
    """Эндпоинт для управления подпиской на курс"""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            return Response(
                {"error": "Необходимо указать course_id"},
                status=400
            )

        course = get_object_or_404(Course, id=course_id)

        subscription = Subscription.objects.filter(
            user=user,
            course=course
        )

        if subscription.exists():
            # Если подписка есть — удаляем
            subscription.delete()
            message = "Подписка удалена"
            is_subscribed = False
        else:
            # Если подписки нет — создаем
            Subscription.objects.create(user=user, course=course)
            message = "Подписка добавлена"
            is_subscribed = True

        return Response({
            "message": message,
            "is_subscribed": is_subscribed,
            "course_id": course.id,
            "course_name": course.name
        })

    def get(self, request, *args, **kwargs):
        """Опционально: получить список подписок текущего пользователя"""
        subscriptions = Subscription.objects.filter(user=request.user)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)
