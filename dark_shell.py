import clr
import sys
from sys import argv
from os import _exit, system
from os.path import dirname, realpath, join
from time import sleep
from threading import Thread
from game_wrapper import DarkSouls
from dslib.ds_cmprocessor import DSRCmp
from dslib.ds_gui import DSRPositionGUI, DSRGraphicsGUI
from dsres.ds_commands import DS_NEST, DS_STATIC
dir_path = dirname(realpath(__file__))
sys.path.append(join(dir_path, "dsprh"))
clr.AddReference("GameHook")
# noinspection PyUnresolvedReferences
from DarkShellRemastered import DSRHook


class DarkShell(DSRCmp):

    def __init__(self, hook: DSRHook, script=None):
        super(DarkShell, self).__init__()
        self.game = DarkSouls(hook)
        self.set_nested_completer(DS_NEST)
        self.execute_source(script)
        if script is None:
            open(self.game.STATIC_SOURCE, "a")
            Thread(target=self.execute_static_commands).start()

    def execute_static_commands(self):
        execute = True
        sleep(5)
        while True:
            if execute:
                if self.game.can_read():
                    self.execute_source(self.game.STATIC_SOURCE)
                    execute = False
                else:
                    sleep(1)
                    continue
            if not self.game.can_read():
                execute = True
            sleep(1)

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

    def do_begin(self, args):
        pass

    @staticmethod
    def help_static():
        print("\nUsage:\t",
              "static [command [args]]\n\t",
              "static list\n\t",
              "static clean\n\t",
              "static remove [line-num]")
        print("\nOptions:")
        for opt in DS_STATIC.keys():
            print("\t%s" % opt)
        print("\n")

    def do_static(self, args):
        try:
            if args[0] in DS_STATIC.keys():
                self.game.switch(command="static", arguments=args)
            else:
                if args[0] not in DS_NEST.keys():
                    print("Unrecognized command: %s" % args[0])
                else:
                    print("Command '%s' can't be static!" % args[0])
        except FileNotFoundError:
            pass

    def do_pos_gui(self, args):
        try:
            DSRPositionGUI(process=self.game).mainloop()
        except Exception as e:
            print("%s: %s\nCouldn't launch position GUI" % (type(e).__name__, e))

    def do_graphics_gui(self, args):
        try:
            DSRGraphicsGUI(process=self.game).mainloop()
        except Exception as e:
            print("%s: %s\nCouldn't launch graphics GUI" % (type(e).__name__, e))

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
        print("\titem-get [category-name] [item-ID] [count]\n")

    def do_item_get(self, args):
        try:
            if args[0] in DarkSouls.ITEM_CATEGORIES:
                self.game.create_custom_item(DarkSouls.ITEM_CATEGORIES[args[0]], args[1], args[2])
                return
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
    DarkSouls.warn_anticheat()
    source = argv[1] if len(argv) > 1 else None
    if source is None:
        print("Welcome to Dark Shell")
    DarkShell(hook=DSRHook(5000, 5000), script=source).cmp_loop()
