from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from user.models import StudentProfile, TeacherProfile, Student, Teacher
User = get_user_model()


# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ("username", "email", "password")

#     def create(self, validate_data):
#         user = User.objects.create_user(
#             username=validate_data["username"],
#             email=validate_data["email"],
#             password=validate_data["password"],
#         )
#         return user


# class LoginSerializer(TokenObtainPairSerializer):
#     def validate(self, attrs):
#         data = super().validate(attrs)
#         data["user_id"] = self.user.id
#         data["username"] = self.user.username
#         data["email"] = self.user.email
#         return data

class StudentRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = Student.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class TeacherRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
    
    def create(self, validated_data):
        user = Teacher.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['role'] = self.user.role
        return data


# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ["id", "username", "email", "first_name", "last_name"]


class ProfileSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'profile']

    def get_profile(self, obj):
        if obj.role == User.Role.STUDENT:
            profile = getattr(obj, 'studentprofile', None)
            return {"student_id": profile.student_id} if profile else None
        elif obj.role == User.Role.TEACHER:
            profile = getattr(obj, 'teacherprofile', None)
            return {"teacher_id": profile.teacher_id} if profile else None