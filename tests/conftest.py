import pytest
from django.contrib.auth import get_user_model

from projects.models import Project

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="user@test.com",
        password="pw12345",
        name="Тест",
        surname="Пользователь",
        phone="+79991112233",
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        email="other@test.com",
        password="pw12345",
        name="Другой",
        surname="Юзер",
        phone="+79992223344",
    )


@pytest.fixture
def project(db, user):
    project = Project.objects.create(
        name="Test Project",
        description="Hello",
        owner=user,
        status=Project.STATUS_OPEN,
    )
    project.participants.add(user)
    return project
