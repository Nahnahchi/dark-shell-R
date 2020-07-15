from sys import argv, _getframe
from os import _exit, system
from threading import Thread, Event
from dslib.manager import DarkSouls
from dslib.process import wait_for
from dslib.cmd import DSRCmd
from dslib.gui import DSRPositionGUI, DSRGraphicsGUI
from dsobj.item import DSRItem
from dsres.resources import read_mod_items
from dsres.commands import DSR_NEST, nest_add
from colorama import Fore, init
from traceback import format_exc
from _version import __version__, check_for_updates, MetaInfoError
from prompt_toolkit.shortcuts import set_title

_DEBUG = False
_FLAGS = {
    "help": ("-h", "--help"),
    "debug": ("-d", "--debug")
}


class DarkShell(DSRCmd):

    def __init__(self):
        super(DarkShell, self).__init__(_DEBUG)
        sync_evt = Event()
        nest_add([DSRItem(item.strip(), -1).get_name() for item in read_mod_items()])
        self.set_nested_completer(DSR_NEST)
        self.game_man = DarkSouls(_DEBUG)
        self.get_frame = lambda: _getframe().f_code.co_name
        Thread(target=self._execute_static_commands, args=(sync_evt,)).start()
        Thread(target=self._execute_waiting_commands, args=(sync_evt,)).start()
        Thread(target=self.game_man.load_saved_func, args=(sync_evt,)).start()

    def _execute_static_commands(self, sync_execute: Event):
        sync_execute.wait()
        while True:
            wait_for(self.game_man.can_read)
            static_commands = DarkSouls.STATIC_FUNC.copy()
            for func in static_commands.keys():
                try:
                    self.game_man.switch(command=func[0], arguments=static_commands[func])
                except Exception as e:
                    print(Fore.RED + (format_exc() if _DEBUG else "%s in '%s' — %s" % (
                        type(e).__name__, self.get_frame(), e)) + Fore.RESET)
            wait_for(self.game_man.can_read, desired_state=False)

    def _execute_waiting_commands(self, sync_execute: Event):
        sync_execute.wait()
        waiting_commands = DarkSouls.WAITING_FUNC.copy()
        for evt_hash in waiting_commands:
            try:
                entry = waiting_commands[evt_hash]
                event = Event()
                flag_id = entry["val"][0]
                flag_state = entry["val"][1]
                command = entry["arg"][0]
                args = entry["arg"][1:]
                Thread(target=self.game_man.start_listen, args=(evt_hash, flag_id, flag_state, event)).start()
                Thread(target=self._delay_command, args=(command, args, event)).start()
            except Exception as e:
                print(Fore.RED + (format_exc() if _DEBUG else "%s in '%s' — %s" % (
                    type(e).__name__, self.get_frame(), e)) + Fore.RESET)

    def _delay_command(self, command: str, args: list, evt: Event):
        evt.wait()
        self.execute_command(command, args)

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
    def help_pos_gui():
        pass

    @staticmethod
    def help_meta():
        print(Fore.LIGHTBLUE_EX + "\nUsage:" + Fore.LIGHTYELLOW_EX + "\tmeta [option [option]]")
        print(Fore.LIGHTBLUE_EX + "\nOptions:" + Fore.LIGHTYELLOW_EX)
        for com in DSR_NEST["meta"].keys():
            if DSR_NEST["meta"][com] is not None:
                opts = " [ "
                for opt in DSR_NEST["meta"][com].keys():
                    opts += opt + " "
                com += opts + "]"
            print("\t%s" % com)
        print(Fore.RESET)

    def do_meta(self, args):
        try:
            self.game_man.switch(command="meta", arguments=args)
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s in '%s' — %s" % (
                type(e).__name__, self.get_frame(), e)) + Fore.RESET)

    @staticmethod
    def help_on_flag():
        print(Fore.LIGHTBLUE_EX + "\nUsage:" + Fore.LIGHTYELLOW_EX + "\ton-flag [option [option]]")
        print(Fore.LIGHTBLUE_EX + "\nOptions:" + Fore.LIGHTYELLOW_EX)
        for opt in DSR_NEST["on-flag"].keys():
            print("\t%s" % opt)
        print(Fore.RESET)

    def do_on_flag(self, args):
        try:
            wait_evt = Event()
            self.game_man.switch(command="on-flag", arguments=["notify", wait_evt])
            Thread(target=self._delay_command, args=(args[0], args[1:], wait_evt)).start()
            DarkSouls.WAITING_FUNC[hash(wait_evt)].update({"arg": args})
            self.game_man.save_func()
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s in '%s' — %s" % (
                type(e).__name__, self.get_frame(), e)) + Fore.RESET)

    def do_pos_gui(self, args):
        try:
            DSRPositionGUI(process=self.game_man).mainloop()
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s in '%s' — %s" % (
                type(e).__name__, self.get_frame(), e)) + Fore.RESET)

    @staticmethod
    def help_graphics_gui():
        pass

    def do_graphics_gui(self, args):
        try:
            DSRGraphicsGUI(process=self.game_man).mainloop()
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s in '%s' — %s" % (
                type(e).__name__, self.get_frame(), e)) + Fore.RESET)

    @staticmethod
    def help_set():
        print(Fore.LIGHTBLUE_EX + "\nUsage:" + Fore.LIGHTYELLOW_EX + "\tset [option] [value]")
        print(Fore.LIGHTBLUE_EX + "\nOptions:" + Fore.LIGHTYELLOW_EX)
        for opt in DSR_NEST["set"].keys():
            print("\t%s" % opt)
        print(Fore.RESET)

    def do_set(self, args):
        try:
            self.game_man.switch(command="set", arguments=args)
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s in '%s' — %s" % (
                type(e).__name__, self.get_frame(), e)) + Fore.RESET)

    @staticmethod
    def help_enable():
        print(Fore.LIGHTBLUE_EX + "\nUsage:" + Fore.LIGHTYELLOW_EX + "\tenable [option/flag-id]")
        print(Fore.LIGHTBLUE_EX + "\nOptions:" + Fore.LIGHTYELLOW_EX)
        for opt in DSR_NEST["enable"].keys():
            print("\t%s" % opt)
        print(Fore.RESET)

    def do_enable(self, args):
        try:
            self.game_man.switch(command="enable", arguments=args + [True])
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s in '%s' — %s" % (
                type(e).__name__, self.get_frame(), e)) + Fore.RESET)

    @staticmethod
    def help_disable():
        print(Fore.LIGHTBLUE_EX + "\nUsage:" + Fore.LIGHTYELLOW_EX + "\tdisable [option/flag-id]")
        print(Fore.LIGHTBLUE_EX + "\nOptions:" + Fore.LIGHTYELLOW_EX)
        for opt in DSR_NEST["disable"].keys():
            print("\t%s" % opt)
        print(Fore.RESET)

    def do_disable(self, args):
        try:
            self.game_man.switch(command="enable", arguments=args + [False])
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s in '%s' — %s" % (
                type(e).__name__, self.get_frame(), e)) + Fore.RESET)

    @staticmethod
    def help_get():
        print(Fore.LIGHTBLUE_EX + "\nUsage:" + Fore.LIGHTYELLOW_EX + "\tget [option/flag-id]")
        print(Fore.LIGHTBLUE_EX + "\nOptions:" + Fore.LIGHTYELLOW_EX)
        for opt in DSR_NEST["get"].keys():
            print("\t%s" % opt)
        print(Fore.RESET)

    def do_get(self, args):
        try:
            self.game_man.switch(command="get", arguments=args)
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s in '%s' — %s" % (
                type(e).__name__, self.get_frame(), e)) + Fore.RESET)

    @staticmethod
    def help_game_restart():
        pass

    def do_game_restart(self, args):
        try:
            if self.game_man.game_restart():
                print(Fore.GREEN + "Game restarted" + Fore.RESET)
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s in '%s' — %s" % (
                type(e).__name__, self.get_frame(), e)) + Fore.RESET)

    @staticmethod
    def help_force_menu():
        pass

    def do_force_menu(self, args):
        self.game_man.menu_kick()

    @staticmethod
    def help_item_get():
        print(Fore.LIGHTBLUE_EX + "\nUsage:" + Fore.LIGHTYELLOW_EX + "\titem-get [item-name [count]]\n")
        print("\titem-get [category-name] [item-ID] [count]\n" + Fore.RESET)

    def do_item_get(self, args):
        try:
            if args[0] in DarkSouls.ITEM_CATEGORIES:
                DarkSouls.create_custom_item(args, func=self.game_man.item_get)
                return
            i_name, i_count = DarkSouls.get_item_name_and_count(args)
            if i_count > 0:
                self.game_man.create_item(i_name, i_count, func=self.game_man.item_get)
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s in '%s' — %s" % (
                type(e).__name__, self.get_frame(), e)) + Fore.RESET)

    @staticmethod
    def help_item_mod():
        print(Fore.LIGHTBLUE_EX + "\nUsage:" + Fore.LIGHTYELLOW_EX + "\titem-mod add\n")
        print("\titem-mod remove [item-name]\n")
        print("\titem-mod list\n")
        print("\titem-mod clear\n" + Fore.RESET)

    def do_item_mod(self, args):
        try:
            if DarkSouls.update_items(args):
                self.set_nested_completer(DSR_NEST)
                Thread(target=self.game_man.read_items).start()
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s in '%s' — %s" % (
                type(e).__name__, self.get_frame(), e)) + Fore.RESET)

    @staticmethod
    def help_item_get_upgrade():
        print(Fore.LIGHTBLUE_EX + "\nUsage:" + Fore.LIGHTYELLOW_EX + "\titem-get-upgrade [item-name]\n" + Fore.RESET)

    def do_item_get_upgrade(self, args):
        try:
            i_name, i_count = DarkSouls.get_item_name_and_count(args)
            if i_count > 0:
                self.game_man.upgrade_item(i_name, i_count)
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s in '%s' — %s" % (
                type(e).__name__, self.get_frame(), e)) + Fore.RESET)

    @staticmethod
    def help_warp():
        print(Fore.LIGHTBLUE_EX + "\nUsage:" + Fore.LIGHTYELLOW_EX + "\twarp [area-name [bonfire-name]]")
        print(Fore.LIGHTBLUE_EX + "\nOptions:" + Fore.LIGHTYELLOW_EX)
        for opt in DSR_NEST["warp"].keys():
            if DSR_NEST["warp"][opt] is not None:
                places = " [ "
                for place in DSR_NEST["warp"][opt].keys():
                    places += place + " "
                opt += places + "]"
            print("\t%s" % opt)
        print(Fore.RESET)

    def do_warp(self, args):
        try:
            if args[0] == "bonfire":
                self.game_man.bonfire_warp()
            else:
                b_name = " ".join(args[0:])
                self.game_man.bonfire_warp_by_name(b_name)
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s in '%s' — %s" % (
                type(e).__name__, self.get_frame(), e)) + Fore.RESET)

    @staticmethod
    def help_notify():
        print(Fore.LIGHTBLUE_EX + "\nUsage:" + Fore.LIGHTYELLOW_EX + "\tnotify [banner-name]")
        print(Fore.LIGHTBLUE_EX + "\nOptions:" + Fore.LIGHTYELLOW_EX)
        for opt in DSR_NEST["notify"].keys():
            print("\t%s" % opt)
        print(Fore.RESET)

    def do_notify(self, args):
        try:
            banner = self.game_man.banners[args[0]] if args[0] != "default" else 12
            self.game_man.display_banner(banner)
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s in '%s' — %s" % (
                type(e).__name__, self.get_frame(), e)) + Fore.RESET)

    @staticmethod
    def help_unlock_all_gestures():
        pass

    def do_unlock_all_gestures(self, args):
        try:
            raise NotImplementedError("This option not yet available")
            if self.game_man.unlock_all_gestures():
                print("All gestures unlocked")
        except Exception as e:
            print(Fore.RED + (format_exc() if _DEBUG else "%s in '%s' — %s" % (
                type(e).__name__, self.get_frame(), e)) + Fore.RESET)


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
            print(Fore.LIGHTBLUE_EX + "Available options:" + Fore.LIGHTYELLOW_EX)
            for f in _FLAGS.values():
                print("\t%s" % str(f))
            exit()
    print(Fore.LIGHTYELLOW_EX + "Loading..." + Fore.RESET)
    if not _DEBUG:
        DarkSouls.warn_anti_cheat()
        DarkShell.do_clear(args=[])
    set_title("DarkShell-R")
    try:
        if _DEBUG:
            raise MetaInfoError(reason="Skipping the update check", message="Debug State")
        is_latest, version = check_for_updates()
    except MetaInfoError as e:
        if _DEBUG:
            print(Fore.LIGHTYELLOW_EX + str(e) + Fore.RESET)
        is_latest, version = True, __version__
    print(Fore.LIGHTBLUE_EX + "Welcome to DarkShell %s%s" % (
        "v" + __version__, (" (v%s is available)" % version) if not is_latest else "" + Fore.RESET
    ))
    try:
        DarkShell().cmd_loop()
    except Exception as ex:
        print(Fore.RED + (format_exc() if _DEBUG else "FATAL | %s: %s" % (type(ex).__name__, ex)) + Fore.RESET)
        input()
        _exit(1)
