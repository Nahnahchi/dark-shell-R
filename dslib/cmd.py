from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.shortcuts import prompt
from traceback import format_exc
from colorama import Fore
from sys import _getframe


class CmdParser:

    def __init__(self, args: str):
        args = args.split()
        self.command = args[0] if len(args) > 0 else ""
        self.arguments = args[1:] if len(args) > 1 else [DSRCmd.default]

    def get_command(self):
        return self.command

    def get_arguments(self):
        return self.arguments


class DSRCmd:

    com_prefix = "do"
    help_prefix = "help"
    default = "default"
    prompt_prefix = "~ "

    def __init__(self, debug=False):
        self._debug = debug
        self.completer = None
        self.history = InMemoryHistory()

    @staticmethod
    def get_method_name(prefix: str, name: str):
        return prefix.replace("-", "_") + "_" + name.replace("-", "_")

    def set_nested_completer(self, nest: dict):
        self.completer = NestedCompleter.from_nested_dict(nest)

    def cmd_loop(self):
        while True:
            try:
                user_inp = prompt(
                    DSRCmd.prompt_prefix,
                    completer=self.completer,
                    history=self.history,
                    enable_history_search=True
                )
                parser = CmdParser(user_inp)
                self.execute_command(
                    command=parser.get_command(),
                    arguments=parser.get_arguments()
                )
            except KeyboardInterrupt:
                if self._debug:
                    print(Fore.RED + format_exc() + Fore.RESET)

    def execute_command(self, command, arguments):
        try:
            getattr(
                self, DSRCmd.get_method_name(
                    prefix=DSRCmd.com_prefix,
                    name=command if command.strip() else DSRCmd.default
                )
            )(arguments)
        except AttributeError as e:
            print(Fore.RED + (format_exc() if self._debug else "%s in '%s' — %s" % (
                type(e).__name__, _getframe().f_code.co_name, e)) + Fore.RESET)

    def do_help(self, args):
        if args[0] != DSRCmd.default:
            try:
                getattr(self, DSRCmd.get_method_name(prefix=DSRCmd.help_prefix, name=args[0]))()
            except AttributeError as e:
                print(Fore.RED + (format_exc() if self._debug else "%s in '%s' — %s" % (
                    type(e).__name__, _getframe().f_code.co_name, e)) + Fore.RESET)
        else:
            prefix = DSRCmd.get_method_name(prefix=DSRCmd.com_prefix, name="")
            prefix_len = len(prefix)
            commands = []
            for name in dir(self.__class__):
                if name[:prefix_len] == prefix:
                    com_name = name[prefix_len:]
                    if com_name != DSRCmd.default:
                        commands.append(com_name.replace("_", "-"))
            commands.sort()
            print(Fore.LIGHTYELLOW_EX)
            for command in commands:
                print("\t%s" % command)
            print(Fore.RESET)

    def do_default(self, args):
        if self._debug:
            print(Fore.BLUE + "time for crab" + Fore.RESET)
