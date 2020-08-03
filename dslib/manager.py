# noinspection PyUnresolvedReferences
from dsbin.imports import Stats, Enum, get_clr_type
from dslib.process import DSRProcess
from dslib.cmd import DSRCmd
from dsobj.bonfire import DSRBonfire
from dsobj.item import DSRItem, DSRInfusion, Upgrade
from dsres.resources import SAVE_DIR, play_random_sound
from dsres.commands import nest_add, nest_remove, nest_reset
from prompt_toolkit.shortcuts import set_title, input_dialog, radiolist_dialog, message_dialog, yes_no_dialog
from os.path import join
from sys import _getframe
from time import sleep
from datetime import datetime
from threading import Thread, Event
from collections import defaultdict
from traceback import format_exc
from colorama import Fore
from ctypes import ArgumentError
from pickle import load, dump, UnpicklingError


class DarkSouls(DSRProcess):
    PROCESS_NAME = "DARK SOULS™: REMASTERED"
    STATIC_SOURCE = join(SAVE_DIR, "static.dat")
    WAITING_SOURCE = join(SAVE_DIR, "waiting.dat")
    STATIC_FUNC = {}
    WAITING_FUNC = {}
    ITEM_CATEGORIES = ({
        "weapon": 0x00000000,
        "good": 0x40000000,
        "ring": 0x20000000,
        "armor": 0x10000000
    })

    def __init__(self, debug=False):
        super(DarkSouls, self).__init__(DarkSouls.PROCESS_NAME, debug)
        self._debug = debug
        self.bonfires = defaultdict(DSRBonfire)
        self.items = defaultdict(DSRItem)
        self.infusions = defaultdict(DSRInfusion)
        self.covenants = defaultdict(int)
        self.banners = defaultdict(int)
        self.stats = {stat: 0 for stat in Enum.GetValues(get_clr_type(Stats))}
        Thread(target=self.read_bonfires).start()
        Thread(target=self.read_items).start()
        Thread(target=self.read_infusions).start()
        Thread(target=self.read_covenants).start()
        Thread(target=self.read_banners).start()

    def update_version(self):
        set_title("DarkShell-R — Game Version: %s" % self.get_version())

    @staticmethod
    def warn_anti_cheat():
        message_dialog(
            title="WARNING",
            text="Dark Souls Remastered has an anti-cheat system.\nDo not use this application online!"
        ).run()

    @staticmethod
    def get_name_from_arg(arg: str):
        return arg.replace("-", " ").title()

    @staticmethod
    def update_items(args):
        if len(args) == 0:
            raise ArgumentError("No arguments given!")
        else:
            if args[0] == "clear":
                from dsres.resources import clear_mod_items
                clear_mod_items(DarkSouls.ITEM_CATEGORIES)
                nest_reset()
            elif args[0] == "remove":
                from dsres.resources import remove_mod_item
                try:
                    remove_mod_item(args[1])
                    nest_remove(args[1])
                except IndexError:
                    raise ArgumentError("Item name not specified!")
            elif args[0] == "list":
                from dsres.resources import read_mod_items
                print(Fore.LIGHTBLUE_EX + "\n\tID\t\tName" + Fore.LIGHTYELLOW_EX)
                for item in read_mod_items():
                    item = item.split()
                    if len(item) == 4:
                        print("\t%s\t\t%s" % (item[0], DarkSouls.get_name_from_arg(item[3])))
                print(Fore.RESET)
            elif args[0] == "add":
                from dsres.resources import create_mod_files
                create_mod_files(DarkSouls.ITEM_CATEGORIES)
                category = radiolist_dialog(
                    title="Select item category",
                    text="Category of the new item:",
                    values=[(cat, cat.upper()) for cat in DarkSouls.ITEM_CATEGORIES.keys()]
                ).run()
                if category is None:
                    return False
                item_id = input_dialog(
                    title="Enter item ID",
                    text="Item ID for the new %s:" % category
                ).run()
                if item_id is None or not item_id.strip():
                    return False
                item_name = input_dialog(
                    title="Enter item name",
                    text="Name of the new %s:" % category
                ).run()
                if not item_name.strip():
                    return False
                from dsres.resources import write_mod_item
                formatted_name = "-".join(item_name.lower().split())
                try:
                    if write_mod_item(category, formatted_name, int(item_id)):
                        print(Fore.GREEN + ("%s '%s' (ID: %s) added successfully" % (
                            category.title(), item_name.title(), item_id)) + Fore.RESET)
                        nest_add([formatted_name])
                        return True
                    return False
                except ValueError:
                    raise ArgumentError("Can't convert %s '%s' to int!" % (type(item_id).__name__, item_id))
            else:
                raise ArgumentError("Unknown argument: %s" % args[0])
            return True

    @staticmethod
    def get_item_name_and_count(args: list):
        if len(args) == 0:
            raise ArgumentError("No item name specified!")
        i_name = args[0].lower()
        i_count = 1
        try:
            if len(args) >= 2:
                i_count = int(args[1])
        except ValueError:
            raise ArgumentError("Can't convert %s '%s' to int!" % (type(args[1]).__name__, args[1]))
        return i_name, i_count

    @staticmethod
    def get_upgrade_value_infusable(infusions: list, item: DSRItem):
        infusion = radiolist_dialog(
            title="Select infusion type",
            text="How would you like %s to be upgraded?" % DarkSouls.get_name_from_arg(item.get_name()),
            values=infusions
        ).run()
        if infusion is None:
            return None
        upgrade = input_dialog(
            title="Enter upgrade value",
            text="Item type: Normal [%s]" % infusion.upper()
        ).run()
        try:
            int(upgrade)
        except ValueError:
            raise ArgumentError("Can't convert %s '%s' to int" % (type(upgrade).__name__, upgrade))
        return upgrade, infusion

    @staticmethod
    def get_upgrade_value_pyro_flame(item: DSRItem):
        is_pyro_asc = item.get_upgrade_type() == Upgrade.PYRO_FLAME_ASCENDED
        max_upgrade = 5 if is_pyro_asc else 15
        upgrade = input_dialog(
            title="Enter upgrade value for %s" % DarkSouls.get_name_from_arg(item.get_name()),
            text="Item type: %sPyromancy Flame" % "Ascended " if is_pyro_asc else ""
        ).run()
        try:
            if int(upgrade) > max_upgrade or int(upgrade) < 0:
                print(Fore.RED + ("Can't upgrade %sPyromancy Flame to +%s" % (
                    "Ascended " if is_pyro_asc else "", upgrade)) + Fore.RESET)
                return None
        except ValueError:
            raise ArgumentError("Can't convert %s '%s' to int!" % (type(upgrade).__name__, upgrade))
        return upgrade

    @staticmethod
    def get_upgrade_value_armor_or_unique(item: DSRItem):
        is_unique = item.get_upgrade_type() == Upgrade.UNIQUE
        max_upgrade = 5 if is_unique else 10
        upgrade = input_dialog(
            title="Enter upgrade value for %s" % DarkSouls.get_name_from_arg(item.get_name()),
            text="Item type: %s" % "Unique" if is_unique else "Armor"
        ).run()
        try:
            if int(upgrade) > max_upgrade or int(upgrade) < 0:
                print(Fore.RED + ("Can't upgrade %s to +%s" % (
                    "Unique" if is_unique else "Armor", upgrade)) + Fore.RESET)
                return None
        except ValueError:
            raise ArgumentError("Can't convert %s '%s' to int!" % (type(upgrade).__name__, upgrade))
        return upgrade

    @staticmethod
    def warn_disable_npc():
        return yes_no_dialog(
            title="Warning",
            text="This command will kill all NPCs in the area. Do you want to proceed?"
        ).run()

    def print_status(self):
        print(Fore.LIGHTBLUE_EX + "\n\tLevel:" + Fore.LIGHTYELLOW_EX + (" %d" % self.get_stat(Stats.LVL)))
        print(Fore.LIGHTBLUE_EX + "\n\tHealth:" + Fore.RED + (" %d/%d" % (self.get_hp(), self.get_hp_max())))
        print(Fore.LIGHTBLUE_EX + "\tStamina:" + Fore.GREEN + (" %d\n" % self.get_stamina()))
        exclude = (Stats.LVL, Stats.SLS, Stats.HUM)
        for stat in self.stats.keys():
            if stat not in exclude:
                print(Fore.LIGHTBLUE_EX + ("\t%s:" % Enum.GetName(get_clr_type(Stats), stat))
                      + Fore.LIGHTYELLOW_EX + (" %d" % self.get_stat(stat)))
        print(Fore.LIGHTBLUE_EX + "\n\tSouls:" + Fore.LIGHTYELLOW_EX + (" %d" % self.get_stat(Stats.SLS)))
        print(Fore.LIGHTBLUE_EX + "\tHumanity:" + Fore.LIGHTYELLOW_EX + (" %d" % self.get_stat(Stats.HUM)))
        print(Fore.RESET)

    @staticmethod
    def raise_warp_error(b_full_name: str):
        from dsres.commands import DSR_NEST
        if not b_full_name.strip() or b_full_name.lower() == DSRCmd.default:
            raise ArgumentError("No arguments given!")
        area_name = b_full_name.split()[0]
        if area_name not in DSR_NEST["warp"].keys():
            raise ArgumentError("Unknown area name: %s" % DarkSouls.get_name_from_arg(area_name))
        else:
            if len(b_full_name.split()) < 2:
                raise ArgumentError("No bonfire name specified!")
            bonfire_name = b_full_name.split()[1]
            if bonfire_name not in DSR_NEST["warp"][area_name]:
                raise ArgumentError("Unknown bonfire name for area '%s': %s" % (
                    DarkSouls.get_name_from_arg(area_name), bonfire_name
                ))
        raise AssertionError("Error processing arguments: %s | Can't determine the reason of failure" % b_full_name)

    def bonfire_warp_by_name(self, b_full_name: str):
        if b_full_name not in self.bonfires.keys():
            DarkSouls.raise_warp_error(b_full_name)
        else:
            b_id = self.bonfires[b_full_name].get_id()
            self.set_bonfire(b_id)
            self.bonfire_warp()
            print(Fore.GREEN + ("Warped to location ID: %d" % b_id) + Fore.RESET)

    def level_stat(self, s_name: str, s_level: int):
        raise NotImplementedError("Function unavailable")
        for stat in self.stats.keys():
            if stat.value != s_name:
                if stat != Stats.LVL:
                    self.stats[stat] = self.get_stat(stat)
            else:
                new_stat = s_level
                cur_stat = self.get_stat(stat)
                soul_level = self.get_stat(Stats.LVL) + (new_stat - cur_stat)
                self.stats[stat] = new_stat
                self.stats[Stats.LVL] = soul_level
        return self.level_up(self.stats)

    def create_item(self, i_name: str, i_count: int, func):
        if i_name not in self.items.keys():
            raise ArgumentError("Item '%s' doesn't exist!" % DarkSouls.get_name_from_arg(i_name))
        else:
            item = self.items[i_name]
            i_id = item.get_id()
            i_cat = item.get_category()
            func(i_cat, i_id, i_count)
            print(Fore.GREEN + ("Created new item, ID: %d" % i_id) + Fore.RESET)

    @staticmethod
    def create_custom_item(args: list, func):
        try:
            i_cat, i_id, i_count = DarkSouls.ITEM_CATEGORIES[args[0]], args[1], args[2]
            func(i_cat, i_id, i_count)
            print(Fore.GREEN + ("Created new item, ID: %s" % i_id) + Fore.RESET)
        except IndexError:
            raise ArgumentError("No item ID/count specified!")

    def upgrade_item(self, i_name: str, i_count: int):
        if i_name not in self.items.keys():
            raise ArgumentError("Item '%s' doesn't exist!" % DarkSouls.get_name_from_arg(i_name))
        else:
            item = self.items[i_name]
            i_id = item.get_id()
            i_category = item.get_category()
            if item.get_upgrade_type() == Upgrade.NONE:
                print(Fore.RED + "Can't upgrade this item!" + Fore.RESET)
                return
            elif item.get_upgrade_type() in (Upgrade.ARMOR, Upgrade.UNIQUE):
                upgrade = DarkSouls.get_upgrade_value_armor_or_unique(item)
                if upgrade is None:
                    return
                i_id += int(upgrade)
            elif item.get_upgrade_type() in (Upgrade.PYRO_FLAME, Upgrade.PYRO_FLAME_ASCENDED):
                upgrade = DarkSouls.get_upgrade_value_pyro_flame(item)
                if upgrade is None:
                    return
                i_id += int(upgrade) * 100
            elif item.get_upgrade_type() in (Upgrade.INFUSABLE, Upgrade.INFUSABLE_RESTRICTED):
                values = [
                    (self.infusions[key].get_name(), self.infusions[key].get_name().upper())
                    for key in self.infusions.keys()
                ]
                upgrade, infusion = DarkSouls.get_upgrade_value_infusable(values, item)
                if upgrade is None:
                    return
                i_id = self.infusions[infusion].infuse(item, int(upgrade))
            else:
                raise AssertionError(
                    "Can't determine the upgrade type for item '%s'!" % DarkSouls.get_name_from_arg(i_name)
                )
            if i_id >= item.get_id():
                self.item_get(i_category, i_id, i_count)
                print(Fore.GREEN + "Upgrade successful" + Fore.RESET)

    @staticmethod
    def ask_flag():
        flag_id = input_dialog(
            title="Enter a flag ID",
            text="Event flag to listen to:"
        ).run()
        if flag_id is None or not flag_id.strip():
            raise ArgumentError("No flag ID specified!")
        if not flag_id.isnumeric():
            raise ArgumentError("Can't convert %s '%s' to int!" % (type(flag_id).__name__, flag_id))
        state = radiolist_dialog(
            title="Select flag state",
            text="Desired state of event flag %s" % flag_id,
            values=[
                (True, "ON"),
                (False, "OFF")
            ]
        ).run()
        if state is None:
            raise ArgumentError("No state specified!")
        return int(flag_id), state

    def start_listen(self, pid: int, flag_id: int, state: bool, e: Event):
        try:
            self.listen_for_flag(flag_id, flag_state=state)
            if pid in DarkSouls.WAITING_FUNC.keys():
                now = datetime.now().strftime("%H:%M:%S")
                print(Fore.LIGHTYELLOW_EX + ("[%s] " % now) + Fore.LIGHTCYAN_EX + "Event flag" +
                      Fore.LIGHTYELLOW_EX + (" %d " % flag_id) + Fore.LIGHTCYAN_EX + "is" +
                      (Fore.GREEN if state else Fore.RED) + (" %s" % ("ON" if state else "OFF")) + Fore.RESET)
                e.set()
                play_random_sound()
        except Exception as e:
            print(Fore.RED + (format_exc() if self._debug else "%s in '%s' — %s" % (
                type(e).__name__, _getframe().f_code.co_name, e)) + Fore.RESET)
        finally:
            DarkSouls.update_waiting_func(key=pid, to_del=True)

    def read_performed_animations(self):
        print(Fore.LIGHTBLUE_EX + "\n\tTime\t\tID" + Fore.RESET)
        last_anim_id = 0
        while True:
            curr_anim_id = self.get_last_animation()
            curr_time = datetime.now().strftime("%H:%M:%S")
            if curr_anim_id not in (-1, last_anim_id):
                print(Fore.LIGHTYELLOW_EX + "\t" + curr_time + "\t" + str(curr_anim_id) + Fore.RESET)
                last_anim_id = curr_anim_id
            sleep(0.016)

    def read_bonfires(self):
        from dsres.resources import get_bonfires
        bonfires = get_bonfires()
        for b in bonfires:
            try:
                bonfire = DSRBonfire(b.strip())
                self.bonfires[bonfire.get_name()] = bonfire
            except Exception as e:
                print(Fore.RED + (format_exc() if self._debug else
                                  "%s: Error reading bonfire: %s | %s" %
                                  (type(e).__name__, b.split(), e)) + Fore.RESET)

    def read_items(self):
        from dsres.resources import get_item_files, get_items, get_mod_item_files, get_mod_items
        for func in (get_item_files, get_items), (get_mod_item_files, get_mod_items):
            item_files = func[0]()
            for file in item_files:
                items = func[1](file)
                category = items[0] if len(items) > 0 else None
                for i in items[1:]:
                    try:
                        if i.strip():
                            item = DSRItem(i.strip(), int(category, 16))
                            self.items[item.get_name()] = item
                    except ValueError as e:
                        print(Fore.RED + (format_exc() if self._debug else
                                          "%s: Error reading item category in file '%s' | %s" %
                                          (type(e).__name__, file, e)) + Fore.RESET)
                        break
                    except Exception as e:
                        print(Fore.RED + (format_exc() if self._debug else
                                          "%s: Error reading item: %s | %s" %
                                          (type(e).__name__, i.title().split(), e)) + Fore.RESET)
                        continue

    def read_infusions(self):
        from dsres.resources import get_infusions
        infusions = get_infusions()
        for i in infusions:
            try:
                infusion = DSRInfusion(i.strip())
                self.infusions[infusion.get_name()] = infusion
            except Exception as e:
                print(Fore.RED + (format_exc() if self._debug else
                                  "%s: Error reading infusion: %s | %s" %
                                  (type(e).__name__, i.split(), e)) + Fore.RESET)

    def read_covenants(self):
        from dsres.resources import get_covenants
        covenants = get_covenants()
        for c in covenants:
            try:
                covenant = c.split()
                cov_id = int(covenant[0])
                cov_name = covenant[1]
                self.covenants[cov_name] = cov_id
            except Exception as e:
                print(Fore.RED + (format_exc() if self._debug else
                                  "%s: Error reading covenant: %s | %s" %
                                  (type(e).__name__, c.split(), e)) + Fore.RESET)

    def read_banners(self):
        from dsres.resources import get_banners
        banners = get_banners()
        for b in banners:
            try:
                banner = b.split()
                banner_id = int(banner[0])
                banner_name = banner[1]
                self.banners[banner_name] = banner_id
            except Exception as e:
                print(Fore.RED + (format_exc() if self._debug else
                                  "%s: Error reading banner: %s | %s" %
                                  (type(e).__name__, b.split(), e)) + Fore.RESET)

    @staticmethod
    def clear_saved_func(args):
        if "static" in args:
            DarkSouls.STATIC_FUNC.clear()
        if "waiting" in args:
            DarkSouls.WAITING_FUNC.clear()

    @staticmethod
    def _test(args):
        if "audio" in args:
            play_random_sound()

    @staticmethod
    def manage_thread_info(args):
        if len(args) == 0:
            raise ArgumentError("No option specified!")
        elif args[0] == "clear":
            from dsres.commands import DSR_NEST
            arg = args[1:] if len(args) > 1 else DSR_NEST["meta"]["processes"]["clear"].keys()
            DarkSouls.clear_saved_func(arg)
        elif args[0] == "list":
            if not bool(DarkSouls.STATIC_FUNC):
                print(Fore.LIGHTBLUE_EX + "No commands to re-execute" + Fore.RESET)
            else:
                print(Fore.LIGHTBLUE_EX + "\nTo be re-executed:\n")
                for command in DarkSouls.STATIC_FUNC:
                    print(Fore.LIGHTCYAN_EX + "\t" + command[0] + Fore.LIGHTYELLOW_EX + " " +
                          " ".join([str(arg).lower() for arg in DarkSouls.STATIC_FUNC[command]]))
                print(Fore.RESET)
            if not bool(DarkSouls.WAITING_FUNC):
                print(Fore.LIGHTBLUE_EX + "No commands are waiting for event flags" + Fore.RESET)
            else:
                print(Fore.LIGHTBLUE_EX + "\nWaiting for event flags:\n")
                for evt_hash in DarkSouls.WAITING_FUNC:
                    entry = DarkSouls.WAITING_FUNC[evt_hash]
                    flag_id = entry["val"][0]
                    flag_state = entry["val"][1]
                    command = entry["arg"][0]
                    args = entry["arg"][1:]
                    print(Fore.YELLOW + "\t" + str(flag_id).zfill(8) + " → " +
                          ((Fore.LIGHTGREEN_EX + "ON") if flag_state else (Fore.LIGHTRED_EX + "OFF")) +
                          Fore.LIGHTCYAN_EX + "\t" + command + Fore.LIGHTYELLOW_EX + " " + " ".join(args))
                print(Fore.RESET)

    @staticmethod
    def load_all_func(e: Event):

        def load_static():
            try:
                static_func = load(open(DarkSouls.STATIC_SOURCE, "rb"))
                DarkSouls.STATIC_FUNC.update(static_func)
            except (FileNotFoundError, UnpicklingError, EOFError):
                open(DarkSouls.STATIC_SOURCE, "w+")
                DarkSouls.STATIC_FUNC.clear()

        def load_waiting():
            try:
                waiting_func = load(open(DarkSouls.WAITING_SOURCE, "rb"))
                DarkSouls.WAITING_FUNC.update(waiting_func)
            except (FileNotFoundError, UnpicklingError, EOFError):
                open(DarkSouls.WAITING_SOURCE, "w+")
                DarkSouls.WAITING_FUNC.clear()

        ls = Thread(target=load_static)
        lw = Thread(target=load_waiting)
        ls.start(), lw.start()
        ls.join(), lw.join()
        e.set()

    @staticmethod
    def save_all_func():
        Thread(target=dump, args=(DarkSouls.STATIC_FUNC, open(DarkSouls.STATIC_SOURCE, "wb"))).start()
        Thread(target=dump, args=(DarkSouls.WAITING_FUNC, open(DarkSouls.WAITING_SOURCE, "wb"))).start()

    @staticmethod
    def update_static_func(command: str, args: list, to_add: bool):
        key = (command, args[0])
        if to_add:
            DarkSouls.STATIC_FUNC[key] = args
        else:
            DarkSouls.STATIC_FUNC.pop(key, None)
        DarkSouls.save_all_func()

    @staticmethod
    def update_waiting_func(key: int, val: dict = None, to_del=False):
        assert (not to_del) ^ (val is None)
        if to_del:
            DarkSouls.WAITING_FUNC.pop(key, None)
        else:
            try:
                DarkSouls.WAITING_FUNC[key].update(val)
            except KeyError:
                DarkSouls.WAITING_FUNC[key] = val
        DarkSouls.save_all_func()

    def validate_covenant(self, key: str):
        if key not in self.covenants.keys():
            raise ArgumentError("Covenant '%s' doesn't exist!" % DarkSouls.get_name_from_arg(key))

    def switch(self, command: str, arguments: list):

        dsr = self

        def validate(data, data_type: type):
            try:
                data_type(data)
            except (ValueError, TypeError):
                raise ArgumentError("Unknown argument: %s" % data)

        def convert(data, data_type: type):
            try:
                return data_type(data)
            except ValueError:
                raise ArgumentError("Can't convert %s '%s' to %s!" % (type(data).__name__, data, data_type.__name__))

        class Switcher:

            @classmethod
            def switch(cls):
                case_name = DSRCmd.get_method_name(prefix=command, name=arguments[0])
                default_func = getattr(cls, DSRCmd.get_method_name(prefix=command, name="default"))
                case_method = getattr(cls, case_name, default_func)
                case_method()

            @staticmethod
            def set_default():
                stat_name = arguments[0]
                validate(stat_name, Stats)
                stat_value = int(arguments[1])
                if dsr.set_stat(stat_name, stat_value):
                    print(Fore.GREEN + ("%s set to %d" % (stat_name.upper(), stat_value)) + Fore.RESET)

            @staticmethod
            def get_default():
                flag_id = convert(arguments[0], int)
                print(Fore.LIGHTBLUE_EX + ("FLAG %d:" % flag_id) + Fore.LIGHTYELLOW_EX +
                      (" %s" % (dsr.read_event_flag(flag_id))) + Fore.RESET)

            @staticmethod
            def enable_default():
                validate(arguments[0], int)
                flag_id = convert(arguments[0], int)
                enable = arguments[1]
                dsr.write_event_flag(flag_id, enable)
                print(Fore.GREEN + ("EVENT FLAG %d %s" % (flag_id, ("enabled" if enable else "disabled"))) + Fore.RESET)

            @staticmethod
            def on_flag_default():
                pass

            @staticmethod
            def meta_default():
                import _version
                is_latest, version = _version.check_for_updates()
                if is_latest:
                    print(Fore.GREEN + "Using the latest version" + Fore.RESET)
                else:
                    print(Fore.LIGHTCYAN_EX + "Update available" + Fore.RESET)

            @staticmethod
            def set_speed_self():
                speed = convert(arguments[1], float)
                dsr.set_animation_speed(speed)
                print(Fore.GREEN + ("Animation speed changed to %.2f" % speed) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, speed != 1.0)

            @staticmethod
            def set_phantom_type():
                phantom_type = convert(arguments[1], int)
                dsr.set_phantom_type(phantom_type)
                print(Fore.GREEN + ("Phantom type set to %d" % phantom_type) + Fore.RESET)

            @staticmethod
            def set_team_type():
                team_type = convert(arguments[1], int)
                dsr.set_team_type(team_type)
                print(Fore.GREEN + ("Team type set to %d" % team_type) + Fore.RESET)

            @staticmethod
            def set_sls():
                souls = convert(arguments[1], int)
                dsr.set_stat(Stats.SLS, souls)
                print(Fore.GREEN + ("Souls set to %d" % souls) + Fore.RESET)

            @staticmethod
            def set_hum():
                humanity = convert(arguments[1], int)
                dsr.set_stat(Stats.HUM, humanity)
                print(Fore.GREEN + ("Humanity set to %d" % humanity) + Fore.RESET)

            @staticmethod
            def set_name():
                name = " ".join(arguments[1:])
                dsr.set_name(name)
                print(Fore.GREEN + ("Name set to '%s'" % name) + Fore.RESET)

            @staticmethod
            def set_ng():
                new_game = convert(arguments[1], int)
                dsr.set_ng_mode(new_game)
                print(Fore.GREEN + ("NG changed to +%d" % new_game) + Fore.RESET)

            @staticmethod
            def set_covenant():
                raise NotImplementedError("This option not yet available")
                covenant_name = arguments[1]
                dsr.validate_covenant(covenant_name)
                covenant_id = dsr.covenants[covenant_name]
                dsr.set_covenant(covenant_id)
                print("Covenant changed to %s" % DarkSouls.get_name_from_arg(covenant_name))

            @staticmethod
            def get_status():
                dsr.print_status()

            @staticmethod
            def get_last_animation():
                dsr.read_performed_animations()

            @staticmethod
            def enable_super_armor():
                enable = arguments[1]
                dsr.set_super_armor(enable)
                print(Fore.GREEN + ("SUPER ARMOR %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_gravity():
                enable = arguments[1]
                dsr.set_no_gravity(not enable)
                print(Fore.GREEN + ("GRAVITY %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_no_dead():
                enable = arguments[1]
                dsr.set_no_dead(enable)
                print(Fore.GREEN + ("NO DEAD %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_no_stamina_consume():
                enable = arguments[1]
                dsr.set_no_stamina_consume(enable)
                print(Fore.GREEN + ("NO STAMINA CONSUME %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_no_goods_consume():
                enable = arguments[1]
                dsr.set_no_goods_consume(enable)
                print(Fore.GREEN + ("NO GOODS CONSUME %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_no_damage():
                enable = arguments[1]
                dsr.set_no_damage(enable)
                print(Fore.GREEN + ("NO DAMAGE %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_no_hit():
                enable = arguments[1]
                dsr.set_no_hit(enable)
                print(Fore.GREEN + ("NO HIT %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_no_update():
                enable = arguments[1]
                dsr.set_no_update(enable)
                print(Fore.GREEN + ("NO UPDATE %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_no_magic_all():
                enable = arguments[1]
                dsr.set_no_magic_all(enable)
                print(Fore.GREEN + ("NO MAGIC ALL %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_no_ammo_consume_all():
                enable = arguments[1]
                dsr.set_no_ammo_consume_all(enable)
                print(Fore.GREEN + ("NO AMMO CONSUME ALL %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_no_dead_all():
                enable = arguments[1]
                dsr.set_no_dead_all(enable)
                print(Fore.GREEN + ("NO DEAD ALL %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_no_damage_all():
                enable = arguments[1]
                dsr.set_no_damage_all(enable)
                print(Fore.GREEN + ("NO DAMAGE ALL %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_no_hit_all():
                enable = arguments[1]
                dsr.set_no_hit_all(enable)
                print(Fore.GREEN + ("NO HIT ALL %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_no_attack_all():
                enable = arguments[1]
                dsr.set_no_attack_all(enable)
                print(Fore.GREEN + ("NO ATTACK ALL %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_no_move_all():
                enable = arguments[1]
                dsr.set_no_move_all(enable)
                print(Fore.GREEN + ("NO MOVE ALL %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_no_update_ai_all():
                enable = arguments[1]
                dsr.set_no_update_ai_all(enable)
                print(Fore.GREEN + ("NO UPDATE AI ALL %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_death_cam():
                enable = arguments[1]
                dsr.death_cam(enable)
                print(Fore.GREEN + ("DEATH CAM %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_player_dead_mode():
                enable = arguments[1]
                dsr.set_player_dead_mode(enable)
                print(Fore.GREEN + ("PLAYER DEAD MODE %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_player_exterminate():
                enable = arguments[1]
                dsr.set_exterminate(enable)
                print(Fore.GREEN + ("PLAYER EXTERMINATE %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_player_hide():
                enable = arguments[1]
                dsr.set_hide(enable)
                print(Fore.GREEN + ("PLAYER HIDE %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_player_silence():
                enable = arguments[1]
                dsr.set_silence(enable)
                print(Fore.GREEN + ("PLAYER SILENCE %s" % ("enabled" if enable else "disabled")) + Fore.RESET)
                DarkSouls.update_static_func(command, arguments, enable)

            @staticmethod
            def enable_events():
                enable = arguments[1]
                dsr.disable_all_area_event(not enable)
                print(Fore.GREEN + ("ALL AREA EVENTS %s" % ("enabled" if enable else "disabled")) + Fore.RESET)

            @staticmethod
            def enable_npc():
                enable = arguments[1]
                if not enable:
                    if not dsr.warn_disable_npc():
                        return
                dsr.disable_all_area_enemies(not enable)
                print(Fore.GREEN + ("ALL AREA ENEMIES %s" % ("enabled" if enable else "disabled")) + Fore.RESET)

            @staticmethod
            def enable_map():
                enable = arguments[1]
                dsr.disable_all_area_map(not enable)
                print(Fore.GREEN + ("ALL AREA MAP %s" % ("enabled" if enable else "disabled")) + Fore.RESET)

            @staticmethod
            def enable_obj():
                enable = arguments[1]
                dsr.disable_all_area_obj(not enable)
                print(Fore.GREEN + ("ALL AREA OBJ %s" % ("enabled" if enable else "disabled")) + Fore.RESET)

            @staticmethod
            def enable_obj_break():
                enable = arguments[1]
                dsr.enable_all_area_obj_break(enable)
                print(Fore.GREEN + ("ALL AREA OBJ BREAK %s" % ("enabled" if enable else "disabled")) + Fore.RESET)

            @staticmethod
            def enable_hi_hit():
                enable = arguments[1]
                dsr.disable_all_area_hi_hit(not enable)
                print(Fore.GREEN + ("ALL AREA HI HIT %s" % ("enabled" if enable else "disabled")) + Fore.RESET)

            @staticmethod
            def enable_lo_hit():
                enable = arguments[1]
                dsr.disable_all_area_lo_hit(not enable)
                print(Fore.GREEN + ("ALL AREA LO HIT %s" % ("enabled" if enable else "disabled")) + Fore.RESET)

            @staticmethod
            def enable_sfx():
                enable = arguments[1]
                dsr.disable_all_area_sfx(not enable)
                print(Fore.GREEN + ("ALL AREA SFX %s" % ("enabled" if enable else "disabled")) + Fore.RESET)

            @staticmethod
            def enable_sound():
                enable = arguments[1]
                dsr.disable_all_area_sound(not enable)
                print(Fore.GREEN + ("ALL AREA SOUND %s" % ("enabled" if enable else "disabled")) + Fore.RESET)

            @staticmethod
            def enable_obj_break_record_mode():
                enable = arguments[1]
                dsr.enable_obj_break_record_mode(enable)
                print(Fore.GREEN + ("OBJ BREAK RECORD MODE %s" % ("enabled" if enable else "disabled")) + Fore.RESET)

            @staticmethod
            def enable_auto_map_warp_mode():
                enable = arguments[1]
                dsr.enable_auto_map_warp_mode(enable)
                print(Fore.GREEN + ("AUTO MAP WARP MODE %s" % ("enabled" if enable else "disabled")) + Fore.RESET)

            @staticmethod
            def enable_chr_npc_wander_test():
                enable = arguments[1]
                dsr.enable_chr_npc_wander_test(enable)
                print(Fore.GREEN + ("CHR NPC WANDER TEST %s" % ("enabled" if enable else "disabled")) + Fore.RESET)

            @staticmethod
            def enable_dbg_chr_all_dead():
                enable = arguments[1]
                dsr.enable_dbg_chr_all_dead(enable)
                print(Fore.GREEN + ("DBG CHR ALL DEAD %s" % ("enabled" if enable else "disabled")) + Fore.RESET)

            @staticmethod
            def enable_online_mode():
                enable = arguments[1]
                dsr.enable_online_mode(enable)
                print(Fore.GREEN + ("ONLINE MODE %s" % ("enabled" if enable else "disabled")) + Fore.RESET)

            @staticmethod
            def enable_enemy_control():
                enable = arguments[1]
                dsr.enable_enemy_control(enable)

            @staticmethod
            def on_flag_notify():
                evt = arguments[-1]
                flag_id, state = DarkSouls.ask_flag()
                DarkSouls.update_waiting_func(key=hash(evt), val={"val": (flag_id, state)})
                Thread(target=dsr.start_listen, args=(hash(evt), flag_id, state, evt)).start()

            @staticmethod
            def meta_test():
                DarkSouls._test(arguments[1:])

            @staticmethod
            def meta_info():
                import _version
                _version.print_app_info()

            @staticmethod
            def meta_open():
                from dsres.resources import open_resource
                open_resource(arguments)

            @staticmethod
            def meta_changelog():
                import _version
                _version.print_changelog()

            @staticmethod
            def meta_processes():
                DarkSouls.manage_thread_info(arguments[1:])

        Switcher.switch()
