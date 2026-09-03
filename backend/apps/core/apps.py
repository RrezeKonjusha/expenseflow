from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "apps.core"
    label = "core"
    verbose_name = "Core (shared)"

    def ready(self):
        from .mongo import connect_mongo

        connect_mongo()
