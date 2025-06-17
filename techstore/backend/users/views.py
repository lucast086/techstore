"""Views for user authentication."""

from django.contrib.auth import authenticate, logout
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.serializers import LoginSerializer


class LoginView(APIView):
    """View for handling user login."""

    def post(self, request):
        """Handle POST request for login."""
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            return Response({"detail": "Login successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """View for handling user logout."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Handle POST request for logout."""
        logout(request)
        return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)
