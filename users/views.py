from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from users.models import User, Payment
from users.paginators import PaymentPaginator
from users.serializers import (
    UserProfileSerializer,
    UserDetailSerializer,
    UserRegistrationSerializer,
    PaymentSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegistrationSerializer
        if self.action == "retrieve":
            # При просмотре чужого профиля возвращаем ограниченные данные
            if self.get_object() != self.request.user:
                return UserProfileSerializer
            return UserDetailSerializer
        if self.action == "update" or self.action == "partial_update":
            # Редактировать можно только свой профиль
            if self.get_object() != self.request.user:
                self.permission_denied(
                    self.request, message="Вы можете редактировать только свой профиль"
                )
            return UserDetailSerializer
        return UserProfileSerializer

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [AllowAny]
        return super().get_permissions()


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["paid_lesson", "paid_course", "type"]
    ordering_fields = ["payment_date", "amount"]
    pagination_class = PaymentPaginator

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moderators").exists():
            return Payment.objects.all()
        return Payment.objects.filter(payer=user)

