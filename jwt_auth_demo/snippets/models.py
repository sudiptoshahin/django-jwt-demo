from django.db import models
from pygments.lexers import get_all_lexers
from user.models import User
# from pygments.styles import get_all_styles
# from user.models import User
# from django.contrib.auth import get_user_model
from typing import List, Tuple
from datetime import datetime

# User = get_user_model()

LEXERS = [item for item in get_all_lexers() if item[1]]
# LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
# STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])
LANGUAGE_CHOICES: List[Tuple[str, str]] = [
    ("python", "Python"),
    ("javascript", "JavaScript"),
]

STYLE_CHOICES: List[Tuple[str, str]] = [
    ("friendly", "Friendly"),
    ("monokai", "Monokai"),
]


class Snippet(models.Model):
    created: datetime = models.DateTimeField(auto_now_add=True)
    title: str = models.CharField(max_length=100, blank=True, default="")
    code: str = models.TextField()
    lineos: bool = models.BooleanField(default=False)
    language: str = models.CharField(
        choices=LANGUAGE_CHOICES, default="python", max_length=100
    )
    style: str = models.CharField(choices=STYLE_CHOICES, default="friendly",
                                  max_length=100)
    owner = models.ForeignKey(
        User, related_name="snippets", on_delete=models.CASCADE, null=True
    )

    class Meta:
        ordering = ["created"]
