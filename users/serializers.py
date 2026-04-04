from rest_framework import serializers
from users.models import User, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра профиля (ограниченная информация)"""

    class Meta:
        model = User
        fields = ["id", "email", "phone", "city", "avatar", "first_name", "date_joined"]


class UserDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра своего профиля (полная информация)"""

    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "phone", "city", "avatar", "first_name", "last_name",
            "date_joined", "payments"
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "phone", "city", "avatar"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "phone", "city", "avatar", "first_name", "last_name", "payments"]

