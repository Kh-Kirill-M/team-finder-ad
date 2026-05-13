from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import ChangePasswordForm, LoginForm, ProfileEditForm, RegistrationForm
from .models import User

USERS_PER_PAGE = 12
PAGE_QUERY_PARAM = "page"
FILTER_QUERY_PARAM = "filter"

FILTER_OWNERS_OF_FAVORITE_PROJECTS = "owners-of-favorite-projects"
FILTER_OWNERS_OF_PARTICIPATING_PROJECTS = "owners-of-participating-projects"
FILTER_INTERESTED_IN_MY_PROJECTS = "interested-in-my-projects"
FILTER_PARTICIPANTS_OF_MY_PROJECTS = "participants-of-my-projects"

ALLOWED_USER_FILTERS = frozenset({
    FILTER_OWNERS_OF_FAVORITE_PROJECTS,
    FILTER_OWNERS_OF_PARTICIPATING_PROJECTS,
    FILTER_INTERESTED_IN_MY_PROJECTS,
    FILTER_PARTICIPANTS_OF_MY_PROJECTS,
})

ROUTE_USER_DETAIL = "users:detail"
ROUTE_PROJECTS_LIST = "projects:list"

REGISTER_TEMPLATE = "users/register.html"
LOGIN_TEMPLATE = "users/login.html"
PARTICIPANTS_TEMPLATE = "users/participants.html"
USER_DETAIL_TEMPLATE = "users/user-details.html"
EDIT_PROFILE_TEMPLATE = "users/edit_profile.html"
CHANGE_PASSWORD_TEMPLATE = "users/change_password.html"


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect(ROUTE_PROJECTS_LIST)
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(ROUTE_PROJECTS_LIST)
    else:
        form = RegistrationForm()
    return render(request, REGISTER_TEMPLATE, {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect(ROUTE_PROJECTS_LIST)
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect(ROUTE_PROJECTS_LIST)
    else:
        form = LoginForm(request)
    return render(request, LOGIN_TEMPLATE, {"form": form})


def logout_view(request):
    logout(request)
    return redirect(ROUTE_PROJECTS_LIST)


def participants_view(request):
    qs = User.objects.filter(is_active=True).order_by("-id")
    active_filter = ""
    if request.user.is_authenticated:
        active_filter = request.GET.get(FILTER_QUERY_PARAM, "") or ""
        qs = _apply_user_filter(qs, request.user, active_filter)

    paginator = Paginator(qs, USERS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get(PAGE_QUERY_PARAM))

    return render(
        request,
        PARTICIPANTS_TEMPLATE,
        {
            "participants": page_obj,
            "page_obj": page_obj,
            "is_paginated": page_obj.has_other_pages(),
            "active_filter": active_filter,
        },
    )


def _apply_user_filter(qs, current_user, key):
    """4 фильтра по варианту 1."""
    if key not in ALLOWED_USER_FILTERS:
        return qs
    if key == FILTER_OWNERS_OF_FAVORITE_PROJECTS:
        return qs.filter(owned_projects__interested_users=current_user).distinct()
    if key == FILTER_OWNERS_OF_PARTICIPATING_PROJECTS:
        return qs.filter(owned_projects__participants=current_user).distinct()
    if key == FILTER_INTERESTED_IN_MY_PROJECTS:
        return qs.filter(favorites__owner=current_user).distinct()
    if key == FILTER_PARTICIPANTS_OF_MY_PROJECTS:
        return qs.filter(participated_projects__owner=current_user).distinct()
    return qs


def user_detail_view(request, user_id):
    profile = get_object_or_404(User, pk=user_id)
    return render(request, USER_DETAIL_TEMPLATE, {"user": profile})


@login_required
@require_http_methods(["GET", "POST"])
def edit_profile_view(request, user_id=None):
    if user_id is None:
        target = request.user
    else:
        target = get_object_or_404(User, pk=user_id)
        if target.pk != request.user.pk and not request.user.is_staff:
            return HttpResponseForbidden("Нет прав на редактирование")

    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=target)
        if form.is_valid():
            form.save()
            return redirect(ROUTE_USER_DETAIL, user_id=target.pk)
    else:
        form = ProfileEditForm(instance=target)
    return render(request, EDIT_PROFILE_TEMPLATE, {"form": form, "user": target})


@login_required
@require_http_methods(["GET", "POST"])
def change_password_view(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect(ROUTE_USER_DETAIL, user_id=request.user.pk)
    else:
        form = ChangePasswordForm(request.user)
    return render(request, CHANGE_PASSWORD_TEMPLATE, {"form": form})
