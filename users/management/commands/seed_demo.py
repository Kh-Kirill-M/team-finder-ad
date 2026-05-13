"""Создаёт тестовых пользователей и проекты.

Использование:
    python manage.py seed_demo            # создаёт стандартный набор
    python manage.py seed_demo --reset    # удаляет всё и пересоздаёт
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from projects.models import Project

User = get_user_model()


DEMO_USERS = [
    {
        "email": "maria@yandex.ru",
        "password": "password",
        "name": "Мария",
        "surname": "Иванова",
        "phone": "+79161112233",
        "about": "Бэкенд-разработчик, ищу команду для пет-проекта.",
        "github_url": "https://github.com/maria",
    },
    {
        "email": "ivan@yandex.ru",
        "password": "password",
        "name": "Иван",
        "surname": "Петров",
        "phone": "+79162223344",
        "about": "Фронтенд на React. Открыт к коллаборации.",
        "github_url": "https://github.com/ivan",
    },
    {
        "email": "olga@yandex.ru",
        "password": "password",
        "name": "Ольга",
        "surname": "Сидорова",
        "phone": "+79163334455",
        "about": "Дизайнер интерфейсов, ux/ui.",
        "github_url": "",
    },
    {
        "email": "alex@yandex.ru",
        "password": "password",
        "name": "Алексей",
        "surname": "Кузнецов",
        "phone": "+79164445566",
        "about": "DevOps. Помогу настроить инфраструктуру.",
        "github_url": "https://github.com/alex",
    },
]

DEMO_PROJECTS = [
    {
        "owner_email": "maria@yandex.ru",
        "name": "TeamFinder",
        "description": (
            "Платформа, на которой разработчики, дизайнеры и другие специалисты "
            "находят единомышленников для совместной работы над pet-проектами."
        ),
        "status": Project.STATUS_OPEN,
        "github_url": "https://github.com/maria/teamfinder",
    },
    {
        "owner_email": "ivan@yandex.ru",
        "name": "Async Chat",
        "description": "Чат на Django Channels с поддержкой групповых комнат.",
        "status": Project.STATUS_OPEN,
        "github_url": "https://github.com/ivan/async-chat",
    },
    {
        "owner_email": "olga@yandex.ru",
        "name": "Дизайн-система TeamFinder",
        "description": "UI-кит и набор компонентов для веб-сервиса.",
        "status": Project.STATUS_OPEN,
        "github_url": "",
    },
    {
        "owner_email": "alex@yandex.ru",
        "name": "DevOps Toolbox",
        "description": "Набор инструментов для развёртывания Django-проектов в Docker.",
        "status": Project.STATUS_CLOSED,
        "github_url": "https://github.com/alex/devops-toolbox",
    },
    {
        "owner_email": "maria@yandex.ru",
        "name": "PetShop API",
        "description": "REST API на DRF для интернет-магазина зоотоваров.",
        "status": Project.STATUS_OPEN,
        "github_url": "",
    },
]


class Command(BaseCommand):
    help = "Создаёт тестовых пользователей и проекты для ревью."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Удалить демо-данные перед созданием.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self._reset()

        users_by_email = {}
        for data in DEMO_USERS:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "name": data["name"],
                    "surname": data["surname"],
                    "phone": data["phone"],
                    "about": data["about"],
                    "github_url": data["github_url"],
                },
            )
            if created:
                user.set_password(data["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Создан {user.email}"))
            else:
                self.stdout.write(f"Пропущен (уже есть): {user.email}")
            users_by_email[data["email"]] = user

        for proj in DEMO_PROJECTS:
            owner = users_by_email[proj["owner_email"]]
            project, created = Project.objects.get_or_create(
                name=proj["name"],
                owner=owner,
                defaults={
                    "description": proj["description"],
                    "status": proj["status"],
                    "github_url": proj["github_url"],
                },
            )
            if created:
                project.participants.add(owner)
                self.stdout.write(self.style.SUCCESS(f"Создан проект: {project.name}"))
            else:
                self.stdout.write(f"Пропущен проект (уже есть): {project.name}")

        # перекрёстные участия и избранное — чтобы было что показать
        maria = users_by_email["maria@yandex.ru"]
        ivan = users_by_email["ivan@yandex.ru"]
        olga = users_by_email["olga@yandex.ru"]

        tf = Project.objects.filter(name="TeamFinder", owner=maria).first()
        chat = Project.objects.filter(name="Async Chat", owner=ivan).first()
        if tf:
            tf.participants.add(ivan, olga)
            olga.favorites.add(tf)
        if chat:
            maria.favorites.add(chat)

        self.stdout.write(self.style.SUCCESS("Готово."))

    def _reset(self):
        emails = [d["email"] for d in DEMO_USERS]
        Project.objects.filter(owner__email__in=emails).delete()
        User.objects.filter(email__in=emails).delete()
        self.stdout.write(self.style.WARNING("Демо-данные удалены."))
