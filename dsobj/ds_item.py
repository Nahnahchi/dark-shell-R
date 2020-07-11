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

    def __init__(self, source: str, category: int):
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


def infuse(item: DSRItem, infusion: DSRInfusion, upgrade: int):
    if upgrade > infusion.get_max_upgrade() or upgrade < 0:
        print("Can't upgrade %s weapons to +%d" % (infusion.get_name(), upgrade))
        return -1
    item_id = item.get_id() + upgrade
    if item.get_upgrade_type() == Upgrade.INFUSABLE or item.get_upgrade_type() == Upgrade.INFUSABLE_RESTRICTED:
        item_id += infusion.get_value()
    return item_id
