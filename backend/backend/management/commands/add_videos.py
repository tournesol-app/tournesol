from django.core.management.base import BaseCommand
from backend.add_videos import VideoManager
from inspect import signature
from django_react.settings import load_gin_config


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--config', help="Gin configuration file",
                            type=str, default='backend/add_videos.gin')
        parser.add_argument('--only_download', help='Only download these (useful for debugging)',
                            action='append',
                            default=None)
        parser.add_argument('--console', help='Run console', type=bool)

    def handle(self, **options):
        load_gin_config(options['config'])
        try:
            vm = VideoManager(only_download=options['only_download'])
        except Exception as e:
            print("Arguments are wrong, initialization failed")
            print(e)
            return None

        if options['console']:
            commands = [x for x in dir(vm) if not x.startswith(
                '_') and callable(getattr(vm, x))]
            print("Available commands: ", commands)
            print("Type exit to stop")
            while True:
                print("> ", end="")
                inp = input().strip()
                if inp in commands:
                    f = getattr(vm, inp)
                    print(signature(f))
                    f()
                elif inp == 'exit':
                    return None
                else:
                    print("Unknown command")
                    print("Available commands: ", commands)
                    print("Type exit to stop")
        else:
            print("Doing default import")
            vm.fill_info()
            vm.add_videos_in_folder_to_db()
            vm.clear_info()
