from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from .models import User
from .validators import normalize_phone, validate_github_url, validate_phone


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(),
        min_length=4,
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        # phone обязателен в модели — на регистрации его нет,
        # ставим уникальную заглушку и просим заполнить в профиле.
        user.phone = self._make_placeholder_phone()
        if commit:
            user.save()
        return user

    @staticmethod
    def _make_placeholder_phone():
        """Уникальный placeholder в формате +7XXXXXXXXXX до заполнения профиля."""
        import secrets
        while True:
            tail = "".join(str(secrets.randbelow(10)) for _ in range(10))
            candidate = "+7" + tail
            if not User.objects.filter(phone=candidate).exists():
                return candidate


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput())

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if email and password:
            user = authenticate(self.request, username=email, password=password)
            if user is None:
                raise forms.ValidationError("Неверный email или пароль")
            if not user.is_active:
                raise forms.ValidationError("Учётная запись отключена")
            self.user = user
        return cleaned


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "Ссылка на GitHub",
        }
        widgets = {
            "avatar": forms.ClearableFileInput(attrs={"id": "id_avatar"}),
            "about": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        validate_phone(phone)
        normalized = normalize_phone(phone)
        qs = User.objects.filter(phone=normalized)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Этот номер уже используется.")
        return normalized

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "")
        validate_github_url(url)
        return url


class ChangePasswordForm(PasswordChangeForm):
    """Стандартная форма Django с русскими лейблами."""

    error_messages = {
        **PasswordChangeForm.error_messages,
        "password_incorrect": "Неверный текущий пароль.",
        "password_mismatch": "Пароли не совпадают.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = "Текущий пароль"
        self.fields["new_password1"].label = "Новый пароль"
        self.fields["new_password2"].label = "Подтвердите новый пароль"
