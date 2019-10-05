from enum import Enum


class Stat(Enum):

    VIT = "vit"
    ATN = "atn"
    END = "end"
    STR = "str"
    DEX = "dex"
    RES = "res"
    INT = "int"
    FTH = "fth"
    SLV = "slv"
    SLS = "sls"
    HUM = "hum"


class DSRProcess:

    def __init__(self, hook):
        self.hook = hook
        self.hook.Start()

    def get_version(self):
        return self.hook.Version

    def is_hooked(self):
        return self.hook.Hooked

    def set_game_speed(self, value):
        return self.hook.SetAnimSpeed(value)

    def get_stat(self, stat: Stat):
        if stat == Stat.VIT:
            return self.hook.GetVitality()
        elif stat == Stat.ATN:
            return self.hook.GetAttunement()
        elif stat == Stat.END:
            return self.hook.GetEndurance()
        elif stat == Stat.STR:
            return self.hook.GetStrength()
        elif stat == Stat.DEX:
            return self.hook.GetDexterity()
        elif stat == Stat.RES:
            return self.hook.GetResistance()
        elif stat == Stat.INT:
            return self.hook.GetIntelligence()
        elif stat == Stat.FTH:
            return self.hook.GetFaith()
        elif stat == Stat.SLV:
            return self.hook.GetSoulLevel()
        elif stat == Stat.SLS:
            return self.hook.GetSouls()
        elif stat == Stat.HUM:
            return self.hook.GetHumanity()

    def update_sl(self, stat: Stat, new_val: int):
        old_val = self.get_stat(stat)
        return self.hook.SetSoulLevel(self.hook.GetSoulLevel() + (new_val - old_val))

    def set_stat(self, stat: Stat, value: int):
        if stat == Stat.VIT:
            return self.update_sl(stat, value) and self.hook.SetVitality(value)
        elif stat == Stat.ATN:
            return self.update_sl(stat, value) and self.hook.SetAttunement(value)
        elif stat == Stat.END:
            return self.update_sl(stat, value) and self.hook.SetEndurance(value)
        elif stat == Stat.STR:
            return self.update_sl(stat, value) and self.hook.SetStrength(value)
        elif stat == Stat.DEX:
            return self.update_sl(stat, value) and self.hook.SetDexterity(value)
        elif stat == Stat.RES:
            return self.update_sl(stat, value) and self.hook.SetResistance(value)
        elif stat == Stat.INT:
            return self.update_sl(stat, value) and self.hook.SetIntelligence(value)
        elif stat == Stat.FTH:
            return self.update_sl(stat, value) and self.hook.SetFaith(value)
        elif stat == Stat.SLV:
            return self.hook.SetSoulLevel(value)
        elif stat == Stat.SLS:
            return self.hook.SetSouls(value)
        elif stat == Stat.HUM:
            return self.hook.SetHumanity(value)

    def get_hp(self):
        return self.hook.GetHealth()

    def get_hp_mod_max(self):
        return self.hook.GetHealthMax()

    def get_stamina(self):
        return self.hook.GetStaminaMax()

    def set_bonfire(self, value: int):
        self.hook.SetLastBonfire(value)

    def bonfire_warp(self):
        return self.hook.BonfireWarp() == 0

    def item_get(self, item_category, item_id, item_count):
        return self.hook.GetItem(item_category, item_id, item_count) == 0
