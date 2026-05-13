from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .avatar import generate_avatar
from .managers import UserManager

NAME_MAX_LENGTH = 124
SURNAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
ABOUT_MAX_LENGTH = 256
AVATAR_UPLOAD_DIR = "avatars/"
DEFAULT_AVATAR_LETTER = "?"


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True)
    name = models.CharField("Имя", max_length=NAME_MAX_LENGTH)
    surname = models.CharField("Фамилия", max_length=SURNAME_MAX_LENGTH)
    avatar = models.ImageField("Аватар", upload_to=AVATAR_UPLOAD_DIR)
    phone = models.CharField("Телефон", max_length=PHONE_MAX_LENGTH, unique=True)
    github_url = models.URLField("GitHub", blank=True)
    about = models.TextField("О себе", max_length=ABOUT_MAX_LENGTH, blank=True)

    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
        verbose_name="Избранные проекты",
    )

    is_active = models.BooleanField("Активен", default=True)
    is_staff = models.BooleanField("Сотрудник", default=False)
    date_joined = models.DateTimeField("Дата регистрации", auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname", "phone"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name} {self.surname} ({self.email})"

    def get_full_name(self):
        return f"{self.name} {self.surname}".strip()

    def get_short_name(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.avatar:
            letter = self.name[:1] if self.name else DEFAULT_AVATAR_LETTER
            filename, content = generate_avatar(letter)
            self.avatar.save(filename, content, save=False)
        super().save(*args, **kwargs)
