from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_default_schedule(sender, **kwargs):
    from django_celery_beat.models import PeriodicTask, IntervalSchedule

    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.HOURS,
    )

    PeriodicTask.objects.get_or_create(
        name='Update Cryptocurrency Prices',
        task='api.tasks.update_crypto_prices',
        interval=schedule,
        enabled=True
    )


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        post_migrate.connect(create_default_schedule, sender=self)
