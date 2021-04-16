from django.apps import AppConfig


class BackendConfig(AppConfig):
    name = 'backend'

    def ready(self):
        import backend.new_email_domain_signal  # noqa
