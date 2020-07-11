from dslib.ds_process import DSRProcess, Stats
from dslib.ds_cmd import DSRCmd
from dsobj.ds_bonfire import DSRBonfire
from dsobj.ds_item import DSRItem, DSRInfusion, Upgrade, infuse
from dsres.ds_resources import SAVE_DIR
from dsres.ds_commands import nest_add, nest_remove, nest_reset
from prompt_toolkit.shortcuts import set_title, input_dialog, radiolist_dialog, message_dialog, yes_no_dialog
from os.path import join
from threading import Thread
from collections import defaultdict
from traceback import format_exc
from colorama import Fore
from ctypes import ArgumentError
from pickle import load, dump, UnpicklingError


class DarkSouls(DSRProcess):

    PROCESS_NAME = "DARK SOULS™: REMASTERED"
    STATIC_SOURCE = join(SAVE_DIR, "static.dat")
    STATIC_FUNC = {}
    ITEM_CATEGORIES = {
        "weapon": 0x00000000,
        "good": 0x40000000,
        "ring": 0x20000000,
        "armor": 0x10000000
    }

    def __init__(self, debug=False):
        super(DarkSouls, self).__init__(DarkSouls.PROCESS_NAME, debug)
        self.debug = debug
        self.bonfires = defaultdict(DSRBonfire)
        self.items = defaultdict(DSRItem)
        self.infusions = defaultdict(DSRInfusion)
        self.covenants = defaultdict(int)
        self.stats = {stat: 0 for stat in vars(Stats).values() if isinstance(stat, Stats)}
        Thread(target=self.read_bonfires).start()
        Thread(target=self.read_items).start()
        Thread(target=self.read_infusions).start()
        Thread(target=self.read_covenants).start()
        Thread(target=self.read_static_func).start()

    def update_version(self):
        set_title("DarkShell-R — Game Version: %s" % self.get_version())

    def change_stat(self, stat_name: str, stat_value: int):
        try:
            stat = Stats(stat_name)
            return self.set_stat(stat, stat_value)
        except ValueError:
            print("Wrong arguments: %s" % stat_name)
            return False

    @staticmethod
    def warn_anti_cheat():
        message_dialog(
            title="WARNING",
            text="Dark Souls Remastered has an anti-cheat system.\nDo not use this online!"
        ).run()

    @staticmethod
    def get_name_from_arg(arg: str):
        return arg.replace("-", " ").title()

    @staticmethod
    def add_new_item(args):
        if len(args) == 0:
            raise ArgumentError("No arguments given!")
        else:
            if args[0] == "clear":
                from dsres.ds_resources import clear_mod_items
                clear_mod_items(DarkSouls.ITEM_CATEGORIES)
                nest_reset()
            elif args[0] == "remove":
                from dsres.ds_resources import remove_mod_item
                try:
                    remove_mod_item(args[1])
                    nest_remove(args[1])
                except IndexError:
                    raise ArgumentError("Item name not specified!")
            elif args[0] == "list":
                from dsres.ds_resources import read_mod_items
                print("\n\tID\t\tName")
                for item in read_mod_items():
                    item = item.split()
                    if len(item) == 4:
                        print("\t%s\t\t%s" % (item[0], DarkSouls.get_name_from_arg(item[3])))
                print("\n")
            elif args[0] == "add":
                from dsres.ds_resources import create_mod_files
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
                if item_id is None:
                    return False
                item_name = input_dialog(
                    title="Enter item name",
                    text="Name of the new %s:" % category
                ).run()
                if item_name is None:
                    return False
                from dsres.ds_resources import write_mod_item
                formatted_name = "-".join(item_name.lower().split())
                try:
                    if write_mod_item(category, formatted_name, int(item_id)):
                        print("%s '%s' (ID: %s) added successfully" % (category.title(), item_name.title(), item_id))
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
                print("Can't upgrade %sPyromancy Flame to +%s" % ("Ascended " if is_pyro_asc else "", upgrade))
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
                print("Can't upgrade %s to +%s" % ("Unique" if is_unique else "Armor", upgrade))
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
        print("\n\tHealth: %d/%d" % (self.get_hp(), self.get_hp_max()))
        print("\tStamina: %d\n" % self.get_stamina())
        for stat in self.stats.keys():
            print("\t%s: %d" % (stat.value, self.get_stat(stat)))
        print("\n")

    @staticmethod
    def raise_warp_error(b_full_name: str):
        from dsres.ds_commands import DS_NEST
        if not b_full_name.strip():
            raise ArgumentError("No arguments given!")
        area_name = b_full_name.split()[0]
        if area_name not in DS_NEST["warp"].keys():
            raise ArgumentError("Unknown area name: %s" % DarkSouls.get_name_from_arg(area_name))
        else:
            if len(b_full_name.split()) < 2:
                raise ArgumentError("No bonfire name specified!")
            bonfire_name = b_full_name.split()[1]
            if bonfire_name not in DS_NEST["warp"][area_name]:
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
            print("Warped to location ID: %d" % b_id)

    def level_stat(self, s_name: str, s_level: int):
        for stat in self.stats.keys():
            if stat.value != s_name:
                if stat != Stats.SLV:
                    self.stats[stat] = self.get_stat(stat)
            else:
                new_stat = s_level
                cur_stat = self.get_stat(stat)
                soul_level = self.get_soul_level() + (new_stat - cur_stat)
                self.stats[stat] = new_stat
                self.stats[Stats.SLV] = soul_level
        return self.level_up(self.stats)

    def create_item(self, i_name: str, i_count: int, func):
        if i_name not in self.items.keys():
            raise ArgumentError("Item '%s' doesn't exist!" % DarkSouls.get_name_from_arg(i_name))
        else:
            item = self.items[i_name]
            i_id = item.get_id()
            i_cat = item.get_category()
            func(i_cat, i_id, i_count)
            print("Created new item, ID: %d" % i_id)

    @staticmethod
    def create_custom_item(args: list, func):
        try:
            i_cat, i_id, i_count = DarkSouls.ITEM_CATEGORIES[args[0]], args[1], args[2]
            func(i_cat, i_id, i_count)
            print("Created new item, ID: %s" % i_id)
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
                print("Can't upgrade this item!")
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
                i_id = infuse(item, self.infusions[infusion], int(upgrade))
            else:
                raise AssertionError(
                    "Can't determine the upgrade type for item '%s'!" % DarkSouls.get_name_from_arg(i_name)
                )
            if i_id <= 0:
                print("Upgrade failed")
            else:
                self.item_get(i_category, i_id, i_count)
                print("Upgrade successful")

    def read_bonfires(self):
        from dsres.ds_resources import get_bonfires
        bonfires = get_bonfires()
        for b in bonfires:
            try:
                bonfire = DSRBonfire(b.strip())
                self.bonfires[bonfire.get_name()] = bonfire
            except Exception as e:
                print(Fore.RED + (format_exc() if self.debug else
                                  "%s: Error reading bonfire: %s | %s" %
                                  (type(e).__name__, b.split(), e)) + Fore.RESET)

    def read_items(self):
        from dsres.ds_resources import get_item_files, get_items, get_mod_item_files, get_mod_items
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
                        print(
                            Fore.RED + (format_exc() if self.debug else
                                        "%s: Error reading item category in file '%s' | %s" %
                                        (type(e).__name__, file, e)) + Fore.RESET)
                        break
                    except Exception as e:
                        print(Fore.RED + (format_exc() if self.debug else
                                          "%s: Error reading item: %s | %s" %
                                          (type(e).__name__, i.title().split(), e)) + Fore.RESET)
                        continue

    def read_infusions(self):
        from dsres.ds_resources import get_infusions
        infusions = get_infusions()
        for i in infusions:
            try:
                infusion = DSRInfusion(i.strip())
                self.infusions[infusion.get_name()] = infusion
            except Exception as e:
                print(Fore.RED + (format_exc() if self.debug else
                                  "%s: Error reading infusion: %s | %s" %
                                  (type(e).__name__, i.split(), e)) + Fore.RESET)

    def read_covenants(self):
        from dsres.ds_resources import get_covenants
        covenants = get_covenants()
        for c in covenants:
            try:
                covenant = c.split()
                cov_id = int(covenant[0])
                cov_name = covenant[1]
                self.covenants[cov_name] = cov_id
            except Exception as e:
                print(Fore.RED + (format_exc() if self.debug else
                                  "%s: Error reading covenant: %s | %s" %
                                  (type(e).__name__, c.split(), e)) + Fore.RESET)

    @staticmethod
    def read_static_func():
        try:
            static_func = load(open(DarkSouls.STATIC_SOURCE, "rb"))
            DarkSouls.STATIC_FUNC.update(static_func)
        except (FileNotFoundError, UnpicklingError, EOFError):
            open(DarkSouls.STATIC_SOURCE, "w+")
            DarkSouls.STATIC_FUNC.clear()

    @staticmethod
    def write_static_func():
        dump(DarkSouls.STATIC_FUNC, open(DarkSouls.STATIC_SOURCE, "wb"))

    def validate_covenant(self, key: str):
        if key not in self.covenants.keys():
            raise ArgumentError("Covenant '%s' doesn't exist!" % DarkSouls.get_name_from_arg(key))

    @staticmethod
    def validate_stat(stat_name: str):
        try:
            Stats(stat_name)
        except ValueError:
            raise ArgumentError("Unknown argument: %s" % stat_name)

    @staticmethod
    def validate_flag(flag_id):
        try:
            int(flag_id)
        except ValueError:
            raise ArgumentError("Unknown argument: %s" % flag_id)

    def switch(self, command: str, arguments: list):

        dark_souls = self

        def convert(data, data_type: type):
            try:
                return data_type(data)
            except ValueError:
                raise ArgumentError("Can't convert %s '%s' to %s!" % (type(data).__name__, data, data_type.__name__))

        class Switcher:

            @classmethod
            def switch(cls):
                case_name = DSRCmd.get_method_name(prefix=command + "_", name=arguments[0])
                default = getattr(cls, command + "_default")
                case_method = getattr(cls, case_name, default)
                case_method()

            @staticmethod
            def set_default():
                stat_name = arguments[0]
                dark_souls.validate_stat(stat_name)
                stat_value = int(arguments[1])
                if dark_souls.change_stat(stat_name, stat_value):
                    print("%s set to %d" % (stat_name.upper(), stat_value))

            @staticmethod
            def get_default():
                flag_id = convert(arguments[0], int)
                print("FLAG %d: %s" % (flag_id, dark_souls.read_event_flag(flag_id)))

            @staticmethod
            def enable_default():
                dark_souls.validate_flag(arguments[0])
                flag_id = convert(arguments[0], int)
                enable = arguments[1]
                dark_souls.write_event_flag(flag_id, enable)
                print("EVENT FLAG %d %s" % (flag_id, ("enabled" if enable else "disabled")))

            @staticmethod
            def set_speed_game():
                speed = convert(arguments[1], float)
                dark_souls.set_game_speed(speed)
                print("Game speed changed to %.2f" % speed)
                if speed == 1.0:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def set_phantom_type():
                raise NotImplementedError("This option not yet available")
                phantom_type = convert(arguments[1], int)
                dark_souls.set_phantom_type(phantom_type)
                print("Phantom type set to %d" % phantom_type)

            @staticmethod
            def set_team_type():
                raise NotImplementedError("This option not yet available")
                team_type = convert(arguments[1], int)
                dark_souls.set_team_type(team_type)
                print("Team type set to %d" % team_type)

            @staticmethod
            def set_sls():
                souls = convert(arguments[1], int)
                dark_souls.set_stat(Stats.SLS, souls)
                print("Souls set to %d" % souls)

            @staticmethod
            def set_hum():
                humanity = convert(arguments[1], int)
                dark_souls.set_stat(Stats.HUM, humanity)
                print("Humanity set to %d" % humanity)

            @staticmethod
            def set_name():
                name = " ".join(arguments[1:])
                dark_souls.set_name(name)
                print("Name set to '%s'" % name)

            @staticmethod
            def set_ng():
                raise NotImplementedError("This option not yet available")
                new_game = convert(arguments[1], int)
                dark_souls.set_ng_mode(new_game)
                print("NG changed to +%d" % new_game)

            @staticmethod
            def set_covenant():
                raise NotImplementedError("This option not yet available")
                covenant_name = arguments[1]
                dark_souls.validate_covenant(covenant_name)
                covenant_id = dark_souls.covenants[covenant_name]
                dark_souls.set_covenant(covenant_id)
                print("Covenant changed to %s" % DarkSouls.get_name_from_arg(covenant_name))

            @staticmethod
            def get_status():
                dark_souls.print_status()

            @staticmethod
            def enable_super_armor():
                enable = arguments[1]
                dark_souls.set_super_armor(enable)
                print("SUPER ARMOR %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_draw():
                raise NotImplementedError("This option not yet available")
                enable = arguments[1]
                dark_souls.set_draw_enable(enable)
                print("DRAW %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_gravity():
                enable = arguments[1]
                dark_souls.set_no_gravity(not enable)
                print("GRAVITY %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_no_dead():
                enable = arguments[1]
                dark_souls.set_no_dead(enable)
                print("NO DEAD %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_no_stamina_consume():
                enable = arguments[1]
                dark_souls.set_no_stamina_consume(enable)
                print("NO STAMINA CONSUME %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_no_goods_consume():
                enable = arguments[1]
                dark_souls.set_no_goods_consume(enable)
                print("NO GOODS CONSUME %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_no_update():
                raise NotImplementedError("This option not yet available")
                enable = arguments[1]
                dark_souls.set_no_update(enable)
                print("NO UPDATE %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_no_attack():
                raise NotImplementedError("This option not yet available")
                enable = arguments[1]
                dark_souls.set_no_attack(enable)
                print("NO ATTACK %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_no_move():
                raise NotImplementedError("This option not yet available")
                enable = arguments[1]
                dark_souls.set_no_move(enable)
                print("NO MOVE %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_no_damage():
                enable = arguments[1]
                dark_souls.set_no_damage(enable)
                print("NO DAMAGE %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_no_hit():
                enable = arguments[1]
                dark_souls.set_no_hit(enable)
                print("NO HIT %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_no_magic_all():
                enable = arguments[1]
                dark_souls.set_no_magic_all(enable)
                print("NO MAGIC ALL %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_no_ammo_consume_all():
                enable = arguments[1]
                dark_souls.set_no_ammo_consume_all(enable)
                print("NO AMMO CONSUME ALL %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_no_dead_all():
                enable = arguments[1]
                dark_souls.set_no_dead_all(enable)
                print("NO DEAD ALL %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_no_damage_all():
                enable = arguments[1]
                dark_souls.set_no_damage_all(enable)
                print("NO DAMAGE ALL %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_no_hit_all():
                enable = arguments[1]
                dark_souls.set_no_hit_all(enable)
                print("NO HIT ALL %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_no_attack_all():
                enable = arguments[1]
                dark_souls.set_no_attack_all(enable)
                print("NO ATTACK ALL %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_no_move_all():
                enable = arguments[1]
                dark_souls.set_no_move_all(enable)
                print("NO MOVE ALL %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_no_update_ai_all():
                enable = arguments[1]
                dark_souls.set_no_update_ai_all(enable)
                print("NO UPDATE AI ALL %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_death_cam():
                enable = arguments[1]
                dark_souls.death_cam(enable)
                print("DEATH CAM %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_player_dead_mode():
                enable = arguments[1]
                dark_souls.set_player_dead_mode(enable)
                print("PLAYER DEAD MODE %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_player_exterminate():
                enable = arguments[1]
                dark_souls.set_exterminate(enable)
                print("PLAYER EXTERMINATE %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_player_hide():
                enable = arguments[1]
                dark_souls.set_hide(enable)
                print("PLAYER HIDE %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_player_silence():
                enable = arguments[1]
                dark_souls.set_silence(enable)
                print("PLAYER SILENCE %s" % ("enabled" if enable else "disabled"))
                if not enable:
                    DarkSouls.STATIC_FUNC.pop((command, arguments[0]))
                else:
                    DarkSouls.STATIC_FUNC[(command, arguments[0])] = arguments

            @staticmethod
            def enable_event():
                enable = arguments[1]
                dark_souls.disable_all_area_event(not enable)
                print("ALL AREA EVENT %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_npc():
                enable = arguments[1]
                if not enable:
                    if not dark_souls.warn_disable_npc():
                        return
                dark_souls.disable_all_area_enemies(not enable)
                print("ALL AREA ENEMIES %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_map():
                enable = arguments[1]
                dark_souls.disable_all_area_map(not enable)
                print("ALL AREA MAP %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_obj():
                enable = arguments[1]
                dark_souls.disable_all_area_obj(not enable)
                print("ALL AREA OBJ %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_obj_break():
                enable = arguments[1]
                dark_souls.enable_all_area_obj_break(enable)
                print("ALL AREA OBJ BREAK %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_hi_hit():
                enable = arguments[1]
                dark_souls.disable_all_area_hi_hit(not enable)
                print("ALL AREA HI HIT %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_lo_hit():
                enable = arguments[1]
                dark_souls.disable_all_area_lo_hit(not enable)
                print("ALL AREA LO HIT %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_sfx():
                enable = arguments[1]
                dark_souls.disable_all_area_sfx(not enable)
                print("ALL AREA SFX %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_sound():
                enable = arguments[1]
                dark_souls.disable_all_area_sound(not enable)
                print("ALL AREA SOUND %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_obj_break_record_mode():
                enable = arguments[1]
                dark_souls.enable_obj_break_record_mode(enable)
                print("OBJ BREAK RECORD MODE %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_auto_map_warp_mode():
                enable = arguments[1]
                dark_souls.enable_auto_map_warp_mode(enable)
                print("AUTO MAP WARP MODE %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_chr_npc_wander_test():
                enable = arguments[1]
                dark_souls.enable_chr_npc_wander_test(enable)
                print("CHR NPC WANDER TEST %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_dbg_chr_all_dead():
                enable = arguments[1]
                dark_souls.enable_dbg_chr_all_dead(enable)
                print("DBG CHR ALL DEAD %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_online_mode():
                enable = arguments[1]
                dark_souls.enable_online_mode(enable)
                print("ONLINE MODE %s" % ("enabled" if enable else "disabled"))

        Switcher.switch()
        DarkSouls.write_static_func()
