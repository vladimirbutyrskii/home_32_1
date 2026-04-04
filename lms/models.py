from django.db import models
from django.conf import settings

NULLABLE = dict(null=True, blank=True)


class Course(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название курса",
        help_text="Укажите название курса",
    )
    preview = models.ImageField(
        upload_to="lms/preview",
        **NULLABLE,
        verbose_name="Эмблема курса",
        help_text="Загрузите эмблему курса",
    )
    description = models.TextField(
        **NULLABLE,
        verbose_name="Описание курса",
        help_text="Укажите описание курса",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        **NULLABLE,
        verbose_name="Владелец",
        related_name="courses",
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ("pk",)


class Lesson(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название урока",
        help_text="Укажите название урока",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Курс",
        help_text="Выберите курс",
        related_name="lessons",
    )
    description = models.TextField(
        **NULLABLE,
        verbose_name="Описание урока",
        help_text="Укажите описание урока",
    )
    preview = models.ImageField(
        upload_to="lms/preview",
        **NULLABLE,
        verbose_name="Эмблема урока",
        help_text="Загрузите эмблему урока",
    )
    link_video = models.URLField(
        max_length=150,
        **NULLABLE,
        verbose_name="Ссылка на видео",
        help_text="Укажите ссылку на видео",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        **NULLABLE,
        verbose_name="Владелец",
        related_name="lessons",
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ("pk",)


class Subscription(models.Model):
    """Модель подписки на обновления курса"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="subscriptions",
    )
    course = models.ForeignKey(
        "Course",
        on_delete=models.CASCADE,
        verbose_name="Курс",
        related_name="subscriptions",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата подписки",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ("user", "course")  # Предотвращаем дублирование подписок
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user.email} -> {self.course.name}"
