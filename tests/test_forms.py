import pytest

from projects.forms import ProjectForm
from users.forms import ProfileEditForm, RegistrationForm
from users.validators import normalize_phone, validate_github_url, validate_phone
from django.core.exceptions import ValidationError


pytestmark = pytest.mark.django_db


def test_phone_validation_ok():
    validate_phone("+79991112233")
    validate_phone("89991112233")


@pytest.mark.parametrize("bad", ["12345", "+7999111", "abcdefgh", "799911122334"])
def test_phone_validation_bad(bad):
    with pytest.raises(ValidationError):
        validate_phone(bad)


def test_phone_normalize():
    assert normalize_phone("89991112233") == "+79991112233"
    assert normalize_phone("+79991112233") == "+79991112233"


def test_github_validation_ok():
    validate_github_url("https://github.com/foo/bar")
    validate_github_url("https://github.com/")
    validate_github_url("")  # пустое допустимо


@pytest.mark.parametrize(
    "bad",
    [
        "https://gitlab.com/foo",
        "ftp://github.com/foo",
        "not a url",
        "https://evil.com/github.com",
    ],
)
def test_github_validation_bad(bad):
    with pytest.raises(ValidationError):
        validate_github_url(bad)


def test_registration_creates_user():
    form = RegistrationForm(data={
        "name": "Ann",
        "surname": "Smith",
        "email": "ann@test.com",
        "password": "secretpw",
    })
    assert form.is_valid(), form.errors
    user = form.save()
    assert user.email == "ann@test.com"
    assert user.check_password("secretpw")
    assert user.phone.startswith("+7")


def test_registration_rejects_duplicate_email(user):
    form = RegistrationForm(data={
        "name": "X",
        "surname": "Y",
        "email": user.email,
        "password": "secretpw",
    })
    assert not form.is_valid()
    assert "email" in form.errors


def test_profile_edit_phone_unique(user, other_user):
    form = ProfileEditForm(
        data={
            "name": user.name,
            "surname": user.surname,
            "about": "",
            "phone": other_user.phone,
            "github_url": "",
        },
        instance=user,
    )
    assert not form.is_valid()
    assert "phone" in form.errors


def test_project_form_requires_name(user):
    form = ProjectForm(data={
        "name": "",
        "description": "x",
        "github_url": "",
        "status": "open",
    })
    assert not form.is_valid()
    assert "name" in form.errors


def test_project_form_validates_github(user):
    form = ProjectForm(data={
        "name": "Ok",
        "description": "x",
        "github_url": "https://gitlab.com/foo",
        "status": "open",
    })
    assert not form.is_valid()
    assert "github_url" in form.errors
