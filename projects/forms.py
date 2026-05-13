from django import forms

from users.validators import validate_github_url

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
            "status": "Статус",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "status": forms.Select(choices=[
                (Project.STATUS_OPEN, "Открыт"),
                (Project.STATUS_CLOSED, "Закрыт"),
            ]),
        }

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise forms.ValidationError("Название обязательно.")
        return name

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "")
        validate_github_url(url)
        return url
