from backend.constants import fields, comments
from django.core.management.base import BaseCommand
from backend.python_to_js import generate_js_code


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--file', help='File to save data to', type=str,
                            default=None)

    def handle(self, **options):
        prefix = "// Tournesol constants file\n"
        prefix += "// Auto-generated file by generate_js_code python function\n"

        if options['file'] is not None:
            prefix += "// To re-create, run backend $ python manage.py " \
                      f"js_constants --file {options['file']}\n"

        prefix += '\n'

        code = generate_js_code(data=fields, comments=comments, prefix=prefix)

        if options['file'] is None:
            print(code)
        else:
            with open(options['file'], 'w') as f:
                f.write(code)
