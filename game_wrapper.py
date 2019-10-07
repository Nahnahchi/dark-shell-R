from inspect import getfile, currentframe
from os import listdir, getenv, makedirs
from os.path import join, dirname, isfile
from dslib.ds_process import DSRProcess, Stat
from dslib.ds_cmprocessor import DSRCmp
from dsobj.ds_bonfire import DSRBonfire
from dsobj.ds_item import DSRItem, DSRInfusion, Upgrade, infuse
from prompt_toolkit.shortcuts import set_title, input_dialog, radiolist_dialog
from threading import Thread
from time import sleep
from collections import defaultdict


save_dir = join(getenv("APPDATA"), "DarkShell", "save")
try:
    makedirs(save_dir)
except FileExistsError:
    pass


class DarkSouls(DSRProcess):

    STATIC_SOURCE = join(save_dir, "static")

    def __init__(self, hook):
        super(DarkSouls, self).__init__(hook)
        self.bonfires = defaultdict(DSRBonfire)
        self.items = defaultdict(DSRItem)
        self.infusions = defaultdict(DSRInfusion)
        Thread(target=self.check_version).start()
        Thread(target=self.read_bonfires).start()
        Thread(target=self.read_items).start()
        Thread(target=self.read_infusions).start()

    def check_version(self):
        while True:
            set_title("Dark Shell R - Game Version: %s" % self.get_version())
            sleep(10)

    def change_stat(self, stat_name: str, stat_value: int):
        try:
            stat = Stat(stat_name)
            return self.set_stat(stat, stat_value)
        except ValueError:
            print("Wrong arguments: %s" % stat_name)
            return False

    @staticmethod
    def get_item_name_and_count(args: list):
        i_name = args[0]
        i_count = 1
        try:
            if len(args) >= 2:
                i_count = int(args[1])
        except ValueError:
            print("Wrong parameter type: %s" % args[1])
            return None, 0
        return i_name, i_count

    @staticmethod
    def get_upgrade_value_infusable(infusions: list, item: DSRItem):
        infusion = radiolist_dialog(
            title="Select infusion type",
            text="How would you like %s to be upgraded?" % item.get_name().upper().replace("-", " "),
            values=infusions
        ).run()
        if infusion is None:
            return None
        upgrade = input_dialog(
            title="Enter upgrade value",
            text="Item type: Normal [%s]" % infusion.upper()
        ).run()
        return upgrade, infusion

    @staticmethod
    def get_upgrade_value_pyro_flame(item: DSRItem):
        is_pyro_asc = item.get_upgrade_type() == Upgrade.PYRO_FLAME_ASCENDED
        max_upgrade = 5 if is_pyro_asc else 15
        upgrade = input_dialog(
            title="Enter upgrade value for %s" % item.get_name().upper().replace("-", " "),
            text="Item type: %sPyromancy Flame" % "Ascended " if is_pyro_asc else ""
        ).run()
        if int(upgrade) > max_upgrade or int(upgrade) < 0:
            print("Can't upgrade %sPyromancy Flame to +%s" % ("Ascended " if is_pyro_asc else "", upgrade))
            return None
        return upgrade

    @staticmethod
    def get_upgrade_value_armor_or_unique(item: DSRItem):
        is_unique = item.get_upgrade_type() == Upgrade.UNIQUE
        max_upgrade = 5 if is_unique else 10
        upgrade = input_dialog(
            title="Enter upgrade value for %s" % item.get_name().upper().replace("-", " "),
            text="Item type: %s" % "Unique" if is_unique else "Armor"
        ).run()
        if int(upgrade) > max_upgrade or int(upgrade) < 0:
            print("Can't upgrade %s to +%s" % ("Unique" if is_unique else "Armor", upgrade))
            return None
        return upgrade

    def print_stats(self):
        print("\n\tHealth: %d/%d" % (self.get_hp(), self.get_hp_max()))
        print("\tStamina: %d\n" % self.get_stamina())
        for stat in vars(Stat).values():
            if isinstance(stat, Stat):
                print("\t%s: %d" % (stat.value, self.get_stat(stat)))
        print("\n")

    def bonfire_warp_by_name(self, b_name: str):
        if b_name not in self.bonfires.keys():
            print("Wrong arguments: %s" % b_name)
        else:
            b_id = self.bonfires[b_name].get_id()
            self.set_bonfire(b_id)
            if self.bonfire_warp():
                print("Warped to location ID: %d" % b_id)
            else:
                print("Failed to warp")

    def create_item(self, i_name: str, i_count: int, func=None):
        if i_name not in self.items.keys():
            print("Wrong arguments: %s" % i_name)
        else:
            item = self.items[i_name]
            i_id = item.get_id()
            i_cat = item.get_category()
            if func(i_cat, i_id, i_count):
                print("Created new item, ID: %d" % i_id)
            else:
                print("Failed to create item")

    def upgrade_item(self, i_name: str, i_count: int):
        if i_name not in self.items.keys():
            print("Item '%s' doesn't exist!" % i_name)
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
                print("Wrong arguments: %s" % i_name)
                return
            if i_id > 0:
                if self.item_get(i_category, i_id, i_count):
                    print("Upgrade successful")
                    return
            print("Upgrade failed")

    def read_bonfires(self):
        bonfires = open("dsres/misc/bonfires.txt", "r").readlines()
        for b in bonfires:
            bonfire = DSRBonfire(b.strip())
            self.bonfires[bonfire.get_name()] = bonfire

    def read_items(self):
        item_dir = join(dirname(getfile(currentframe())), "dsres", "items")
        item_files = [f for f in listdir(item_dir) if isfile(join(item_dir, f))]
        for file in item_files:
            items = open("dsres/items/%s" % file, "r").readlines()
            category = items[0]
            for i in items[1:]:
                item = DSRItem(i.strip(), int(category, 16))
                self.items[item.get_name()] = item

    def read_infusions(self):
        infusions = open("dsres/misc/infusions.txt", "r").readlines()
        for i in infusions:
            infusion = DSRInfusion(i.strip())
            self.infusions[infusion.get_name()] = infusion

    def switch(self, command: str, arguments: list):

        dark_souls = self

        class Switcher:

            @classmethod
            def switch(cls):
                case_name = DSRCmp.get_method_name(prefix=command+"_", name=arguments[0])
                default = getattr(cls, command + "_default")
                case_method = getattr(cls, case_name, default)
                case_method()

            @staticmethod
            def set_default():
                stat_name = arguments[0]
                stat_value = int(arguments[1])
                if dark_souls.change_stat(stat_name, stat_value):
                    print("%s set to %d" % (stat_name.upper(), stat_value))

            @staticmethod
            def get_default():
                flag_id = int(arguments[0])
                if dark_souls.is_hooked():
                    print("FLAG %d: %s" % (flag_id, dark_souls.read_event_flag(flag_id)))

            @staticmethod
            def enable_default():
                flag_id = int(arguments[0])
                enable = arguments[1]
                if dark_souls.write_event_flag(flag_id, enable):
                    print("EVENT FLAG %d %s" % (flag_id, ("enabled" if enable else "disabled")))

            @staticmethod
            def static_default():
                with open(DarkSouls.STATIC_SOURCE, "a") as static_source:
                    static_source.write(" ".join(arguments) + "\n")

            @staticmethod
            def set_speed_game():
                speed = float(arguments[1])
                if dark_souls.set_game_speed(speed):
                    print("Game speed changed to %.2f" % speed)

            @staticmethod
            def get_stats():
                dark_souls.print_stats()

            @staticmethod
            def enable_gravity():
                enable = arguments[1]
                if dark_souls.set_no_gravity(not enable):
                    print("GRAVITY %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_no_dead():
                enable = arguments[1]
                if dark_souls.set_no_dead(enable):
                    print("NO DEAD %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_no_stamina_consume():
                enable = arguments[1]
                if dark_souls.set_no_stamina_consume(enable):
                    print("NO STAMINA CONSUME %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_no_goods_consume():
                enable = arguments[1]
                if dark_souls.set_no_goods_consume(enable):
                    print("NO GOODS CONSUME %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_no_damage():
                enable = arguments[1]
                if dark_souls.set_no_damage(enable):
                    print("NO DAMAGE %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_no_hit():
                enable = arguments[1]
                if dark_souls.set_no_hit(enable):
                    print("NO HIT %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_no_magic_all():
                enable = arguments[1]
                if dark_souls.set_no_magic_all(enable):
                    print("NO MAGIC ALL %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_no_ammo_consume_all():
                enable = arguments[1]
                if dark_souls.set_no_ammo_consume_all(enable):
                    print("NO AMMO CONSUME ALL %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_no_dead_all():
                enable = arguments[1]
                if dark_souls.set_no_dead_all(enable):
                    print("NO DEAD ALL %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_no_damage_all():
                enable = arguments[1]
                if dark_souls.set_no_damage_all(enable):
                    print("NO DAMAGE ALL %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_no_hit_all():
                enable = arguments[1]
                if dark_souls.set_no_hit_all(enable):
                    print("NO HIT ALL %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_no_attack_all():
                enable = arguments[1]
                if dark_souls.set_no_attack_all(enable):
                    print("NO ATTACK ALL %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_no_move_all():
                enable = arguments[1]
                if dark_souls.set_no_move_all(enable):
                    print("NO MOVE ALL %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_death_cam():
                enable = arguments[1]
                if dark_souls.death_cam(enable):
                    print("DEATH CAM %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_player_dead_mode():
                enable = arguments[1]
                if dark_souls.set_player_dead_mode(enable):
                    print("PLAYER DEAD MODE %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_player_exterminate():
                enable = arguments[1]
                if dark_souls.set_exterminate(enable):
                    print("PLAYER EXTERMINATE %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_player_hide():
                enable = arguments[1]
                if dark_souls.set_hide(enable):
                    print("PLAYER HIDE %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def enable_player_silence():
                enable = arguments[1]
                if dark_souls.set_silence(enable):
                    print("PLAYER SILENCE %s" % ("enabled" if enable else "disabled"))

            @staticmethod
            def static_list():
                lines = open(DarkSouls.STATIC_SOURCE, "r").readlines()
                for i in range(len(lines)):
                    print("\t%d %s" % (i, lines[i].strip()))

            @staticmethod
            def static_remove():
                remove_ind = int(arguments[1])
                lines = open(DarkSouls.STATIC_SOURCE, "r").readlines()
                del lines[remove_ind]
                open(DarkSouls.STATIC_SOURCE, "w").writelines(lines)

            @staticmethod
            def static_clean():
                open(DarkSouls.STATIC_SOURCE, "w").write("")

        Switcher.switch()
