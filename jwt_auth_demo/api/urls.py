from django.urls import path, re_path

# from .views import RegisterView, ProtectedView, LoginView, ProfileView
from .views import StudentRegisterView, TeacherRegisterView, LoginView, ProfileView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class NotFoundFallbackAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(
            {
                "detail": "The requested resource was not found.",
                "status_code": 404,
                "error": True,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


urlpatterns = [
    path("register/student/", StudentRegisterView.as_view(), name="student_register"),
    path("register/teacher/", TeacherRegisterView.as_view(), name="teacher_register"),
    # path("register/", RegisterView.as_view(), name="register"),
    # path("protected/", ProtectedView.as_view(), name="protected"),
    # JWT auth endpoints
    path("login/", LoginView.as_view(), name="login"),
    path("token/regresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", ProfileView.as_view(), name="profile"),
    re_path(r"^.*$", NotFoundFallbackAPIView.as_view()),
]
