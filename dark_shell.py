import clr
import sys
from sys import argv
from os import _exit, system
from os.path import dirname, realpath, join
from game_wrapper import DarkSouls
from dslib.ds_cmprocessor import DSRCmp
from dsres.ds_commands import DS_NEST
dir_path = dirname(realpath(__file__))
sys.path.append(join(dir_path, "dsprh"))
clr.AddReference("DSRInterface")
# noinspection PyUnresolvedReferences
from DSRInterface import DSRHook


class DarkShell(DSRCmp):

    def __init__(self, hook: DSRHook, script=None):
        super(DarkShell, self).__init__()
        self.game = DarkSouls(hook)
        self.set_nested_completer(DS_NEST)
        self.execute_source(script)

    @staticmethod
    def do_clear(args):
        system("cls")

    @staticmethod
    def do_exit(args):
        _exit(0)

    @staticmethod
    def do_quit(args):
        _exit(0)

    @staticmethod
    def do_end(args):
        _exit(0)

    @staticmethod
    def do_begin(args):
        pass

    @staticmethod
    def help_set():
        print("\nUsage:\tset [option] [value]")
        print("\nOptions:")
        for opt in DS_NEST["set"].keys():
            print("\t%s" % opt)
        print("\n")

    def do_set(self, args):
        try:
            self.game.switch(command="set", arguments=args)
        except ValueError:
            print("Wrong parameter type: %s " % args[1])
        except Exception as e:
            print("%s: %s\nCouldn't complete the command" % (type(e).__name__, e))

    @staticmethod
    def help_get():
        print("\nUsage:\tget [option/flag-id]")
        print("\nOptions:")
        for opt in DS_NEST["get"].keys():
            print("\t%s" % opt)
        print("\n")

    def do_get(self, args):
        try:
            self.game.switch(command="get", arguments=args)
        except Exception as e:
            print("%s: %s\nCouldn't complete the command" % (type(e).__name__, e))

    @staticmethod
    def help_enable():
        print("\nUsage:\tenable [option/flag-id]")
        print("\nOptions:")
        for opt in DS_NEST["enable"].keys():
            print("\t%s" % opt)
        print("\n")

    def do_enable(self, args):
        try:
            self.game.switch(command="enable", arguments=args+[True])
        except Exception as e:
            print("%s: %s\nCouldn't complete the command" % (type(e).__name__, e))

    @staticmethod
    def help_disable():
        print("\nUsage:\tdisable [option/flag-id]")
        print("\nOptions:")
        for opt in DS_NEST["disable"].keys():
            print("\t%s" % opt)
        print("\n")

    def do_disable(self, args):
        try:
            self.game.switch(command="enable", arguments=args+[False])
        except Exception as e:
            print("%s: %s\nCouldn't complete the command" % (type(e).__name__, e))

    @staticmethod
    def help_item_get():
        print("\nUsage:\titem-get [item-name [count]]\n")

    def do_item_get(self, args):
        try:
            i_name, i_count = DarkSouls.get_item_name_and_count(args)
            if i_count > 0:
                self.game.create_item(i_name, i_count, func=self.game.item_get)
        except Exception as e:
            print("%s: %s\nCouldn't complete the command" % (type(e).__name__, e))

    @staticmethod
    def help_item_get_upgrade():
        print("\nUsage:\titem-get-upgrade [item-name]\n")

    def do_item_get_upgrade(self, args):
        try:
            i_name, i_count = DarkSouls.get_item_name_and_count(args)
            if i_count > 0:
                self.game.upgrade_item(i_name, i_count)
        except Exception as e:
            print("%s: %s\nCouldn't complete the command" % (type(e).__name__, e))

    @staticmethod
    def help_warp():
        print("\nUsage:\twarp [option [option]]")
        print("\nOptions:")
        for opt in DS_NEST["warp"].keys():
            if DS_NEST["warp"][opt] is not None:
                places = " [ "
                for place in DS_NEST["warp"][opt].keys():
                    places += place + " "
                opt += places + "]"
            print("\t%s" % opt)
        print("\n")

    def do_warp(self, args):
        try:
            if args[0] == "bonfire":
                self.game.bonfire_warp()
            else:
                b_name = " ".join(args[0:])
                self.game.bonfire_warp_by_name(b_name)
        except Exception as e:
            print("%s: %s\nCouldn't complete the command" % (type(e).__name__, e))


if __name__ == "__main__":
    source = argv[1] if len(argv) > 1 else None
    if source is None:
        print("Welcome to Dark Shell R")
    DarkShell(hook=DSRHook(5000, 5000), script=source).cmp_loop()
