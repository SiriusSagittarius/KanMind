"""Serializer der auth_app: Registrierung und Login."""
from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    """Validiert und erstellt einen neuen Benutzer aus den Frontend-Daten."""

    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        """Stellt sicher, dass die E-Mail noch nicht vergeben ist."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Diese E-Mail ist bereits vergeben.")
        return value

    def validate(self, attrs):
        """Prueft, dass beide Passwoerter uebereinstimmen."""
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"password": "Die Passwoerter stimmen nicht ueberein."}
            )
        return attrs

    def create(self, validated_data):
        """Legt den Benutzer an; E-Mail dient zugleich als Username."""
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
    """Validiert die Login-Daten (E-Mail und Passwort)."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


def split_fullname(fullname):
    """Teilt einen vollen Namen in Vor- und Nachname auf."""
    parts = fullname.strip().split(" ", 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""
    return first_name, last_name
