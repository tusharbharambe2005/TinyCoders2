"""
Users app views.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import User, TrustedContact
from .serializers import UserRegisterSerializer, UserSerializer, TrustedContactCreateSerializer

from rest_framework.permissions import AllowAny

class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    """
    POST /api/users/register
    Creates a new SafeSphere user profile.
    """
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully.",
                    "user_id": str(user.id),
                    "name": user.name,
                    "phone": user.phone,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddTrustedContactView(APIView):
    permission_classes = [AllowAny]

    """
    POST /api/users/trusted-contact
    Adds a trusted contact for a user.

    Request body:
    {
        "user_id": "<uuid>",
        "contact_name": "Priya",
        "contact_phone": "9876543210",
        "contact_email": "priya@example.com"
    }
    """
    def post(self, request):
        serializer = TrustedContactCreateSerializer(data=request.data)

        if serializer.is_valid():
            contact = serializer.save()
            return Response(
                {
                    "message": "Trusted contact added.",
                    "contact_id": contact.id,
                    "contact_name": contact.contact_name,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUserView(APIView):
    permission_classes = [AllowAny]

    """
    GET /api/users/<user_id>
    Returns user profile including trusted contacts.
    """
    def get(self, request, user_id):
        try:
            user = User.objects.prefetch_related("trusted_contacts").get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
