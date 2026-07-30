"""Serializers of the auth_app: registration and login."""
from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    """Validates and creates a new user from the frontend data."""

    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        """Ensures the email address is not already taken."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already taken.")
        return value

    def validate(self, attrs):
        """Checks that both passwords match."""
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"password": "The passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """Creates the user; the email is also used as the username."""
        first_name, last_name = split_fullname(validated_data["fullname"])
        user = User(
            username=validated_data["email"],
            email=validated_data["email"],
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Validates the login data (email and password)."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


def split_fullname(fullname):
    """Splits a full name into first and last name."""
    parts = fullname.strip().split(" ", 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""
    return first_name, last_name
