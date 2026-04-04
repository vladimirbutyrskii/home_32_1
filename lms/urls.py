from django.urls import include, path
from rest_framework.routers import DefaultRouter
from lms.apps import LmsConfig

from lms.views import (
    CourseViewSet,
    LessonCreateAPIView,
    LessonListAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
    LessonDeleteAPIView,
    SubscriptionAPIView,
)

app_name = LmsConfig.name

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")

urlpatterns = [
    path("lessons/create/", LessonCreateAPIView.as_view(), name="lesson_create"),
    path("lessons/", LessonListAPIView.as_view(), name="lesson_list"),
    path("lessons/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson_detail"),
    path("lessons/update/<int:pk>/", LessonUpdateAPIView.as_view(), name="lesson_update"),
    path("lessons/delete/<int:pk>/", LessonDeleteAPIView.as_view(), name="lesson_delete"),
    path("subscriptions/", SubscriptionAPIView.as_view(), name="subscriptions"),
] + router.urls

