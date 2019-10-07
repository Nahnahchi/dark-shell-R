from enum import Enum
from math import pi


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

    def can_read(self):
        return self.hook.Loaded

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

    def read_event_flag(self, flag_id: int):
        return self.hook.ReadEventFlag(flag_id)

    def write_event_flag(self, flag_id: int, state: bool):
        return self.hook.WriteEventFlag(flag_id, state)

    def death_cam(self, enable: bool):
        return self.hook.SetDeathCam(enable)

    def set_super_armor(self, enable: bool):
        return self.hook.SetPlayerSuperArmor(enable)

    def set_no_gravity(self, enable: bool):
        return self.hook.SetNoGravity(enable)

    def set_no_dead(self, enable: bool):
        return self.hook.SetPlayerNoDead(enable)

    def set_no_stamina_consume(self, enable: bool):
        return self.hook.SetPlayerNoStamina(enable)

    def set_no_goods_consume(self, enable: bool):
        return self.hook.SetPlayerNoGoods(enable)

    def set_no_damage(self, enable: bool):
        return self.hook.SetPlayerDisableDamage(enable)

    def set_no_hit(self, enable: bool):
        return self.hook.SetPlayerNoHit(enable)

    def get_player_dead_mode(self):
        return self.hook.GetPlayerDeadMode()

    def set_player_dead_mode(self, enable: bool):
        return self.hook.SetPlayerDeadMode(enable)

    def set_no_magic_all(self, enable: bool):
        return self.hook.SetAllNoMagicQty(enable)

    def set_no_stamina_all(self, enable: bool):
        return self.hook.SetAllNoStamina(enable)

    def set_exterminate(self, enable: bool):
        return self.hook.SetPlayerExterminate(enable)

    def set_no_ammo_consume_all(self, enable: bool):
        return self.hook.SetAllNoArrow(enable)

    def set_hide(self, enable: bool):
        return self.hook.SetPlayerHide(enable)

    def set_silence(self, enable: bool):
        return self.hook.SetPlayerSilence(enable)

    def set_no_dead_all(self, enable: bool):
        return self.hook.SetAllNoDead(enable)

    def set_no_damage_all(self, enable: bool):
        return self.hook.SetAllNoDamage(enable)

    def set_no_hit_all(self, enable: bool):
        return self.hook.SetAllNoHit(enable)

    def set_no_attack_all(self, enable: bool):
        return self.hook.SetAllNoAttack(enable)

    def set_no_move_all(self, enable: bool):
        return self.hook.SetAllNoMove(enable)

    def set_no_update_ai_all(self, enable: bool):
        return self.hook.SetAllNoUpdateAI(enable)

    def get_hp(self):
        return self.hook.GetHealth()

    def get_hp_max(self):
        return self.hook.GetHealthMax()

    def get_stamina(self):
        return self.hook.GetStaminaMax()

    def get_pos(self):
        return (
            self.hook.GetPositionX(),
            self.hook.GetPositionY(),
            self.hook.GetPositionZ(),
            (self.hook.GetPositionAngle() + pi) / (pi * 2) * 360
        )

    def get_pos_stable(self):
        return (
            self.hook.GetStablePositionX(),
            self.hook.GetStablePositionY(),
            self.hook.GetStablePositionZ(),
            (self.hook.GetStablePositionAngle() + pi) / (pi * 2) * 360
        )

    def jump_pos(self, x, y, z, a):
        self.hook.PosWarp(x, y, z, a)

    def set_bonfire(self, value: int):
        self.hook.SetLastBonfire(value)

    def bonfire_warp(self):
        return self.hook.BonfireWarp() == 0

    def item_get(self, item_category, item_id, item_count):
        return self.hook.GetItem(item_category, item_id, item_count) == 0
