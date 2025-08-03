from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
# from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer
from .serializers import (
    StudentRegisterSerializer,
    TeacherRegisterSerializer,
    LoginSerializer,
    ProfileSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView


# class RegisterView(APIView):
#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"message": "User created successfully."},
#                 status=status.HTTP_201_CREATED,
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class StudentRegisterView(APIView):
    def post(self, request):
        serializer = StudentRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Student registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeacherRegisterView(APIView):
    def post(self, request):
        serializer = TeacherRegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Teacher registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {"message": f"Hello, {request.user.username}"}, status=status.HTTP_200_OK
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)
