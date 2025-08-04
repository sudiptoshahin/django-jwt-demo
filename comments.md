"""
===========================
JWT Authentication in Django REST Framework
===========================

This project uses **JWT (JSON Web Token)** authentication via the `djangorestframework-simplejwt` package.

Why JWT?
--------
JWT is a stateless, secure, and scalable token-based authentication method that enables frontend-backend separation and is ideal for APIs.

Overview
--------
We have implemented user authentication and registration with different roles (Admin, Student, Teacher).
Each user has a role assigned, and additional profile data is stored in role-specific profile models.

Step-by-Step Implementation
---------------------------

1. **Custom User Model (`User`)**
   - Inherits from `AbstractUser`.
   - Adds a `role` field with choices: ADMIN, STUDENT, TEACHER.
   - Uses a base role in proxy models to automatically assign roles during creation.

2. **Proxy Models for Roles**
   - `Student` and `Teacher` are proxy models of `User`.
   - Each has its own custom manager to filter users by role.
   - Each has a related `StudentProfile` or `TeacherProfile` for extra data.

3. **Custom Managers**
   - `StudentManager` and `TeacherManager` override `get_queryset()` to filter by role.
   - Optional `create_user()` methods can be added here for DRY user creation logic.

4. **Signals**
   - When a `Student` or `Teacher` is created, a `post_save` signal triggers automatic creation of related `Profile` objects.

5. **JWT Integration**
   - Using `rest_framework_simplejwt`:
     - `TokenObtainPairSerializer` subclass is used to return user data with tokens on login.
     - Access and Refresh tokens are issued.

6. **Serializers**
   - `StudentRegisterSerializer` and `TeacherRegisterSerializer`:
     - Used to register users of respective roles.
     - Uses the appropriate manager to create the user and assign the correct role.
   - `LoginSerializer`:
     - Subclasses `TokenObtainPairSerializer`.
     - Adds extra fields (`username`, `email`, `role`, `user_id`) in the token response.
   - `ProfileSerializer`:
     - Returns user data including nested profile fields depending on role (e.g., `student_id` or `teacher_id`).

7. **Registration Flow**
   - Users register via `/register/student/` or `/register/teacher/` (example endpoint names).
   - Appropriate serializer assigns role and saves user.
   - Profile object is automatically created.

8. **Login Flow**
   - User logs in via `/api/token/` with username/email and password.
   - If credentials are valid, a pair of JWT tokens (access + refresh) is returned with user details.

9. **Protected Endpoints**
   - Use `@permission_classes([IsAuthenticated])` or `IsAuthenticated` class to protect API views.
   - Frontend must attach the `Authorization: Bearer <access_token>` header to access protected resources.

10. **Token Refreshing**
    - Clients can call `/api/token/refresh/` with a refresh token to get a new access token.

Dependencies
------------
- `djangorestframework`
- `djangorestframework-simplejwt`

Install with:
```bash
pip install djangorestframework djangorestframework-simplejwt
