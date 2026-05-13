from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import ProjectForm
from .models import Project

PROJECTS_PER_PAGE = 12


@require_GET
def project_list_view(request):
    qs = (
        Project.objects.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at", "-id")
    )
    paginator = Paginator(qs, PROJECTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "projects/project_list.html",
        {
            "projects": page_obj,
            "page_obj": page_obj,
            "is_paginated": page_obj.has_other_pages(),
        },
    )


@require_GET
def project_detail_view(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required(login_url="/users/login/")
@require_http_methods(["GET", "POST"])
def project_create_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(f"/projects/{project.id}/")
    else:
        form = ProjectForm()
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required(login_url="/users/login/")
@require_http_methods(["GET", "POST"])
def project_edit_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id and not request.user.is_staff:
        return HttpResponseForbidden("Нет прав на редактирование")

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(f"/projects/{project.id}/")
    else:
        form = ProjectForm(instance=project)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True},
    )


@login_required(login_url="/users/login/")
@require_POST
def project_complete_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id:
        return JsonResponse({"status": "error", "message": "forbidden"}, status=403)
    if project.status != Project.STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "message": "already closed"},
            status=400,
        )
    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": project.status})


@login_required(login_url="/users/login/")
@require_POST
def project_toggle_participate_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({"status": "ok", "participant": participant})


@login_required(login_url="/users/login/")
@require_POST
def project_toggle_favorite_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    if user.favorites.filter(pk=project.pk).exists():
        user.favorites.remove(project)
        favorited = False
    else:
        user.favorites.add(project)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})


@login_required(login_url="/users/login/")
@require_GET
def favorite_projects_view(request):
    qs = (
        request.user.favorites.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at", "-id")
    )
    paginator = Paginator(qs, PROJECTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "projects/favorite_projects.html",
        {
            "projects": page_obj,
            "page_obj": page_obj,
            "is_paginated": page_obj.has_other_pages(),
        },
    )
