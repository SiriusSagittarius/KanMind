"""Views der auth_app: Registrierung, Login und E-Mail-Pruefung."""
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegistrationSerializer


def build_auth_response(user):
    """Baut die Standard-Auth-Antwort (Token + Nutzerdaten) fuer das Frontend."""
    token, _ = Token.objects.get_or_create(user=user)
    return {
        "token": token.key,
        "user_id": user.id,
        "email": user.email,
        "fullname": user.get_full_name(),
    }


class RegistrationView(APIView):
    """Registriert einen neuen Benutzer und liefert dessen Auth-Token."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(build_auth_response(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Authentifiziert einen Benutzer per E-Mail und Passwort."""

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
                {"detail": "Ungueltige Anmeldedaten."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(build_auth_response(user), status=status.HTTP_200_OK)


class EmailCheckView(APIView):
    """Prueft, ob eine E-Mail existiert, und gibt das Nutzerobjekt zurueck."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response(
                {"detail": "Parameter 'email' fehlt."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = {"id": user.id, "email": user.email, "fullname": user.get_full_name()}
        return Response(data, status=status.HTTP_200_OK)
