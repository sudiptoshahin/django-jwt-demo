from django.urls import path
# from .views import RegisterView, ProtectedView, LoginView, ProfileView
from .views import StudentRegisterView, TeacherRegisterView, LoginView, ProfileView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/student/', StudentRegisterView.as_view(), name='student_register'),
    path('register/teacher/', TeacherRegisterView.as_view(), name='teacher_register'),
    # path("register/", RegisterView.as_view(), name="register"),
    # path("protected/", ProtectedView.as_view(), name="protected"),
    # JWT auth endpoints
    path("login/", LoginView.as_view(), name="login"),
    path("token/regresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
