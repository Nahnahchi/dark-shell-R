from enum import Enum
from colorama import Fore


class Upgrade(Enum):

    NONE = 0
    UNIQUE = 1
    ARMOR = 2
    INFUSABLE = 3
    INFUSABLE_RESTRICTED = 4
    PYRO_FLAME = 5
    PYRO_FLAME_ASCENDED = 6


class DSRItem:

    def __init__(self, source: str, category: int = -1):
        source = source.split()
        self.category = category
        self.item_id = int(source[0]) if len(source) > 0 and source[0].isnumeric() else -1
        self.stack_limit = int(source[1]) if len(source) > 1 and source[1].isnumeric() else -1
        self.upgrade_type = Upgrade(int(source[2])) if len(source) > 2 and source[2].isnumeric() else Upgrade.NONE
        self.item_name = source[3] if len(source) > 3 else ""

    def get_id(self):
        return self.item_id

    def get_name(self):
        return self.item_name

    def get_stack_limit(self):
        return self.stack_limit

    def get_upgrade_type(self):
        return self.upgrade_type

    def get_category(self):
        return self.category


class DSRInfusion:

    def __init__(self, res: str):
        res = res.split()
        self.value = int(res[0]) if len(res) > 0 and res[0].isnumeric() else -1
        self.max_upgrade = int(res[1]) if len(res) > 1 and res[1].isnumeric() else -1
        self.restricted = bool(int(res[2])) if len(res) > 2 and res[2].isnumeric() else -1
        self.name = res[3] if len(res) > 3 else ""

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

    def get_max_upgrade(self):
        return self.max_upgrade

    def is_restricted(self):
        return self.is_restricted

    def infuse(self, item: DSRItem, upgrade: int):
        item_id = item.get_id()
        if item.get_upgrade_type() not in (Upgrade.INFUSABLE, Upgrade.INFUSABLE_RESTRICTED):
            print(Fore.RED + ("Item '%s' is not infusable!" % self.get_name().replace("-", " ").title()) + Fore.RESET)
        elif upgrade > self.get_max_upgrade() or upgrade < 0:
            print(Fore.RED + ("Can't upgrade %s weapons to +%d!" % (self.get_name(), upgrade)) + Fore.RESET)
        else:
            item_id += upgrade + self.get_value()
        return item_id
