from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver


# ---------------------------
# Custom User Model
# ---------------------------


class User(AbstractUser):
    """
    A custom user model that extends Django's AbstractUser.

    This model adds a 'role' field to categorize users and provides
    methods for role-based logic. It serves as the base for all user types.
    """

    class Role(models.TextChoices):
        """
        Defines the different roles a user can have.
        This provides a clear and consistent way to manage user types.
        """

        ADMIN = "ADMIN", "Admin"
        STUDENT = "STUDENT", "Student"
        TEACHER = "TEACHER", "Teacher"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ADMIN)
    # The `base_role` attribute is used by the proxy models to
    # automatically set the role when a user is created through them.
    base_role = Role.ADMIN

    def save(self, *args, **kwargs):
        """
        Overrides the save method to set the user's role before saving.

        If the user is new (i.e., has no primary key), it sets the
        role to the `base_role` defined in the model or proxy model.
        This ensures that users created through proxy models (e.g., Student,
        Teacher)
        have the correct role assigned automatically.
        """
        if not self.pk:
            self.role = self.role or self._meta.model.base_role
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns a human-readable string representation of the user.
        Includes both the username and their role for clarity.
        """
        return f"{self.username} ({self.role})"

    @property
    def is_student(self):
        """
        A property to check if the user is a student.
        Useful for permissions and conditional logic in templates or views.
        """
        return self.role == self.Role.STUDENT

    @property
    def is_teacher(self):
        """
        A property to check if the user is a teacher.
        Useful for permissions and conditional logic.
        """
        return self.role == self.Role.TEACHER


# ---------------------------
# Custom Managers
# ---------------------------


class StudentManager(BaseUserManager):
    """
    A custom manager for the Student proxy model.

    This manager automatically filters querysets to only include users
    with the 'STUDENT' role. It also provides a custom `create_user` method
    that sets the role to 'STUDENT' by default.
    """

    def get_queryset(self, *args, **kwargs):
        """
        Filters the default queryset to only show users with the 'STUDENT'
        role.
        """
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.STUDENT)

    def create_user(self, username, email, password=None, **extra_fields):
        """
        A custom method to create a new user with the 'STUDENT' role.

        This simplifies the process of creating student accounts and
        ensures the role is set correctly.
        """
        # Call the parent `create_user` method to handle the basic user
        # creation.
        user = super().create_user(
            username=username, email=email, password=password, **extra_fields
        )
        # Explicitly set the role to 'STUDENT'
        user.role = User.Role.STUDENT
        user.save()
        return user


class TeacherManager(BaseUserManager):
    """
    A custom manager for the Teacher proxy model.

    Similar to `StudentManager`, this manager filters querysets for 'TEACHER'
    and provides a `create_user` method for creating teacher accounts.
    """

    def get_queryset(self, *args, **kwargs):
        """
        Filters the default queryset to only show users with the 'TEACHER'
        role.
        """
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.TEACHER)

    def create_user(self, username, email, password=None, **extra_fields):
        """
        A custom method to create a new user with the 'TEACHER' role.
        """
        user = super().create_user(
            username=username, email=email, password=password, **extra_fields
        )
        user.role = User.Role.TEACHER
        user.save()
        return user


# ---------------------------
# Proxy Models
# ---------------------------
class Student(User):
    """
    A proxy model for the 'Student' user role.

    Proxy models are used to change the Python-level behavior of a model
    without changing its database schema. This model uses the `StudentManager`
    and sets the `base_role` to 'STUDENT', ensuring that users created
    through this model are automatically students.
    """

    base_role = User.Role.STUDENT
    objects = StudentManager()

    class Meta:
        proxy = True  # This is the key to making it a proxy model.

    def welcome(self):
        """
        A custom method specific to the 'Student' role.
        This demonstrates how proxy models can be used to add
        role-specific functionality.
        """
        return "Only for Student"


class Teacher(User):
    """
    A proxy model for the 'Teacher' user role.

    Similar to `Student`, this provides a way to interact with 'Teacher'
    users separately and add specific methods or managers.
    """

    base_role = User.Role.TEACHER
    objects = TeacherManager()

    class Meta:
        proxy = True

    def welcome(self):
        """
        A custom method specific to the 'Teacher' role.
        """
        return "Only for Teacher"


# ---------------------------
# Profile Models
# ---------------------------


class StudentProfile(models.Model):
    """
    A one-to-one profile model for student users.

    This model holds additional information specific to students that
    doesn't belong directly in the core `User` model, following the
    best practice of separating user authentication from user details.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        """
        Returns a string representation of the student profile.
        """
        return f"Student Profile: {self.user.username}"


class TeacherProfile(models.Model):
    """
    A one-to-one profile model for teacher users.

    Similar to `StudentProfile`, this holds teacher-specific information.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    teacher_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        """
        Returns a string representation of the teacher profile.
        """
        return f"Teacher Profile: {self.user.username}"


# ---------------------------
# Signals
# ---------------------------


@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance, created, **kwargs):
    """
    A Django signal to automatically create a profile for a new user.

    This function is triggered every time a `User` instance is saved.

    `post_save` is a signal sent at the end of the save() method.
    `sender` is the model class (User).
    `instance` is the actual instance being saved.
    `created` is a boolean; True if a new record was created, False otherwise.

    If a new user is created (`created=True`), this signal checks their role
    and automatically creates a corresponding `StudentProfile` or
    `TeacherProfile`.
    This ensures that every new user has a profile, preventing `DoesNotExist`
    errors
    when trying to access `user.studentprofile`.
    """
    # Only run this logic if a new user instance was just created.
    if not created:
        return

    # Check the user's role and create the appropriate profile.
    if instance.role == User.Role.STUDENT:
        # get_or_create is used to prevent duplicate profiles if the signal is
        # triggered multiple times (e.g., in a test environment).
        StudentProfile.objects.get_or_create(user=instance)

    elif instance.role == User.Role.TEACHER:
        TeacherProfile.objects.get_or_create(user=instance)
