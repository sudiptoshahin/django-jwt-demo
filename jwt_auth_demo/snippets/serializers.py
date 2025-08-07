from rest_framework import serializers
from snippets.models import Snippet
# , LANGUAGE_CHOICES, STYLE_CHOICES
# from django.contrib.auth import get_user_model
from django.http import HttpRequest
from typing import TypedDict, Optional
from user.models import User

# User = get_user_model


# --- define typed dict for snippet data----
class SnippetData(TypedDict, total=False):
    title: str
    code: str
    lineos: bool
    language: str
    style: str


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # here we use tuple `()`` instead of `[]` because they are not going
        # change dynamically
        # fields = ["id", "username"]
        fields = ("id", "username")


class SnippetSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    title = serializers.CharField(required=True, max_length=100)

    class Meta:
        model = Snippet
        # fields = '__all__'
        # fields = ["id", "title", "code", "lineos", "language", "style",
        #           "owner"]
        # here we use tuple `()`` instead of `[]` because they are not going
        # change dynamically
        fields = ("id", "title", "code", "lineos", "language", "style",
                  "owner")
        # read_only_fields = ["id", "owner"]
        read_only_fields = ("id", "owner")

    # field level validation
    def validate_title(self, value: str) -> str:
        if "django" not in value.lower():
            raise serializers.ValidationError(
                'Title must contain the words "django".'
            )
        return value

    # object level validation
    def validate(self, data: SnippetData) -> SnippetData:
        if data["language"] == "javascript" and data["style"] == "friendly":
            raise serializers.ValidationError(
                "Friendly style is not allowed with Javascript language."
            )
        return data

    def create(self, validated_data: SnippetData) -> Snippet:
        # custom logics
        request: Optional[HttpRequest] = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["owner"] = request.user
        print("__request_from_snippet_serializer___", request)
        # custom logics

        return super().create(validated_data)

    def update(self, instance: Snippet,
               validated_data: SnippetData) -> Snippet:
        # write custom logic here
        return super().update(instance, validated_data)


# class SnippetSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     title = serializers.CharField(
#         required=False, alow_blank=True, max_length=100
#     )
#     code = serializers.CharField(style={"base_template": "textarea.html"})
#     lineos = serializers.BooleanField(required=False)
#     language = serializers.ChoiceField(
#         choices=LANGUAGE_CHOICES, default="python"
#     )
#     style = serializers.ChoiceField(
#     choices=STYLE_CHOICES, default="friendly"
# )

#     def create(self, validated_data: SnippetData) -> Snippet:
#         """
#         Create and return a new `Snippet` instance, given the validated_data
#         """
#         return Snippet.objects.create(**validated_data)

#     def updated(self, instance: Snippet,
#                 validated_data: SnippetData) -> Snippet:
#         """
#         Update and return an existing `Snippet` instance, given the validated
#         data.
#         """
#         instance.title = validated_data.get("title", instance.title)
#         instance.code = validated_data.get("code", instance.code)
#         instance.lineos = validated_data.get("lineos", instance.lineos)
#         instance.language = validated_data.get("language", instance.language)
#         instance.style = validated_data.get("style", instance.style)
#         instance.save()
#         return instance
