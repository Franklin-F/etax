import sys
import time
import importlib
import traceback
import subprocess
from django.core.management.base import BaseCommand
from lib.select import select


class Command(BaseCommand):
    help = 'Call method on a select of models'

    def add_arguments(self, parser):
        parser.add_argument("model", type=str, help="Model to range")
        parser.add_argument("func", type=str, nargs='?', help="Call model func")
        parser.add_argument("--module", type=str, default='agent.models', help="Module to import")
        parser.add_argument("--noshow", action='store_true', help="NOT Show model info & delineate border")
        parser.add_argument("--sleep", type=float, help="Sleep seconds between processing models")
        parser.add_argument("--nocatch", action='store_true', help="DO NOT catch exception")
        parser.add_argument("--condition", "-c", type=str, help="Process condition")

        parser.add_argument("--id", type=str, help="Model ID")
        parser.add_argument("--ids", type=str, help="Model IDS")
        parser.add_argument("--minid", type=int, help="Model Min ID")
        parser.add_argument("--maxid", type=int, help="Model Max ID")
        parser.add_argument("--slice", type=str, help="Slice pair divider,remainder like 8,0 or 8,1")
        parser.add_argument("--reverse", "-r", action='store_true', default=False, help="Process model in reverse order")
        parser.add_argument("--limit", type=int, help="Limit num")
        parser.add_argument("--where", "-w", type=str, help="Mysql where query")
        parser.add_argument("--chunk", type=int, default=1000, help="Chunk size")
        parser.add_argument("--pk", type=str, default='id', help="Model Primary Key name")

        parser.add_argument("arg1", type=str, nargs='?', help="Call model func arg 1")
        parser.add_argument("arg2", type=str, nargs='?', help="Call model func arg 2")
        parser.add_argument("arg3", type=str, nargs='?', help="Call model func arg 3")
        parser.add_argument("arg4", type=str, nargs='?', help="Call model func arg 4")
        parser.add_argument("arg5", type=str, nargs='?', help="Call model func arg 5")
        parser.add_argument("arg6", type=str, nargs='?', help="Call model func arg 6")
        parser.add_argument("arg7", type=str, nargs='?', help="Call model func arg 7")
        parser.add_argument("arg8", type=str, nargs='?', help="Call model func arg 8")
        parser.add_argument("arg9", type=str, nargs='?', help="Call model func arg 9")

    def handle(self, *args, **options):
        self.args = args
        self.options = options
        if options['slice'] and options['slice'].isdigit():
            self.slice()
        else:
            self.process()

    def slice(self):
        python = sys.executable
        if sys.platform == 'win32':
            python = python.replace('\\', '\\\\').replace('\\', '\\\\')
            python = f"cmd /c {python}"

        arg_names = ['model', 'func', 'arg1', 'arg2', 'arg3', 'arg4', 'arg5', 'arg6', 'arg7', 'arg8', 'arg9']
        kwarg_names = {
            'module': 'apps.home.models',
            'reverse': False,
            'noshow': False,
            'pk': 'id',
            'sleep': None,
            'nocatch': False,
            'id': None,
            'minid': None,
            'maxid': None,
            'condition': None,
            'where': None,
            'chunk': 1000,
            'limit': None,
        }
        args = []
        for name in arg_names:
            if self.options.get(name) is not None:
                args.append(self.options.get(name))
        for name, default in kwarg_names.items():
            if self.options.get(name) is not default and self.options.get(name) != default:
                args.append(f'--{name}={self.options.get(name)}')
        nums = int(self.options['slice'])
        for num in range(nums):
            newslice = f'--slice="{nums},{num}"'
            newargs = args + [newslice]
            newargs = ' '.join(newargs)
            cmd = f"{python} manage.py select {newargs}"
            bash = f"bash --init-file <(echo '{cmd}')"
            screen = f'screen bash -c "{bash}; bash"'
            subprocess.run(screen, shell=True)

    def get_cls(self):
        mdl_name = self.options['module']
        cls_name = self.options['model']
        mdl = importlib.import_module(mdl_name)
        cls = getattr(mdl, cls_name)
        return cls

    def get_args(self):
        args = []
        for i in range(1, 10):
            arg = self.options.get(f'arg{i}')
            if arg is None:
                continue
            elif arg == 'None':
                arg = None
            elif arg == 'True':
                arg = True
            elif arg == 'False':
                arg = False
            elif arg.isdigit():
                arg = int(arg)
            elif arg.isnumeric():
                arg = float(arg)
            args.append(arg)
        return args

    def get_filters(self):
        keys = [
            'id',
            'ids',
            'minid',
            'maxid',
            'slice',
            'reverse',
            'limit',
            'where',
            'chunk',
            'pk',
        ]
        filters = {key: self.options.get(key) for key in keys}
        return filters

    def process(self):
        cls = self.get_cls()
        args = self.get_args()
        filters = self.get_filters()
        for model in select(cls, **filters):
            self.process_model(model, *args)

    def need_process(self, model):
        if not self.options['condition']:
            return True
        func = getattr(model, self.options['condition'])
        return func()

    def process_model(self, model, *args, **kwargs):
        if not self.need_process(model):
            return
        if not self.options['noshow']:
            print('=' * 30)
            print(model)
        if not self.options['func']:
            return
        func = getattr(model, self.options['func'])
        ret = None
        try:
            ret = func(*args, **kwargs)
        except Exception as err:
            if self.options['nocatch']:
                raise
            print(err)
            traceback.print_exc()
        if not self.options['noshow']:
            print(ret)
        if self.options['sleep']:
            time.sleep(self.options['sleep'])
