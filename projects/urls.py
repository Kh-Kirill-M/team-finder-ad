from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("list/", views.project_list_view, name="list"),
    path("favorites/", views.favorite_projects_view, name="favorites"),
    path("create-project/", views.project_create_view, name="create"),
    path("<int:project_id>/", views.project_detail_view, name="detail"),
    path("<int:project_id>/edit/", views.project_edit_view, name="edit"),
    path(
        "<int:project_id>/complete/",
        views.project_complete_view,
        name="complete",
    ),
    path(
        "<int:project_id>/toggle-participate/",
        views.project_toggle_participate_view,
        name="toggle_participate",
    ),
    path(
        "<int:project_id>/toggle-favorite/",
        views.project_toggle_favorite_view,
        name="toggle_favorite",
    ),
]
