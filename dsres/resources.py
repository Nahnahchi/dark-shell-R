from random import choice
from simpleaudio import WaveObject
from os.path import join, isfile, exists, isdir
from os import listdir, getcwd, getenv, makedirs, startfile
import sys

APPDATA = join(getenv("APPDATA"), "DarkShellR")
SAVE_DIR = join(APPDATA, "save")
MOD_DIR = join(APPDATA, "mod")
RES_DIR = join(getattr(sys, '_MEIPASS', getcwd()), "dsres")


try:
    makedirs(SAVE_DIR)
except FileExistsError:
    pass
try:
    makedirs(MOD_DIR)
except FileExistsError:
    pass


def play_random_sound():
    WaveObject.from_wave_file(join(get_sound_dir(), choice(get_sound_files()))).play()


def open_resource(args: list):
    if "appdata" in args:
        startfile(APPDATA)
    if "cwd" in args:
        startfile(RES_DIR)
    if "github" in args:
        import webbrowser
        from _version import __github__
        webbrowser.open(__github__)


def get_item_dir():
    return join(RES_DIR, "items")


def get_sound_dir():
    return join(RES_DIR, "sound")


def get_sound_files():
    sound_dir = get_sound_dir()
    sound_files = [f for f in listdir(sound_dir) if isfile(join(sound_dir, f))]
    return sound_files


def get_mod_item_files():
    return [f for f in listdir(MOD_DIR) if isfile(join(MOD_DIR, f))]


def get_item_files():
    item_dir = get_item_dir()
    item_files = [f for f in listdir(item_dir) if isfile(join(item_dir, f))]
    return item_files


def create_mod_files(categories: dict):
    for category in categories.keys():
        file = join(MOD_DIR, category + ".txt")
        if not exists(file) and not isdir(file):
            with open(file, "w") as f:
                f.write(hex(categories[category]).lstrip("0x").zfill(8))


def validate_item(name: str):
    for func in (get_item_files, get_items), (get_mod_item_files, get_mod_items):
        for file in func[0]():
            for item in func[1](file)[1:]:
                item = item.strip()
                if item:
                    if name in item.split()[3]:
                        return False
    return True


def write_mod_item(category: str, name: str, item_id: int):
    if not validate_item(name):
        raise KeyError("Item '%s' already exists!" % " ".join(name.split("-")).title())
    for file in get_mod_item_files():
        if file == category + ".txt":
            with open(join(MOD_DIR, file), "a") as f:
                f.write("\n%d %d %d %s" % (item_id, 1, 0, name))
                return True
    return False


def read_mod_items():
    items = []
    for file in get_mod_item_files():
        with open(join(MOD_DIR, file), "r") as f:
            for line in f.readlines()[1:]:
                if line.strip():
                    items.append(line)
    return items


def remove_mod_item(item: str):
    for file in get_mod_item_files():
        with open(join(MOD_DIR, file), "r+") as f:
            lines = f.readlines()
            f.seek(0)
            f.write(lines[0].strip())
            for line in lines[1:]:
                if line.strip():
                    if line.split()[3].strip() != item:
                        f.write("\n" + line.strip())
            f.truncate()


def clear_mod_items(categories: dict):
    for category_name in categories.keys():
        with open(join(MOD_DIR, category_name + ".txt"), "r+") as f:
            f.seek(0)
            f.write(hex(categories[category_name]).lstrip("0x").zfill(8))
            f.truncate()


def get_bonfires():
    return open("%s/bonfires.txt" % join(RES_DIR, "misc"), "r").readlines()


def get_items(file_name: str):
    return open("%s/%s" % (join(RES_DIR, "items"), file_name), "r").readlines()


def get_mod_items(file_name: str):
    return open("%s/%s" % (MOD_DIR, file_name), "r").readlines()


def get_infusions():
    return open("%s/infusions.txt" % join(RES_DIR, "misc"), "r").readlines()


def get_covenants():
    return open("%s/covenants.txt" % join(RES_DIR, "misc"), "r").readlines()


def get_banners():
    return open("%s/banners.txt" % join(RES_DIR, "misc"), "r").readlines()


def get_known_flags():
    return open("%s/%s" % (RES_DIR, "flags"), "r").readlines()
