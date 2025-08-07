from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, status
from .serializers import (
    StudentRegisterSerializer,
    TeacherRegisterSerializer,
    LoginSerializer,
    ProfileSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError

# ---------------------------
# Student Registration View
# ---------------------------


class StudentRegisterView(generics.CreateAPIView):
    """
    API view for registering a new student user.

    This view uses DRF's `CreateAPIView` to handle POST requests. It leverages
    the serializer's `create()` method for user creation and adds custom
    error handling for database integrity errors and a structured success
    response.

    - **HTTP Method:** `POST`
    - **Endpoint:** Typically `/api/register/student/`
    - **Permissions:** `AllowAny` is used to permit unauthenticated users to
        register.
    """

    # 1. Define the serializer class to be used for validation and
    # deserialization.
    serializer_class = StudentRegisterSerializer

    # 2. Define the permission class to allow access to this endpoint.
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        """
        Overrides the default `perform_create` method to handle database
        errors.

        This method is called by the `create()` method after validation is
        successful.
        It wraps the `serializer.save()` call in a `try...except` block to
        catch
        specific database exceptions, like a unique constraint violation.
        """
        try:
            # `serializer.save()` triggers the `create()` method in our
            # serializer.
            serializer.save()
        except IntegrityError:
            # If a database integrity error occurs (e.g., duplicate username or
            # email),
            # we catch it and re-raise a DRF `ValidationError`. This ensures
            # the error
            # is handled by DRF's exception handler, returning a clean 400 Bad
            # Request
            # response to the client.
            raise ValidationError(
                {
                    "non_field_errors": [
                        "A user with this username or email already exists."
                    ]
                }
            )

    def create(self, request, *args, **kwargs):
        """
        Customizes the final success response for the create action.

        This method overrides the default `create` to provide a more structured
        and informative response upon successful registration.
        """
        # 1. Get the serializer with the request data.
        serializer = self.get_serializer(data=request.data)

        # 2. Validate the data.
        # `raise_exception=True` tells DRF to automatically raise a
        # `ValidationError`
        # if the data is invalid, which will be caught by the framework's
        # exception
        # handler, resulting in a structured 400 Bad Request response.
        serializer.is_valid(raise_exception=True)

        # 3. Perform the creation.
        # This calls our overridden `perform_create` method, which saves the
        # object
        # and handles any `IntegrityError`.
        self.perform_create(serializer)

        # 4. Generate response headers.
        # The `get_success_headers` method is a DRF utility to generate
        # appropriate
        # headers for a successful creation (e.g., `Location` header).
        headers = self.get_success_headers(serializer.data)

        # 5. Return the final, structured response.
        # We provide a clear message and a subset of the non-sensitive user
        # data
        # for a clean and secure API contract.
        return Response(
            {
                "message": "Student registered successfully.",
                "data": {
                    "username": serializer.data["username"],
                    "email": serializer.data["email"],
                },
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


# ---------------------------
# Teacher Registration View
# ---------------------------


class TeacherRegisterView(generics.CreateAPIView):
    """
    API view for registering a new teacher user.

    This view uses DRF's `CreateAPIView` to handle POST requests. It leverages
    the serializer's `create()` method for user creation and adds custom
    error handling for database integrity errors and a structured success
    response.

    - **HTTP Method:** `POST`
    - **Endpoint:** Typically `/api/register/teacher/`
    - **Permissions:** `AllowAny` is used to permit unauthenticated users to
    register.
    """

    # 1. Define the serializer class to be used for validation and
    # deserialization.
    serializer_class = TeacherRegisterSerializer

    # 2. Define the permission class to allow access to this endpoint.
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        """
        Overrides the default `perform_create` method to handle database
        errors.

        This method is called by the `create()` method after validation is
        successful.
        It wraps the `serializer.save()` call in a `try...except` block to
        catch
        specific database exceptions, like a unique constraint violation.
        """
        try:
            # `serializer.save()` triggers the `create()` method in our
            # serializer.
            serializer.save()
        except IntegrityError:
            # If a database integrity error occurs (e.g., duplicate username
            # or email),
            # we catch it and re-raise a DRF `ValidationError`. This ensures
            # the error
            # is handled by DRF's exception handler, returning a clean 400 Bad
            # Request
            # response to the client.
            raise ValidationError(
                {
                    "non_field_errors": [
                        "A user with this username or email already exists."
                    ]
                }
            )

    def create(self, request, *args, **kwargs):
        """
        Customizes the final success response for the create action.

        This method overrides the default `create` to provide a more structured
        and informative response upon successful registration.
        """
        # 1. Get the serializer with the request data.
        serializer = self.get_serializer(data=request.data)

        # 2. Validate the data.
        # `raise_exception=True` tells DRF to automatically raise a
        # `ValidationError`
        # if the data is invalid, which will be caught by the framework's
        # exception
        # handler, resulting in a structured 400 Bad Request response.
        serializer.is_valid(raise_exception=True)

        # 3. Perform the creation.
        # This calls our overridden `perform_create` method, which saves the
        # object
        # and handles any `IntegrityError`.
        self.perform_create(serializer)

        # 4. Generate response headers.
        # The `get_success_headers` method is a DRF utility to generate
        # appropriate
        # headers for a successful creation (e.g., `Location` header).
        headers = self.get_success_headers(serializer.data)

        # 5. Return the final, structured response.
        # We provide a clear message and a subset of the non-sensitive user
        # data
        # for a clean and secure API contract.
        return Response(
            {
                "message": "Teacher registered successfully.",
                "data": {
                    "username": serializer.data["username"],
                    "email": serializer.data["email"],
                },
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


# ---------------------------
# Login View
# ---------------------------


class LoginView(TokenObtainPairView):
    """
    API view for user login and JWT token issuance.

    This view uses rest_framework_simplejwt's TokenObtainPairView to handle
    the authentication process. It provides a clean and secure way to
    handle logins, with built-in error messages and a structured
    success response from the custom serializer.
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request for user login.

        The parent `post` method orchestrates the entire process. It will:
        - Validate the username and password using the `LoginSerializer`.
        - If validation fails, it raises an exception, which DRF handles to
          return a 401 Unauthorized response with an appropriate error message.
        - If validation succeeds, it calls the serializer's `validate()` method
          to generate the tokens and add our custom user data.
        - It then returns a 200 OK response with the generated data.

        This override adds a top-level success message for clarity.
        """
        # Call the parent's post method, which handles all the core logic.
        response = super().post(request, *args, **kwargs)

        # Check if the login was successful (HTTP 200 OK).
        if response.status_code == status.HTTP_200_OK:
            # Add a clear, top-level success message to the response data.
            response.data["message"] = "Login successful."

        return response


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {"message": f"Hello, {request.user.username}"},
            status=status.HTTP_200_OK
        )


class ProfileView(APIView):
    """
    API view for retrieving the current user's profile information.

    This endpoint requires authentication and returns a structured response
    containing the user's core details and role-specific profile data.

    - **HTTP Method:** `GET`
    - **Endpoint:** Typically `/api/profile/`
    - **Permissions:** `IsAuthenticated` to ensure the user is logged in.
    """

    # Restricts access to only authenticated users.
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handles the GET request to retrieve the user's profile.

        Args:
            request (Request): The incoming HTTP request object.

        Returns:
            Response: A DRF Response object with the serialized profile data.
        """
        try:
            # 1. Instantiate the serializer with the current authenticated
            # user object.
            #  `request.user` is a User model instance provided by DRF's
            # authentication backend.
            serializer = ProfileSerializer(request.user)

            # 2. Return a structured success response.
            #    Wrapping the data in a dictionary with a message provides a
            # consistent
            #    API contract for the client.
            return Response(
                {
                    "message": "User profile retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            # 3. Handle unexpected server errors.
            #    While the IsAuthenticated permission makes `request.user`
            # reliable,
            #    this provides a final catch for any unforeseen issues.
            return Response(
                {
                    "message": "An unexpected server error occurred.",
                    "error_details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
