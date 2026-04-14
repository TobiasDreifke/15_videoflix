"""Serializers for authentication-related API endpoints."""

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Validate and create a new inactive user account."""

    password = serializers.CharField(write_only=True, min_length=8)
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        """Serializer metadata for the registration payload."""

        model = User
        fields = ['email', 'password', 'confirmed_password']

    def validate(self, data):
        """Ensure the submitted password fields match."""
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError('Passwords do not match.')
        return data

    def create(self, validated_data):
        """Create a new inactive user using the submitted email as username."""
        validated_data.pop('confirmed_password')
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False,
        )
        return user
