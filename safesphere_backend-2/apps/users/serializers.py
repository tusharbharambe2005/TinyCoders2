"""
Users app serializers.
"""
from rest_framework import serializers
from .models import User, TrustedContact


class TrustedContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustedContact
        fields = ["id", "contact_name", "contact_phone", "contact_email", "created_at"]
        read_only_fields = ["id", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    trusted_contacts = TrustedContactSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "name", "phone", "email", "device_id", "created_at", "trusted_contacts"]
        read_only_fields = ["id", "created_at"]


class UserRegisterSerializer(serializers.ModelSerializer):
    """Used for POST /api/users/register – minimal fields required."""
    class Meta:
        model = User
        fields = ["name", "phone", "email", "device_id"]

    def create(self, validated_data):
        return User.objects.create(**validated_data)


class TrustedContactCreateSerializer(serializers.ModelSerializer):
    """Used for POST /api/users/trusted-contact."""
    user_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = TrustedContact
        fields = ["user_id", "contact_name", "contact_phone", "contact_email"]

    def create(self, validated_data):
        from apps.users.models import User
        user = User.objects.get(id=validated_data.pop("user_id"))
        return TrustedContact.objects.create(user=user, **validated_data)
