from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import ProjectForm
from .models import Project

PROJECTS_PER_PAGE = 12

PAGE_QUERY_PARAM = "page"

PROJECT_LIST_TEMPLATE = "projects/project_list.html"
PROJECT_DETAIL_TEMPLATE = "projects/project-details.html"
PROJECT_CREATE_TEMPLATE = "projects/create-project.html"
PROJECT_FAVORITES_TEMPLATE = "projects/favorite_projects.html"

ROUTE_PROJECT_DETAIL = "projects:detail"


def _paginate(request, queryset, per_page=PROJECTS_PER_PAGE):
    """Единая точка пагинации для всех view проектов."""
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(request.GET.get(PAGE_QUERY_PARAM))
    return {
        "projects": page_obj,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
    }


@require_GET
def project_list_view(request):
    qs = (
        Project.objects.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at", "-id")
    )
    return render(request, PROJECT_LIST_TEMPLATE, _paginate(request, qs))


@require_GET
def project_detail_view(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=project_id,
    )
    return render(request, PROJECT_DETAIL_TEMPLATE, {"project": project})


@login_required
@require_http_methods(["GET", "POST"])
def project_create_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(ROUTE_PROJECT_DETAIL, project_id=project.id)
    else:
        form = ProjectForm()
    return render(
        request,
        PROJECT_CREATE_TEMPLATE,
        {"form": form, "is_edit": False},
    )


@login_required
@require_http_methods(["GET", "POST"])
def project_edit_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id and not request.user.is_staff:
        return HttpResponseForbidden("Нет прав на редактирование")

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(ROUTE_PROJECT_DETAIL, project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(
        request,
        PROJECT_CREATE_TEMPLATE,
        {"form": form, "is_edit": True},
    )


@login_required
@require_POST
def project_complete_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id:
        return JsonResponse(
            {"status": "error", "message": "forbidden"},
            status=HTTPStatus.FORBIDDEN,
        )
    if project.status != Project.STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "message": "already closed"},
            status=HTTPStatus.BAD_REQUEST,
        )
    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": project.status})


@login_required
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


@login_required
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


@login_required
@require_GET
def favorite_projects_view(request):
    qs = (
        request.user.favorites.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at", "-id")
    )
    return render(request, PROJECT_FAVORITES_TEMPLATE, _paginate(request, qs))
