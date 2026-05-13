from http import HTTPStatus

import pytest
from django.urls import reverse

from projects.models import Project


pytestmark = pytest.mark.django_db


def test_root_redirects_to_project_list(client):
    response = client.get("/")
    assert response.status_code == HTTPStatus.FOUND
    assert response["Location"] == reverse("projects:list")


def test_project_list_renders(client, project):
    response = client.get(reverse("projects:list"))
    assert response.status_code == HTTPStatus.OK
    assert project.name.encode() in response.content


def test_project_detail_renders(client, project):
    response = client.get(reverse("projects:detail", args=[project.id]))
    assert response.status_code == HTTPStatus.OK
    assert project.name.encode() in response.content


def test_create_project_requires_login(client):
    response = client.get(reverse("projects:create"))
    assert response.status_code == HTTPStatus.FOUND
    assert reverse("users:login") in response["Location"]


def test_create_project_flow(client, user):
    client.force_login(user)
    response = client.post(
        reverse("projects:create"),
        data={
            "name": "My new project",
            "description": "desc",
            "github_url": "",
            "status": "open",
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    project = Project.objects.get(name="My new project")
    assert project.owner == user
    assert user in project.participants.all()
    assert response["Location"] == reverse("projects:detail", args=[project.id])


def test_edit_project_forbidden_for_other(client, other_user, project):
    client.force_login(other_user)
    response = client.get(reverse("projects:edit", args=[project.id]))
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_complete_project_owner_only(client, user, other_user, project):
    url = reverse("projects:complete", args=[project.id])
    client.force_login(other_user)
    response = client.post(url)
    assert response.status_code == HTTPStatus.FORBIDDEN

    client.force_login(user)
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data == {"status": "ok", "project_status": "closed"}
    project.refresh_from_db()
    assert project.status == Project.STATUS_CLOSED


def test_toggle_participate(client, other_user, project):
    client.force_login(other_user)
    url = reverse("projects:toggle_participate", args=[project.id])
    r1 = client.post(url)
    assert r1.json() == {"status": "ok", "participant": True}
    assert other_user in project.participants.all()

    r2 = client.post(url)
    assert r2.json() == {"status": "ok", "participant": False}
    assert other_user not in project.participants.all()


def test_toggle_favorite(client, other_user, project):
    client.force_login(other_user)
    url = reverse("projects:toggle_favorite", args=[project.id])
    r1 = client.post(url)
    assert r1.json() == {"status": "ok", "favorited": True}
    assert project in other_user.favorites.all()

    r2 = client.post(url)
    assert r2.json() == {"status": "ok", "favorited": False}


def test_favorites_page_requires_login(client):
    response = client.get(reverse("projects:favorites"))
    assert response.status_code == HTTPStatus.FOUND


def test_favorites_page_for_logged_in(client, user, project):
    user.favorites.add(project)
    client.force_login(user)
    response = client.get(reverse("projects:favorites"))
    assert response.status_code == HTTPStatus.OK
    assert project.name.encode() in response.content


def test_register_creates_and_logs_in(client):
    response = client.post(
        reverse("users:register"),
        data={
            "name": "Bob",
            "surname": "Z",
            "email": "bob@test.com",
            "password": "secretpw",
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response["Location"] == reverse("projects:list")


def test_login_invalid(client, user):
    response = client.post(
        reverse("users:login"),
        data={"email": user.email, "password": "wrong"},
    )
    assert response.status_code == HTTPStatus.OK
    assert "Невер".encode() in response.content


def test_user_list_filter_owners_of_favorite(client, user, other_user):
    project = Project.objects.create(name="P", owner=other_user)
    user.favorites.add(project)
    client.force_login(user)
    url = reverse("users:list") + "?filter=owners-of-favorite-projects"
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert other_user.email.encode() not in response.content  # email скрыт на карточке
    assert other_user.name.encode() in response.content


def test_users_list_pagination_size(client, db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    for i in range(15):
        User.objects.create_user(
            email=f"u{i}@t.com",
            password="x",
            name=f"N{i}",
            surname="S",
            phone=f"+7900000{i:04d}",
        )
    response = client.get(reverse("users:list"))
    assert response.status_code == HTTPStatus.OK
    # На странице должно быть не больше 12 карточек
    cnt = response.content.count(b'<div class="participant-card"')
    assert cnt == 12
