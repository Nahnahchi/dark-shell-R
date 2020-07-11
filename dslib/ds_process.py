from enum import Enum
from math import pi
# noinspection PyUnresolvedReferences
from dsprh.ds_imports import DSRHook


class ReadMemoryError(Exception):

    def __init__(self, message="Failed to read memory"):
        self.message = message
        super(ReadMemoryError, self).__init__(self.message)


class WriteMemoryError(Exception):

    def __init__(self, message="Failed to write memory"):
        self.message = message
        super(WriteMemoryError, self).__init__(self.message)


class AsmExecuteError(Exception):

    ERR = {
        0x00000080: "WAIT_ABANDONED",
        0x00000102: "WAIT_TIMEOUT",
        0xFFFFFFFF: "WAIT_FAILED"
    }

    def __init__(self, code, message="Failed to execute assembly"):
        self.message = message
        self.error = AsmExecuteError.ERR[code] if code in AsmExecuteError.ERR.keys() else "REASON_UNKNOWN"
        super(AsmExecuteError, self).__init__(self.message)

    def __str__(self):
        return "%s (%s)" % (self.message, self.error)


class Stats(Enum):

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

    def __init__(self, process_name, debug=False):
        self.hook = DSRHook(self, 5000, 5000, process_name)
        self.debug = debug
        self.hook.OnHooked += lambda caller, *e: self.hook.DSRHook_OnHooked()
        self.hook.OnHooked += lambda caller, *e: getattr(self, "update_version", lambda: None)()
        self.hook.Start()

    def get_version(self):
        return self.hook.Version

    def is_hooked(self):
        return self.hook.Hooked

    def can_read(self):
        return self.hook.Loaded

    def set_game_speed(self, value):
        if not self.hook.SetAnimSpeed(value):
            raise WriteMemoryError()

    def get_stat(self, stat: Stats):
        if stat == Stats.VIT:
            return self.hook.GetVitality()
        elif stat == Stats.ATN:
            return self.hook.GetAttunement()
        elif stat == Stats.END:
            return self.hook.GetEndurance()
        elif stat == Stats.STR:
            return self.hook.GetStrength()
        elif stat == Stats.DEX:
            return self.hook.GetDexterity()
        elif stat == Stats.RES:
            return self.hook.GetResistance()
        elif stat == Stats.INT:
            return self.hook.GetIntelligence()
        elif stat == Stats.FTH:
            return self.hook.GetFaith()
        elif stat == Stats.SLV:
            return self.hook.GetSoulLevel()
        elif stat == Stats.SLS:
            return self.hook.GetSouls()
        elif stat == Stats.HUM:
            return self.hook.GetHumanity()

    def update_sl(self, stat: Stats, new_val: int):
        old_val = self.get_stat(stat)
        return self.hook.SetSoulLevel(self.hook.GetSoulLevel() + (new_val - old_val))

    def set_stat(self, stat: Stats, value: int):
        if stat == Stats.VIT:
            return self.update_sl(stat, value) and self.hook.SetVitality(value)
        elif stat == Stats.ATN:
            return self.update_sl(stat, value) and self.hook.SetAttunement(value)
        elif stat == Stats.END:
            return self.update_sl(stat, value) and self.hook.SetEndurance(value)
        elif stat == Stats.STR:
            return self.update_sl(stat, value) and self.hook.SetStrength(value)
        elif stat == Stats.DEX:
            return self.update_sl(stat, value) and self.hook.SetDexterity(value)
        elif stat == Stats.RES:
            return self.update_sl(stat, value) and self.hook.SetResistance(value)
        elif stat == Stats.INT:
            return self.update_sl(stat, value) and self.hook.SetIntelligence(value)
        elif stat == Stats.FTH:
            return self.update_sl(stat, value) and self.hook.SetFaith(value)
        elif stat == Stats.SLV:
            return self.hook.SetSoulLevel(value)
        elif stat == Stats.SLS:
            return self.hook.SetSouls(value)
        elif stat == Stats.HUM:
            return self.hook.SetHumanity(value)

    def read_event_flag(self, flag_id: int):
        if not self.is_hooked():
            raise ReadMemoryError()
        return self.hook.ReadEventFlag(flag_id)

    def write_event_flag(self, flag_id: int, state: bool):
        if not self.hook.WriteEventFlag(flag_id, state):
            raise WriteMemoryError()

    def death_cam(self, enable: bool):
        if not self.hook.SetDeathCam(enable):
            raise WriteMemoryError()

    def set_super_armor(self, enable: bool):
        if not self.hook.SetPlayerSuperArmor(enable):
            raise WriteMemoryError()

    def set_no_gravity(self, enable: bool):
        if not self.hook.SetNoGravity(enable):
            raise WriteMemoryError()

    def set_no_dead(self, enable: bool):
        if not self.hook.SetPlayerNoDead(enable):
            raise WriteMemoryError()

    def set_no_stamina_consume(self, enable: bool):
        if not self.hook.SetPlayerNoStamina(enable):
            raise WriteMemoryError()

    def set_no_goods_consume(self, enable: bool):
        if not self.hook.SetPlayerNoGoods(enable):
            raise WriteMemoryError()

    def set_no_damage(self, enable: bool):
        if not self.hook.SetPlayerDisableDamage(enable):
            raise WriteMemoryError()

    def set_no_hit(self, enable: bool):
        if not self.hook.SetPlayerNoHit(enable):
            raise WriteMemoryError()

    def get_player_dead_mode(self):
        if not self.hook.GetPlayerDeadMode():
            raise WriteMemoryError()

    def set_player_dead_mode(self, enable: bool):
        if not self.hook.SetPlayerDeadMode(enable):
            raise WriteMemoryError()

    def set_no_magic_all(self, enable: bool):
        if not self.hook.SetAllNoMagicQty(enable):
            raise WriteMemoryError()

    def set_no_stamina_all(self, enable: bool):
        if not self.hook.SetAllNoStamina(enable):
            raise WriteMemoryError()

    def set_exterminate(self, enable: bool):
        if not self.hook.SetPlayerExterminate(enable):
            raise WriteMemoryError()

    def set_no_ammo_consume_all(self, enable: bool):
        if not self.hook.SetAllNoArrow(enable):
            raise WriteMemoryError()

    def set_hide(self, enable: bool):
        if not self.hook.SetPlayerHide(enable):
            raise WriteMemoryError()

    def set_silence(self, enable: bool):
        if not self.hook.SetPlayerSilence(enable):
            raise WriteMemoryError()

    def set_no_dead_all(self, enable: bool):
        if not self.hook.SetAllNoDead(enable):
            raise WriteMemoryError()

    def set_no_damage_all(self, enable: bool):
        if not self.hook.SetAllNoDamage(enable):
            raise WriteMemoryError()

    def set_no_hit_all(self, enable: bool):
        if not self.hook.SetAllNoHit(enable):
            raise WriteMemoryError()

    def set_no_attack_all(self, enable: bool):
        if not self.hook.SetAllNoAttack(enable):
            raise WriteMemoryError()

    def set_no_move_all(self, enable: bool):
        if not self.hook.SetAllNoMove(enable):
            raise WriteMemoryError()

    def set_no_update_ai_all(self, enable: bool):
        if not self.hook.SetAllNoUpdateAI(enable):
            raise WriteMemoryError()

    def get_hp(self):
        if not self.is_hooked():
            raise ReadMemoryError()
        return self.hook.GetHealth()

    def set_hp(self, value: int):
        if not self.hook.SetHealthMax(value):
            raise WriteMemoryError()

    def get_hp_max(self):
        if not self.is_hooked():
            raise ReadMemoryError()
        return self.hook.GetHealthMax()

    def get_stamina(self):
        if not self.is_hooked():
            raise ReadMemoryError()
        return self.hook.GetStaminaMax()

    def set_stamina(self, value: int):
        if not self.hook.SetStaminaMax(value):
            raise WriteMemoryError()

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

    def set_name(self, name: str):
        if not self.hook.SetName(name):
            raise WriteMemoryError()

    def set_bonfire(self, value: int):
        if not self.hook.SetLastBonfire(value):
            raise WriteMemoryError()

    def bonfire_warp(self):
        code = self.hook.BonfireWarp()
        if code != 0:
            raise AsmExecuteError(code)

    def item_get(self, item_category: int, item_id: int, item_count: int):
        code = self.hook.GetItem(item_category, item_id, item_count)
        if code != 0:
            raise AsmExecuteError(code)

    def override_filter(self, override: bool):
        self.hook.SetFilterOverride(override)

    def set_brightness(self, red: float, green: float, blue: float):
        self.hook.SetBrightness(red, green, blue)

    def set_contrast(self, red: float, green: float, blue: float):
        self.hook.SetContrast(red, green, blue)

    def set_saturation(self, value: float):
        self.hook.SetSaturation(value)

    def set_hue(self, value: float):
        self.hook.SetHue(value)

    def draw_map(self, enable: bool):
        self.hook.SetDrawMap(enable)

    def draw_objects(self, enable: bool):
        self.hook.SetDrawObjects(enable)

    def draw_creatures(self, enable: bool):
        self.hook.SetDrawCharacters(enable)

    def draw_sfx(self, enable: bool):
        self.hook.SetDrawSFX(enable)

    def draw_cutscenes(self, enable: bool):
        self.hook.SetDrawCutscenes(enable)

    def disable_all_area_enemies(self, disable: bool):
        if not self.hook.DisableAllAreaEnemies(disable):
            raise WriteMemoryError()

    def disable_all_area_event(self, disable: bool):
        if not self.hook.DisableAllAreaEvent(disable):
            raise WriteMemoryError()

    def disable_all_area_map(self, disable: bool):
        if not self.hook.DisableAllAreaMap(disable):
            raise WriteMemoryError()

    def disable_all_area_obj(self, disable: bool):
        if not self.hook.DisableAllAreaObj(disable):
            raise WriteMemoryError()

    def enable_all_area_obj(self, enable: bool):
        if not self.hook.EnableAllAreaObj(enable):
            raise WriteMemoryError()

    def enable_all_area_obj_break(self, enable: bool):
        if not self.hook.EnableAllAreaObjBreak(enable):
            raise WriteMemoryError()

    def disable_all_area_hi_hit(self, disable: bool):
        if not self.hook.DisableAllAreaHiHit(disable):
            raise WriteMemoryError()

    def disable_all_area_lo_hit(self, disable: bool):
        if not self.hook.EnableAllAreaLoHit(not disable):
            raise WriteMemoryError()

    def disable_all_area_sfx(self, disable: bool):
        if not self.hook.DisableAllAreaSfx(disable):
            raise WriteMemoryError()

    def disable_all_area_sound(self, disable: bool):
        if not self.hook.DisableAllAreaSound(disable):
            raise WriteMemoryError()

    def enable_obj_break_record_mode(self, enable: bool):
        if not self.hook.EnableObjBreakRecordMode(enable):
            raise WriteMemoryError()

    def enable_auto_map_warp_mode(self, enable: bool):
        if not self.hook.EnableAutoMapWarpMode(enable):
            raise WriteMemoryError()

    def enable_chr_npc_wander_test(self, enable: bool):
        if not self.hook.EnableChrNpcWanderTest(enable):
            raise WriteMemoryError()

    def enable_dbg_chr_all_dead(self, enable: bool):
        if not self.hook.EnableDbgChrAllDead(enable):
            raise WriteMemoryError()

    def enable_online_mode(self, enable: bool):
        if not self.hook.EnableOnlineMode(enable):
            raise WriteMemoryError()
