from enum import Enum


class Upgrade(Enum):

    NONE = 0
    UNIQUE = 1
    ARMOR = 2
    INFUSABLE = 3
    INFUSABLE_RESTRICTED = 4
    PYRO_FLAME = 5
    PYRO_FLAME_ASCENDED = 6


class DSRItem:

    def __init__(self, res: str, category: int):
        res = res.split()
        self.category = category
        self.item_id = int(res[0])
        self.stack_limit = int(res[1])
        self.upgrade_type = Upgrade(int(res[2]))
        self.item_name = res[3]

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
        self.value = int(res[0])
        self.max_upgrade = int(res[1])
        self.restricted = bool(int(res[2]))
        self.name = res[3]

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

    def get_max_upgrade(self):
        return self.max_upgrade

    def is_restricted(self):
        return self.is_restricted


def infuse(item: DSRItem, infusion: DSRInfusion, upgrade: int):
    if upgrade > infusion.get_max_upgrade() or upgrade < 0:
        print("Can't upgrade %s weapons to +%d" % (infusion.get_name(), upgrade))
        return -1
    item_id = item.get_id() + upgrade
    if item.get_upgrade_type() == Upgrade.INFUSABLE or item.get_upgrade_type() == Upgrade.INFUSABLE_RESTRICTED:
        item_id += infusion.get_value()
    return item_id
