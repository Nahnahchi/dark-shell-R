# noinspection PyUnresolvedReferences
from dsbin.imports import DSRHook, Stats
from time import sleep
from math import pi


def wait_for(predicate, desired_state=True, single_frame=0.016):
    if not callable(predicate):
        return False
    else:
        while predicate() != desired_state:
            sleep(single_frame)
        return True


class ReadMemoryError(Exception):

    def __init__(self, message="Failed to read memory"):
        self.message = message
        super(ReadMemoryError, self).__init__(self.message)


class WriteMemoryError(Exception):

    def __init__(self, message="Failed to write memory"):
        self.message = message
        super(WriteMemoryError, self).__init__(self.message)


class AsmExecuteError(Exception):

    ERR = ({
        0x00000080: "WAIT_ABANDONED",
        0x00000102: "WAIT_TIMEOUT",
        0xFFFFFFFF: "WAIT_FAILED"
    })

    def __init__(self, code, message="Failed to execute assembly"):
        self.message = message
        self.error = AsmExecuteError.ERR[code] if code in AsmExecuteError.ERR.keys() else "REASON_UNKNOWN"
        super(AsmExecuteError, self).__init__(self.message)

    def __str__(self):
        return "%s (%s)" % (self.message, self.error)


class DSRProcess:

    def __init__(self, process_name, debug=False):
        self._hook = DSRHook(self, 5000, 5000, process_name)
        self._debug = debug
        self._hook.OnHooked += lambda caller, *e: self._hook.DSRHook_OnHooked()
        self._hook.OnHooked += lambda caller, *e: getattr(self, "update_version", lambda: None)()
        self._hook.Start()

    def get_version(self):
        return self._hook.Version

    def is_hooked(self):
        return self._hook.Hooked

    def can_read(self):
        return self._hook.Loaded

    def set_animation_speed(self, value: float):
        if not self._hook.SetAnimSpeed(value):
            raise WriteMemoryError()

    def menu_kick(self):
        self._hook.MenuKick()

    def display_banner(self, value: int):
        self._hook.DisplayBanner(value)

    def game_restart(self):
        return self._hook.GameRestart()

    def get_stat(self, stat: Stats):
        if stat == Stats.VIT:
            return self._hook.GetVitality()
        elif stat == Stats.ATN:
            return self._hook.GetAttunement()
        elif stat == Stats.END:
            return self._hook.GetEndurance()
        elif stat == Stats.STR:
            return self._hook.GetStrength()
        elif stat == Stats.DEX:
            return self._hook.GetDexterity()
        elif stat == Stats.RES:
            return self._hook.GetResistance()
        elif stat == Stats.INT:
            return self._hook.GetIntelligence()
        elif stat == Stats.FTH:
            return self._hook.GetFaith()
        elif stat == Stats.LVL:
            return self._hook.GetSoulLevel()
        elif stat == Stats.SLS:
            return self._hook.GetSouls()
        elif stat == Stats.HUM:
            return self._hook.GetHumanity()

    def update_sl(self, stat: Stats, new_val: int):
        old_val = self.get_stat(stat)
        return self._hook.SetSoulLevel(self._hook.GetSoulLevel() + (new_val - old_val))

    def set_stat(self, stat: Stats, value: int):
        if stat == Stats.VIT:
            return self.update_sl(stat, value) and self._hook.SetVitality(value)
        elif stat == Stats.ATN:
            return self.update_sl(stat, value) and self._hook.SetAttunement(value)
        elif stat == Stats.END:
            return self.update_sl(stat, value) and self._hook.SetEndurance(value)
        elif stat == Stats.STR:
            return self.update_sl(stat, value) and self._hook.SetStrength(value)
        elif stat == Stats.DEX:
            return self.update_sl(stat, value) and self._hook.SetDexterity(value)
        elif stat == Stats.RES:
            return self.update_sl(stat, value) and self._hook.SetResistance(value)
        elif stat == Stats.INT:
            return self.update_sl(stat, value) and self._hook.SetIntelligence(value)
        elif stat == Stats.FTH:
            return self.update_sl(stat, value) and self._hook.SetFaith(value)
        elif stat == Stats.LVL:
            return self._hook.SetSoulLevel(value)
        elif stat == Stats.SLS:
            return self._hook.SetSouls(value)
        elif stat == Stats.HUM:
            return self._hook.SetHumanity(value)

    def read_event_flag(self, flag_id: int):
        if not self.can_read() or not self.is_hooked():
            return None
        return self._hook.ReadEventFlag(flag_id)

    def write_event_flag(self, flag_id: int, state: bool):
        if not self._hook.WriteEventFlag(flag_id, state):
            raise WriteMemoryError()

    def listen_for_flag(self, flag_id, flag_state):
        return wait_for(lambda: self.read_event_flag(flag_id), desired_state=flag_state)

    def death_cam(self, enable: bool):
        if not self._hook.SetDeathCam(enable):
            raise WriteMemoryError()

    def set_super_armor(self, enable: bool):
        if not self._hook.SetPlayerSuperArmor(enable):
            raise WriteMemoryError()

    def set_no_gravity(self, enable: bool):
        if not self._hook.SetNoGravity(enable):
            raise WriteMemoryError()

    def set_no_dead(self, enable: bool):
        if not self._hook.SetPlayerNoDead(enable):
            raise WriteMemoryError()

    def set_no_stamina_consume(self, enable: bool):
        if not self._hook.SetPlayerNoStamina(enable):
            raise WriteMemoryError()

    def set_no_goods_consume(self, enable: bool):
        if not self._hook.SetPlayerNoGoods(enable):
            raise WriteMemoryError()

    def set_no_damage(self, enable: bool):
        if not self._hook.SetPlayerDisableDamage(enable):
            raise WriteMemoryError()

    def set_no_hit(self, enable: bool):
        if not self._hook.SetPlayerNoHit(enable):
            raise WriteMemoryError()

    def get_player_dead_mode(self):
        if not self._hook.GetPlayerDeadMode():
            raise WriteMemoryError()

    def set_player_dead_mode(self, enable: bool):
        if not self._hook.SetPlayerDeadMode(enable):
            raise WriteMemoryError()

    def set_no_magic_all(self, enable: bool):
        if not self._hook.SetAllNoMagicQty(enable):
            raise WriteMemoryError()

    def set_no_stamina_all(self, enable: bool):
        if not self._hook.SetAllNoStamina(enable):
            raise WriteMemoryError()

    def set_exterminate(self, enable: bool):
        if not self._hook.SetPlayerExterminate(enable):
            raise WriteMemoryError()

    def set_no_ammo_consume_all(self, enable: bool):
        if not self._hook.SetAllNoArrow(enable):
            raise WriteMemoryError()

    def set_hide(self, enable: bool):
        if not self._hook.SetPlayerHide(enable):
            raise WriteMemoryError()

    def set_silence(self, enable: bool):
        if not self._hook.SetPlayerSilence(enable):
            raise WriteMemoryError()

    def set_no_dead_all(self, enable: bool):
        if not self._hook.SetAllNoDead(enable):
            raise WriteMemoryError()

    def set_no_damage_all(self, enable: bool):
        if not self._hook.SetAllNoDamage(enable):
            raise WriteMemoryError()

    def set_no_hit_all(self, enable: bool):
        if not self._hook.SetAllNoHit(enable):
            raise WriteMemoryError()

    def set_no_attack_all(self, enable: bool):
        if not self._hook.SetAllNoAttack(enable):
            raise WriteMemoryError()

    def set_no_move_all(self, enable: bool):
        if not self._hook.SetAllNoMove(enable):
            raise WriteMemoryError()

    def set_no_update_ai_all(self, enable: bool):
        if not self._hook.SetAllNoUpdateAI(enable):
            raise WriteMemoryError()

    def get_hp(self):
        if not self.is_hooked():
            raise ReadMemoryError()
        return self._hook.GetHealth()

    def set_hp(self, value: int):
        if not self._hook.SetHealthMax(value):
            raise WriteMemoryError()

    def get_hp_max(self):
        if not self.is_hooked():
            raise ReadMemoryError()
        return self._hook.GetHealthMax()

    def get_stamina(self):
        if not self.is_hooked():
            raise ReadMemoryError()
        return self._hook.GetStaminaMax()

    def set_stamina(self, value: int):
        if not self._hook.SetStaminaMax(value):
            raise WriteMemoryError()

    def get_pos(self):
        return (
            self._hook.GetPositionX(),
            self._hook.GetPositionY(),
            self._hook.GetPositionZ(),
            (self._hook.GetPositionAngle() + pi) / (pi * 2) * 360
        )

    def get_pos_stable(self):
        return (
            self._hook.GetStablePositionX(),
            self._hook.GetStablePositionY(),
            self._hook.GetStablePositionZ(),
            (self._hook.GetStablePositionAngle() + pi) / (pi * 2) * 360
        )

    def jump_pos(self, x, y, z, a):
        self._hook.PosWarp(x, y, z, a / 360 * 2 * pi - pi)

    def set_name(self, name: str):
        if not self._hook.SetName(name):
            raise WriteMemoryError()

    def set_team_type(self, value: int):
        if not self._hook.SetTeamType(value):
            raise WriteMemoryError()

    def set_phantom_type(self, value: int):
        if not self._hook.SetChrType(value):
            raise WriteMemoryError()

    def set_ng_mode(self, value: int):
        if not self._hook.SetNewGameType(value):
            raise WriteMemoryError()

    def get_last_animation(self):
        if not self.is_hooked():
            raise ReadMemoryError()
        if not self.can_read():
            return -1
        return self._hook.GetLastAnimation()

    def set_bonfire(self, value: int):
        if not self._hook.SetLastBonfire(value):
            raise WriteMemoryError()

    def bonfire_warp(self):
        code = self._hook.BonfireWarp()
        if code != 0:
            raise AsmExecuteError(code)

    def item_get(self, item_category: int, item_id: int, item_count: int):
        code = self._hook.GetItem(item_category, item_id, item_count)
        if code != 0:
            raise AsmExecuteError(code)

    def override_filter(self, override: bool):
        self._hook.SetFilterOverride(override)

    def set_brightness(self, red: float, green: float, blue: float):
        self._hook.SetBrightness(red, green, blue)

    def set_contrast(self, red: float, green: float, blue: float):
        self._hook.SetContrast(red, green, blue)

    def set_saturation(self, value: float):
        self._hook.SetSaturation(value)

    def set_hue(self, value: float):
        self._hook.SetHue(value)

    def draw_map(self, enable: bool):
        self._hook.SetDrawMap(enable)

    def draw_objects(self, enable: bool):
        self._hook.SetDrawObjects(enable)

    def draw_creatures(self, enable: bool):
        self._hook.SetDrawCharacters(enable)

    def draw_sfx(self, enable: bool):
        self._hook.SetDrawSFX(enable)

    def draw_cutscenes(self, enable: bool):
        self._hook.SetDrawCutscenes(enable)

    def disable_all_area_enemies(self, disable: bool):
        if not self._hook.DisableAllAreaEnemies(disable):
            raise WriteMemoryError()

    def disable_all_area_event(self, disable: bool):
        if not self._hook.DisableAllAreaEvent(disable):
            raise WriteMemoryError()

    def disable_all_area_map(self, disable: bool):
        if not self._hook.DisableAllAreaMap(disable):
            raise WriteMemoryError()

    def disable_all_area_obj(self, disable: bool):
        if not self._hook.DisableAllAreaObj(disable):
            raise WriteMemoryError()

    def enable_all_area_obj(self, enable: bool):
        if not self._hook.EnableAllAreaObj(enable):
            raise WriteMemoryError()

    def enable_all_area_obj_break(self, enable: bool):
        if not self._hook.EnableAllAreaObjBreak(enable):
            raise WriteMemoryError()

    def disable_all_area_hi_hit(self, disable: bool):
        if not self._hook.DisableAllAreaHiHit(disable):
            raise WriteMemoryError()

    def disable_all_area_lo_hit(self, disable: bool):
        if not self._hook.EnableAllAreaLoHit(not disable):
            raise WriteMemoryError()

    def disable_all_area_sfx(self, disable: bool):
        if not self._hook.DisableAllAreaSfx(disable):
            raise WriteMemoryError()

    def disable_all_area_sound(self, disable: bool):
        if not self._hook.DisableAllAreaSound(disable):
            raise WriteMemoryError()

    def enable_obj_break_record_mode(self, enable: bool):
        if not self._hook.EnableObjBreakRecordMode(enable):
            raise WriteMemoryError()

    def enable_auto_map_warp_mode(self, enable: bool):
        if not self._hook.EnableAutoMapWarpMode(enable):
            raise WriteMemoryError()

    def enable_chr_npc_wander_test(self, enable: bool):
        if not self._hook.EnableChrNpcWanderTest(enable):
            raise WriteMemoryError()

    def enable_dbg_chr_all_dead(self, enable: bool):
        if not self._hook.EnableDbgChrAllDead(enable):
            raise WriteMemoryError()

    def enable_online_mode(self, enable: bool):
        if not self._hook.EnableOnlineMode(enable):
            raise WriteMemoryError()
