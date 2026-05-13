from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .avatar import generate_avatar
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True)
    name = models.CharField("Имя", max_length=124)
    surname = models.CharField("Фамилия", max_length=124)
    avatar = models.ImageField("Аватар", upload_to="avatars/")
    phone = models.CharField("Телефон", max_length=12, unique=True)
    github_url = models.URLField("GitHub", blank=True)
    about = models.TextField("О себе", max_length=256, blank=True)

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
            filename, content = generate_avatar(self.name[:1] if self.name else "?")
            self.avatar.save(filename, content, save=False)
        super().save(*args, **kwargs)
