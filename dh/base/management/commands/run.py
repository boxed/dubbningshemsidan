from importlib import import_module

from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Runs the named task'

    def add_arguments(self, parser):
        parser.add_argument('task_name', type=str)
        parser.add_argument('arguments', nargs='*', type=str)

    def handle(self, *args, **options):
        task_name = options['task_name']

        tasks = {}
        for app_name, app in apps.app_configs.items():
            try:
                task_module_name = f'{app.module.__name__}.tasks'
                for name, variable in import_module(task_module_name).__dict__.items():
                    if not name.startswith('_') and getattr(variable, '_is_task', False):
                        assert name not in tasks
                        tasks[name] = variable
            except ImportError:
                pass

        if task_name not in tasks:
            print('Valid tasks:')
            for name in sorted(tasks.keys()):
                print('   ', name)

            return

        task = tasks[task_name]
        print(task(*options['arguments']))
