from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from django.contrib.auth import get_user_model
from user.models import StudentProfile, TeacherProfile, Student, Teacher, User
from django.utils.translation import gettext_lazy as _
from typing import Optional, TypedDict, Dict
from datetime import datetime

# Get the custom user model defined in the project settings.
# This is a best practice to ensure compatibility.
# User = get_user_model()


class UserData(TypedDict, total=False):
    username: str
    first_name: str
    last_name: str
    email: Optional[str]
    is_staff: bool
    is_active: bool
    date_joined: datetime
    role: str


class TokenResponse(TypedDict):
    refresh: str
    access: str
    user_id: int
    username: str
    email: str
    role: str


class StudentRegisterSerializer(serializers.ModelSerializer):
    """
    A serializer for registering new users with the 'STUDENT' role.

    This serializer handles the creation of a new `User` instance and
    associates it with a `StudentProfile`. It validates the input data
    and securely hashes the password.
    """

    # The `password` field is `write_only` to prevent it from being
    # returned in API responses, ensuring password security.
    password: Optional[str] = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data: UserData) -> Student:
        """
        Overrides the `create` method to handle user creation and role
        assignment.

        This is where the business logic for creating a new student user
        resides.
        It's crucial to create the user with the correct role and then create
        the corresponding profile.

        Note: We use the base `User` model for creation because the `Student`
        proxy model doesn't have its own database table. The proxy model
        is an abstraction layer, not a separate entity in the database.
        """
        # Create a new user instance using the `create_user` method, which
        # handles password hashing.
        user: Student = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        # Manually set the role to 'STUDENT' for the newly created user.
        user.role = User.Role.STUDENT
        user.save()
        # Create a corresponding `StudentProfile` for the new user.
        # This is essential for storing student-specific data.
        StudentProfile.objects.create(user=user)
        return user


class TeacherRegisterSerializer(serializers.ModelSerializer):
    """
    A serializer for registering new users with the 'TEACHER' role.

    This works similarly to `StudentRegisterSerializer`, but for teachers.
    It creates a new `User` with the 'TEACHER' role and an associated
    `TeacherProfile`.
    """

    password: Optional[str] = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data: UserData) -> Teacher:
        """
        Overrides the `create` method to handle teacher user creation.
        """
        user: Teacher = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        user.role = User.Role.TEACHER
        user.save()
        TeacherProfile.objects.create(user=user)
        return user


class LoginSerializer(TokenObtainPairSerializer):
    """
    Custom serializer for obtaining JWT tokens.

    This serializer extends `TokenObtainPairSerializer` to provide a more
    structured and informative response upon successful login. It includes
    key user details alongside the access and refresh tokens.

    It also enhances error handling to provide a consistent message for
    invalid credentials, preventing information leakage.
    """

    default_error_messages: Dict[str, str] = {
        "no_active_account": _("Invalid username or password.")
    }

    def validate(self, attrs: Dict[str, str]) -> TokenResponse:
        """
        Overrides the `validate` method to perform authentication and
        augment the response with user details.

        This method is the core of the login process, handling both success
        and failure scenarios.
        """
        try:
            # Call the parent's validate method to authenticate the user and
            # generate the access and refresh tokens. This is the heavy
            # lifting.
            data = super().validate(attrs)
        except serializers.ValidationError:
            # Catch the default validation error raised by `super().validate`
            # for incorrect credentials. By raising our own ValidationError
            # here,
            # we can provide a generic error message, improving security by
            # not distinguishing between an invalid username and a wrong
            # password.
            raise serializers.ValidationError(
                {"detail": self.default_error_messages["no_active_account"]}
            )

        # Upon successful validation, the `self.user` attribute is set.
        # We can now safely access it and add custom user data to the response.
        # data["user_id"] = self.user.id
        # data["username"] = self.user.username
        # data["email"] = self.user.email
        # data["role"] = self.user.role

        # typed_data: TokenResponse = {
        #     "refresh": data.get('refresh'),
        #     "access": data.get('access'),
        #     "user_id": self.user.id,
        #     "username": self.user.username,
        #     "email": self.user.email,
        #     "role": self.user.role
        # }
        typed_data: TokenResponse = {
            **data,
            "user_id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "role": self.user.role,
        }

        return typed_data


class ProfileSerializer(serializers.ModelSerializer):
    """
    A serializer to fetch detailed user information, including role-specific
    profiles.

    This serializer is designed to be used in a profile view, where a user
    can retrieve their own details. It dynamically includes the relevant
    profile data (`student_id` or `teacher_id`) based on the user's role.
    """

    # A custom field to handle the profile data. It will be populated
    # by the `get_profile` method.
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "profile",
        ]

    def get_profile(self, obj: User) -> Optional[Dict[str, Optional[int]]]:
        """
        A custom method to get the user's profile information based on their
        role.

        This method is called by the `SerializerMethodField` to populate the
        `profile` field in the serialized output. It checks the user's role
        and returns the data from the corresponding profile model.
        """
        if obj.role == User.Role.STUDENT:
            # Use `getattr` with a default of `None` to prevent
            # `RelatedObjectDoesNotExist` errors
            # if the profile hasn't been created yet (though the signal should
            # prevent this).
            profile = getattr(obj, "studentprofile", None)
            # Return a dictionary with the specific profile data.
            return {"student_id": profile.student_id} if profile else None
        elif obj.role == User.Role.TEACHER:
            profile = getattr(obj, "teacherprofile", None)
            return {"teacher_id": profile.teacher_id} if profile else None
        return None
