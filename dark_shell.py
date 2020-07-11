from sys import argv
from os import _exit, system
from threading import Thread
from dslib.ds_wrapper import DarkSouls
from dslib.ds_cmd import DSRCmd
from dslib.ds_gui import DSRPositionGUI, DSRGraphicsGUI
from dsobj.ds_item import DSRItem
from dsres.ds_resources import read_mod_items
from dsres.ds_commands import DS_NEST, nest_add
from colorama import Fore, init
from traceback import format_exc
from _version import __version__, check_for_updates, CheckUpdatesError
from prompt_toolkit.shortcuts import set_title

_DEBUG = False
_FLAGS = {
    "help": ("-h", "--help"),
    "debug": ("-d", "--debug")
}


class DarkShell(DSRCmd):

    def __init__(self):
        super(DarkShell, self).__init__(_DEBUG)
        nest_add([DSRItem(item.strip(), -1).get_name() for item in read_mod_items()])
        self.set_nested_completer(DS_NEST)
        self.game = DarkSouls(_DEBUG)
        Thread(target=self._execute_static_commands).start()

    def _execute_static_commands(self):
        execute = True
        while True:
            if execute and self.game.is_hooked():
                if not self.game.can_read():
                    continue
                else:
                    static_commands = DarkSouls.STATIC_FUNC.copy()
                    for func in static_commands.keys():
                        try:
                            self.game.switch(command=func[0], arguments=static_commands[func])
                        except Exception as e:
                            print(Fore.RED + (format_exc() if _DEBUG else "%s: %s" %
                                                                          (type(e).__name__, e)) + Fore.RESET)
                            continue
                    execute = False
            if not self.game.can_read():
                execute = True

    @staticmethod
    def help_clear():
        pass

    @staticmethod
    def do_clear(args):
        system("cls")

    @staticmethod
    def help_exit():
        pass

    @staticmethod
    def do_exit(args):
        _exit(0)

    @staticmethod
    def help_quit():
        pass

    @staticmethod
    def do_quit(args):
        _exit(0)

    @staticmethod
    def help_end():
        pass

    @staticmethod
    def do_end(args):
        _exit(0)

    @staticmethod
    def help_pos_gui():
        pass

    def do_pos_gui(self, args):
        try:
            DSRPositionGUI(process=self.game).mainloop()
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s: %s" % (type(e).__name__, e)) + Fore.RESET)

    @staticmethod
    def help_graphics_gui():
        pass

    def do_graphics_gui(self, args):
        try:
            DSRGraphicsGUI(process=self.game).mainloop()
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s: %s" % (type(e).__name__, e)) + Fore.RESET)

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
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s: %s" % (type(e).__name__, e)) + Fore.RESET)

    @staticmethod
    def help_enable():
        print("\nUsage:\tenable [option/flag-id]")
        print("\nOptions:")
        for opt in DS_NEST["enable"].keys():
            print("\t%s" % opt)
        print("\n")

    def do_enable(self, args):
        try:
            self.game.switch(command="enable", arguments=args + [True])
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s: %s" % (type(e).__name__, e)) + Fore.RESET)

    @staticmethod
    def help_disable():
        print("\nUsage:\tdisable [option/flag-id]")
        print("\nOptions:")
        for opt in DS_NEST["disable"].keys():
            print("\t%s" % opt)
        print("\n")

    def do_disable(self, args):
        try:
            self.game.switch(command="enable", arguments=args + [False])
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s: %s" % (type(e).__name__, e)) + Fore.RESET)

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
            print(Fore.RED + (format_exc() if _DEBUG else "%s: %s" % (type(e).__name__, e)) + Fore.RESET)

    @staticmethod
    def help_game_restart():
        pass

    def do_game_restart(self, args):
        try:
            raise NotImplementedError("This option not yet available")
            if self.game.game_restart():
                print("Game restarted")
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s: %s" % (type(e).__name__, e)) + Fore.RESET)

    @staticmethod
    def help_menu_kick():
        pass

    def do_menu_kick(self, args):
        self.game.menu_kick()

    @staticmethod
    def help_item_get():
        print("\nUsage:\titem-get [item-name [count]]\n")
        print("\titem-get [category-name] [item-ID] [count]\n")

    def do_item_get(self, args):
        try:
            if len(args) > 0 and args[0] in DarkSouls.ITEM_CATEGORIES:
                DarkSouls.create_custom_item(args, func=self.game.item_get)
                return
            i_name, i_count = DarkSouls.get_item_name_and_count(args)
            if i_count > 0:
                self.game.create_item(i_name, i_count, func=self.game.item_get)
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s: %s" % (type(e).__name__, e)) + Fore.RESET)

    @staticmethod
    def help_item_mod():
        print("\nUsage:\titem-mod add\n")
        print("\titem-mod remove [item-name]\n")
        print("\titem-mod list\n")
        print("\titem-mod clear\n")

    def do_item_mod(self, args):
        try:
            if DarkSouls.add_new_item(args):
                self.set_nested_completer(DS_NEST)
                Thread(target=self.game.read_items).start()
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s: %s" % (type(e).__name__, e)) + Fore.RESET)

    @staticmethod
    def help_item_get_upgrade():
        print("\nUsage:\titem-get-upgrade [item-name]\n")

    def do_item_get_upgrade(self, args):
        try:
            i_name, i_count = DarkSouls.get_item_name_and_count(args)
            if i_count > 0:
                self.game.upgrade_item(i_name, i_count)
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s: %s" % (type(e).__name__, e)) + Fore.RESET)

    @staticmethod
    def help_warp():
        print("\nUsage:\twarp [area-name [bonfire-name]]")
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
            if len(args) == 0:
                DarkSouls.raise_warp_error("")
            if args[0] == "bonfire":
                self.game.bonfire_warp()
            else:
                b_name = " ".join(args[0:])
                self.game.bonfire_warp_by_name(b_name)
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s: %s" % (type(e).__name__, e)) + Fore.RESET)

    @staticmethod
    def help_unlock_all_gestures():
        pass

    def do_unlock_all_gestures(self, args):
        try:
            raise NotImplementedError("This option not yet available")
            if self.game.unlock_all_gestures():
                print("All gestures unlocked")
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s: %s" % (type(e).__name__, e)) + Fore.RESET)


def has_flag(key: str):
    for arg in argv:
        if arg in _FLAGS[key]:
            return True
    return False


if __name__ == "__main__":
    init()
    if len(argv) > 1:
        if has_flag("debug"):
            _DEBUG = True
        if has_flag("help"):
            print(Fore.LIGHTYELLOW_EX + "Available options:")
            for f in _FLAGS.values():
                print("\t%s" % str(f))
            exit()
    print(Fore.LIGHTYELLOW_EX + "Loading..." + Fore.RESET)
    set_title("DarkShell-R")
    try:
        is_latest, version = check_for_updates()
        DarkShell.do_clear(args=[])
    except CheckUpdatesError:
        if _DEBUG:
            print(Fore.RED + format_exc() + Fore.RESET)
        is_latest, version = True, __version__
    print(Fore.LIGHTBLUE_EX + "Welcome to DarkShell-R %s%s" % (
        "v" + __version__, (" (v%s is available)" % version) if not is_latest else "" + Fore.RESET
    ))
    try:
        DarkShell().cmd_loop()
    except Exception as ex:
        print(Fore.RED + (format_exc() if _DEBUG else "[FATAL] %s: %s" % (type(ex).__name__, ex)) + Fore.RESET)
        input()
