"""Views of the auth_app: registration, login and email check."""
# Drittanbieter (Third-party)
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
# Lokale Importe (eigene Module)
from .serializers import LoginSerializer, RegistrationSerializer


def build_auth_response(user):
    """Builds the standard auth response (token + user data) for the frontend."""
    token, _ = Token.objects.get_or_create(user=user)
    return {
        "token": token.key,
        "fullname": user.get_full_name(),
        "email": user.email,
        "user_id": user.id,
    }


def build_user_data(user):
    """Builds the short user representation (id, email, fullname) used by email-check."""
    return {
        "id": user.id,
        "email": user.email,
        "fullname": user.get_full_name(),
    }


class RegistrationView(APIView):
    """Registers a new user and returns their auth token."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(build_auth_response(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Authenticates a user via email and password."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(build_auth_response(user), status=status.HTTP_200_OK)


class EmailCheckView(APIView):
    """Checks whether an email exists and returns the user object."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response(
                {"detail": "Missing 'email' parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(build_user_data(user), status=status.HTTP_200_OK)
