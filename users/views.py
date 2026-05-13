from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import ChangePasswordForm, LoginForm, ProfileEditForm, RegistrationForm
from .models import User

USERS_PER_PAGE = 12


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect("/projects/list/")
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/projects/list/")
    else:
        form = RegistrationForm()
    return render(request, "users/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("/projects/list/")
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect("/projects/list/")
    else:
        form = LoginForm(request)
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("/projects/list/")


def participants_view(request):
    qs = User.objects.filter(is_active=True).order_by("-id")
    active_filter = ""
    if request.user.is_authenticated:
        active_filter = request.GET.get("filter", "") or ""
        qs = _apply_user_filter(qs, request.user, active_filter)

    paginator = Paginator(qs, USERS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj,
            "page_obj": page_obj,
            "is_paginated": page_obj.has_other_pages(),
            "active_filter": active_filter,
        },
    )


def _apply_user_filter(qs, current_user, key):
    """4 фильтра по варианту 1."""
    if key == "owners-of-favorite-projects":
        return qs.filter(owned_projects__interested_users=current_user).distinct()
    if key == "owners-of-participating-projects":
        return qs.filter(owned_projects__participants=current_user).distinct()
    if key == "interested-in-my-projects":
        return qs.filter(favorites__owner=current_user).distinct()
    if key == "participants-of-my-projects":
        return qs.filter(participated_projects__owner=current_user).distinct()
    return qs


def user_detail_view(request, user_id):
    profile = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": profile})


@login_required(login_url="/users/login/")
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
            return redirect(f"/users/{target.pk}/")
    else:
        form = ProfileEditForm(instance=target)
    return render(request, "users/edit_profile.html", {"form": form, "user": target})


@login_required(login_url="/users/login/")
@require_http_methods(["GET", "POST"])
def change_password_view(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect(f"/users/{request.user.pk}/")
    else:
        form = ChangePasswordForm(request.user)
    return render(request, "users/change_password.html", {"form": form})
