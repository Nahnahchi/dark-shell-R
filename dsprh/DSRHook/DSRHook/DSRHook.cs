using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using static System.Text.Encoding;
using System.Threading;
using PropertyHookCustom;
using System.Text;

namespace DarkShellRemastered
{
    public class DSRHook : PHook
    {
        private DSROffsets Offsets;

        private PHPointer GroupMaskAddr;
        private PHPointer ChrDbgAddr;
        private PHPointer ChrClassBasePtr;
        private PHPointer ItemGetAddr;
        private PHPointer BonfireWarpAddr;

        private PHPointer CamMan;
        private PHPointer ChrClassWarp;
        private PHPointer ChrFollowCam;
        private PHPointer WorldChrBase;
        private PHPointer ChrData1;
        private PHPointer ChrMapData;
        private PHPointer ChrAnimData;
        private PHPointer ChrPosData;
        private PHPointer ChrData2;
        private PHPointer GraphicsData;
        private PHPointer MenuMan;
        private PHPointer EventFlags;
        public PHPointer GameMan;


        enum Stats: int
        {
            VIT = 0,
            ATT = 1,
            END = 2,
            STR = 3,
            DEX = 4,
            RES = 5,
            INT = 6,
            FTH = 7,
            HUM = 8,
            LVL = 9,
            SLS = 10
        }

        public DSRHook(object caller, int refreshInterval, int minLifetime, string procesName) : base(caller, refreshInterval, minLifetime, p => p.MainWindowTitle == procesName)
        {
            Offsets = new DSROffsets();
            CamMan = RegisterRelativeAOB(DSROffsets.CamManBaseAOB, 3, 7, DSROffsets.CamManOffset);
            ChrFollowCam = RegisterRelativeAOB(DSROffsets.ChrFollowCamAOB, 3, 7, DSROffsets.ChrFollowCamOffset1, DSROffsets.ChrFollowCamOffset2, DSROffsets.ChrFollowCamOffset3);
            GroupMaskAddr = RegisterRelativeAOB(DSROffsets.GroupMaskAOB, 2, 7);
            GraphicsData = RegisterRelativeAOB(DSROffsets.GraphicsDataAOB, 3, 7, DSROffsets.GraphicsDataOffset1, DSROffsets.GraphicsDataOffset2);
            ChrClassWarp = RegisterRelativeAOB(DSROffsets.ChrClassWarpAOB, 3, 7, DSROffsets.ChrClassWarpOffset1);
            WorldChrBase = RegisterRelativeAOB(DSROffsets.WorldChrBaseAOB, 3, 7, DSROffsets.WorldChrBaseOffset1);
            ChrDbgAddr = RegisterRelativeAOB(DSROffsets.ChrDbgAOB, 2, 7);
            MenuMan = RegisterRelativeAOB(DSROffsets.MenuManAOB, 3, 7, DSROffsets.MenuManOffset1);
            ChrClassBasePtr = RegisterRelativeAOB(DSROffsets.ChrClassBaseAOB, 3, 7);
            EventFlags = RegisterRelativeAOB(DSROffsets.EventFlagsAOB, 3, 7, DSROffsets.EventFlagsOffset1, DSROffsets.EventFlagsOffset2);
            ItemGetAddr = RegisterAbsoluteAOB(DSROffsets.ItemGetAOB);
            BonfireWarpAddr = RegisterAbsoluteAOB(DSROffsets.BonfireWarpAOB);

            GameMan = CreateBasePointer((IntPtr)DSROffsets.GameManPtr, 0);
            ChrData1 = CreateChildPointer(WorldChrBase, (int)DSROffsets.WorldChrBase.ChrData1);
            ChrMapData = CreateBasePointer(IntPtr.Zero);
            ChrAnimData = CreateBasePointer(IntPtr.Zero);
            ChrPosData = CreateBasePointer(IntPtr.Zero);
            ChrData2 = CreateChildPointer(ChrClassBasePtr, DSROffsets.ChrData2Offset1, DSROffsets.ChrData2Offset2);
            
        }
        
        public void DSRHook_OnHooked()
        {
            Offsets = DSROffsets.GetOffsets(Process.MainModule.ModuleMemorySize);
            ChrMapData = CreateChildPointer(ChrData1, (int)DSROffsets.ChrData1.ChrMapData + Offsets.ChrData1Boost1);
            ChrAnimData = CreateChildPointer(ChrMapData, (int)DSROffsets.ChrMapData.ChrAnimData);
            ChrPosData = CreateChildPointer(ChrMapData, (int)DSROffsets.ChrMapData.ChrPosData);
        }

        private static readonly Dictionary<int, string> VersionStrings = new Dictionary<int, string>
        {
            [0x4869400] = "1.01",
            [0x496BE00] = "1.01.1",
            [0x37CB400] = "1.01.2",
            [0x3817800] = "1.03",
        };

        public string Version
        {
            get
            {
                if (Hooked)
                {
                    int size = Process.MainModule.ModuleMemorySize;
                    if (VersionStrings.TryGetValue(size, out string version))
                        return version;
                    else
                        return $"0x{size:X8}";
                }
                else
                {
                    return "N/A";
                }
            }
        }

        public bool Loaded => ChrPosData.Resolve() != IntPtr.Zero;

        #region Game Man
        public bool DisableAllAreaEnemies(bool value)
        {
            return GameMan.WriteBoolean((int)DSROffsets.GameMan.IsDisableAllAreaEnemies, value);
        }

        public bool DisableAllAreaEvent(bool value)
        {
            return GameMan.WriteBoolean((int)DSROffsets.GameMan.IsDisableAllAreaEvent, value);
        }

        public bool DisableAllAreaMap(bool value)
        {
            return GameMan.WriteBoolean((int)DSROffsets.GameMan.IsDisableAllAreaMap, value);
        }

        public bool DisableAllAreaObj(bool value)
        {
            return GameMan.WriteBoolean((int)DSROffsets.GameMan.IsDisableAllAreaObj, value);
        }

        public bool EnableAllAreaObj(bool value)
        {
            return GameMan.WriteBoolean((int)DSROffsets.GameMan.IsEnableAllAreaObj, value);
        }

        public bool EnableAllAreaObjBreak(bool value)
        {
            return GameMan.WriteBoolean((int)DSROffsets.GameMan.IsEnableAllAreaObjBreak, value);
        }

        public bool DisableAllAreaHiHit(bool value)
        {
            return GameMan.WriteBoolean((int)DSROffsets.GameMan.IsDisableAllAreaHiHit, value);
        }

        public bool EnableAllAreaLoHit(bool value)
        {
            return GameMan.WriteBoolean((int)DSROffsets.GameMan.IsEnableAllAreaLoHit, value);
        }

        public bool DisableAllAreaSfx(bool value)
        {
            return GameMan.WriteBoolean((int)DSROffsets.GameMan.IsDisableAllAreaSfx, value);
        }

        public bool DisableAllAreaSound(bool value)
        {
            return GameMan.WriteBoolean((int)DSROffsets.GameMan.IsDisableAllAreaSound, value);

        }

        public bool EnableObjBreakRecordMode(bool value)
        {
            return GameMan.WriteBoolean((int)DSROffsets.GameMan.IsObjBreakRecordMode, value);
        }

        public bool EnableAutoMapWarpMode(bool value)
        {
            return GameMan.WriteBoolean((int)DSROffsets.GameMan.IsAuthoMapWarpMode, value);
        }

        public bool EnableChrNpcWanderTest(bool value)
        {
            return GameMan.WriteBoolean((int)DSROffsets.GameMan.IsChrNpCWanderTest, value);
        }

        public bool EnableDbgChrAllDead(bool value)
        {
            return GameMan.WriteBoolean((int)DSROffsets.GameMan.IsDisableAllAreaEnemies, value);
        }

        public bool EnableOnlineMode(bool value)
        {
            return GameMan.WriteBoolean((int)DSROffsets.GameMan.IsOnlineMode, value);
        }

        public bool GameRestart()
        {
            return GameMan.WriteInt32((int)DSROffsets.GameMan.bRequestToEnding, 1);
        }
        #endregion

        #region Player
        public uint LevelUp(int[] values) // Crashes the game
        {
            IntPtr stats = Kernel32.VirtualAllocEx(Handle, IntPtr.Zero, (IntPtr)0x300, 0x1000 | 0x2000, 0x4);

            Kernel32.WriteInt32(Handle, stats + 0x268 + 0x0, values[(int)Stats.VIT]);
            Kernel32.WriteInt32(Handle, stats + 0x268 + 0x4, values[(int)Stats.ATT]);
            Kernel32.WriteInt32(Handle, stats + 0x268 + 0x8, values[(int)Stats.END]);
            Kernel32.WriteInt32(Handle, stats + 0x268 + 0xC, values[(int)Stats.STR]);
            Kernel32.WriteInt32(Handle, stats + 0x268 + 0x10, values[(int)Stats.DEX]);
            Kernel32.WriteInt32(Handle, stats + 0x268 + 0x14, values[(int)Stats.RES]);
            Kernel32.WriteInt32(Handle, stats + 0x268 + 0x18, values[(int)Stats.INT]);
            Kernel32.WriteInt32(Handle, stats + 0x268 + 0x1C, values[(int)Stats.FTH]);
            Kernel32.WriteInt32(Handle, stats + 0x268 + 0x20, values[(int)Stats.HUM]);
            Kernel32.WriteInt32(Handle, stats + 0x268 + 0x24, values[(int)Stats.LVL]);
            Kernel32.WriteInt32(Handle, stats + 0x268 + 0x28, 0);
            Kernel32.WriteInt32(Handle, stats + 0x268 + 0x2C, 0);
            Kernel32.WriteInt32(Handle, stats + 0x268 + 0x30, values[(int)Stats.SLS]);
            
            byte[] asm = (byte[])DSRAssembly.LevelUp.Clone();
            byte[] bytes = BitConverter.GetBytes(stats.ToInt64() + 0x268);
            
            Array.Copy(bytes, 0, asm, 0x2, 8);
            bytes = BitConverter.GetBytes(stats.ToInt64());
            Array.Copy(bytes, 0, asm, 0xC, 8);
            
            uint success = Execute(asm);
            Kernel32.VirtualFreeEx(Handle, stats, IntPtr.Zero, 0x8000);
            return success;
        }

        public bool SetName(string value)
        {
            return ChrData2.WriteString((int)DSROffsets.ChrData2.ChrNameStr1, Encoding.Unicode, 64, value) &&
                   ChrData2.WriteString((int)DSROffsets.ChrData2.ChrNameStr2, Encoding.Unicode, 64, value);
        }

        public int GetHealth()
        {
            return ChrData1.ReadInt32((int)DSROffsets.ChrData1.Health + Offsets.ChrData1Boost2); 
        }

        public bool SetHealth(int value)
        {
            return ChrData1.WriteInt32((int)DSROffsets.ChrData1.Health + Offsets.ChrData1Boost2, value);
        }

        public int GetHealthMax()
        {
            return ChrData1.ReadInt32((int)DSROffsets.ChrData1.MaxHealth + Offsets.ChrData1Boost2);
        }

        public bool SetHealthMax(int value)
        {
            return ChrData1.WriteInt32((int)DSROffsets.ChrData1.MaxHealth + Offsets.ChrData1Boost2, value);
        }

        public int GetStamina()
        {
            return ChrData1.ReadInt32((int)DSROffsets.ChrData1.Stamina + Offsets.ChrData1Boost2);
        }

        public bool SetStamina(int value)
        {
            return ChrData1.WriteInt32((int)DSROffsets.ChrData1.Stamina + Offsets.ChrData1Boost2, value);
        }

        public int GetStaminaMax()
        {
            return ChrData1.ReadInt32((int)DSROffsets.ChrData1.MaxStamina + Offsets.ChrData1Boost2);
        }

        public bool SetStaminaMax(int value)
        {
            return ChrData1.WriteInt32((int)DSROffsets.ChrData1.MaxStamina + Offsets.ChrData1Boost2, value);
        }

        public float GetPositionX()
        {
            return ChrPosData.ReadSingle((int)DSROffsets.ChrPosData.PosX);
        }

        public float GetPositionY()
        {
            return ChrPosData.ReadSingle((int)DSROffsets.ChrPosData.PosY);
        }

        public float GetPositionZ()
        {
            return ChrPosData.ReadSingle((int)DSROffsets.ChrPosData.PosZ);
        }

        public float GetPositionAngle()
        {
            return ChrPosData.ReadSingle((int)DSROffsets.ChrPosData.PosAngle);
        }

        public float GetStablePositionX()
        {
            return ChrClassWarp.ReadSingle((int)DSROffsets.ChrClassWarp.StableX + Offsets.ChrClassWarpBoost);
        }

        public float GetStablePositionY()
        {
            return ChrClassWarp.ReadSingle((int)DSROffsets.ChrClassWarp.StableY + Offsets.ChrClassWarpBoost);
        }

        public float GetStablePositionZ()
        {
            return ChrClassWarp.ReadSingle((int)DSROffsets.ChrClassWarp.StableZ + Offsets.ChrClassWarpBoost);
        }

        public float GetStablePositionAngle()
        {
            return ChrClassWarp.ReadSingle((int)DSROffsets.ChrClassWarp.StableAngle + Offsets.ChrClassWarpBoost);
        }

        public void PosWarp(float x, float y, float z, float angle)
        {
            ChrMapData.WriteSingle((int)DSROffsets.ChrMapData.WarpX, x);
            ChrMapData.WriteSingle((int)DSROffsets.ChrMapData.WarpY, y);
            ChrMapData.WriteSingle((int)DSROffsets.ChrMapData.WarpZ, z);
            ChrMapData.WriteSingle((int)DSROffsets.ChrMapData.WarpAngle, angle);
            ChrMapData.WriteBoolean((int)DSROffsets.ChrMapData.Warp, true);
        }

        public bool SetNoGravity(bool value)
        {
            return ChrData1.WriteFlag32((int)DSROffsets.ChrData1.ChrFlags1 + Offsets.ChrData1Boost1, (uint)DSROffsets.ChrFlags1.NoGravity, value);
        }

        public bool SetNoCollision(bool value)
        {
            return ChrMapData.WriteFlag32((int)DSROffsets.ChrMapData.ChrMapFlags, (uint)DSROffsets.ChrMapFlags.DisableMapHit, value);
        }

        public bool GetDeathCam()
        {
            return WorldChrBase.ReadBoolean((int)DSROffsets.WorldChrBase.DeathCam);
        }

        public bool SetDeathCam(bool value)
        {
            return WorldChrBase.WriteBoolean((int)DSROffsets.WorldChrBase.DeathCam, value);
        }

        public int GetLastBonfire()
        {
            return ChrClassWarp.ReadInt32((int)DSROffsets.ChrClassWarp.LastBonfire + Offsets.ChrClassWarpBoost);
        }

        public bool SetLastBonfire(int value)
        {
            return ChrClassWarp.WriteInt32((int)DSROffsets.ChrClassWarp.LastBonfire + Offsets.ChrClassWarpBoost, value);
        }

        public uint BonfireWarp()
        {
            byte[] asm = (byte[])DSRAssembly.BonfireWarp.Clone();
            byte[] bytes = BitConverter.GetBytes(ChrClassBasePtr.Resolve().ToInt64());
            Array.Copy(bytes, 0, asm, 0x2, 8);
            bytes = BitConverter.GetBytes(BonfireWarpAddr.Resolve().ToInt64());
            Array.Copy(bytes, 0, asm, 0x18, 8);
            return Execute(asm);
        }

        public bool SetAnimSpeed(float value)
        {
            return ChrAnimData.WriteSingle((int)DSROffsets.ChrAnimData.AnimSpeed, value);
        }

        public byte[] DumpFollowCam()
        {
            return ChrFollowCam.ReadBytes(0, 512);
        }

        public void UndumpFollowCam(byte[] value)
        {
            ChrFollowCam.WriteBytes(0, value);
        }
        #endregion

        #region Stats
        public byte GetClass()
        {
            return ChrData2.ReadByte((int)DSROffsets.ChrData2.Class);
        }

        public bool SetClass(byte value)
        {
            return ChrData2.WriteByte((int)DSROffsets.ChrData2.Class, value);
        }

        public int GetHumanity()
        {
            return ChrData2.ReadInt32((int)DSROffsets.ChrData2.Humanity);
        }

        public bool SetHumanity(int value)
        {
            return ChrData2.WriteInt32((int)DSROffsets.ChrData2.Humanity, value);
        }

        public int GetSouls()
        {
            return ChrData2.ReadInt32((int)DSROffsets.ChrData2.Souls);
        }

        public bool SetSouls(int value)
        {
            return ChrData2.WriteInt32((int)DSROffsets.ChrData2.Souls, value);
        }

        public int GetSoulLevel()
        {
            return ChrData2.ReadInt32((int)DSROffsets.ChrData2.SoulLevel);
        }

        public bool SetSoulLevel(int value)
        {
            return ChrData2.WriteInt32((int)DSROffsets.ChrData2.SoulLevel, value);
        }

        public int GetVitality()
        {
            return ChrData2.ReadInt32((int)DSROffsets.ChrData2.Vitality);
        }

        public bool SetVitality(int value)
        {
            return ChrData2.WriteInt32((int)DSROffsets.ChrData2.Vitality, value);
        }

        public int GetAttunement()
        {
            return ChrData2.ReadInt32((int)DSROffsets.ChrData2.Attunement);
        }

        public bool SetAttunement(int value)
        {
            return ChrData2.WriteInt32((int)DSROffsets.ChrData2.Attunement, value);
        }

        public int GetEndurance()
        {
            return ChrData2.ReadInt32((int)DSROffsets.ChrData2.Endurance);
        }

        public bool SetEndurance(int value)
        {
            return ChrData2.WriteInt32((int)DSROffsets.ChrData2.Endurance, value);
        }

        public int GetStrength()
        {
            return ChrData2.ReadInt32((int)DSROffsets.ChrData2.Strength);
        }
        public bool SetStrength(int value)
        {
            return ChrData2.WriteInt32((int)DSROffsets.ChrData2.Strength, value);
        }

        public int GetDexterity()
        {
            return ChrData2.ReadInt32((int)DSROffsets.ChrData2.Dexterity);
        }
        public bool SetDexterity(int value)
        {
            return ChrData2.WriteInt32((int)DSROffsets.ChrData2.Dexterity, value);
        }

        public int GetResistance()
        {
            return ChrData2.ReadInt32((int)DSROffsets.ChrData2.Resistance);
        }

        public bool SetResistance(int value)
        {
            return ChrData2.WriteInt32((int)DSROffsets.ChrData2.Resistance, value);
        }

        public int GetIntelligence()
        {
            return ChrData2.ReadInt32((int)DSROffsets.ChrData2.Intelligence);
        }

        public bool SetIntelligence(int value)
        {
            return ChrData2.WriteInt32((int)DSROffsets.ChrData2.Intelligence, value);
        }

        public int GetFaith()
        {
            return ChrData2.ReadInt32((int)DSROffsets.ChrData2.Faith);
        }

        public bool SetFaith(int value)
        {
            return ChrData2.WriteInt32((int)DSROffsets.ChrData2.Faith, value);
        }
        #endregion

        #region Items
        public uint GetItem(int category, int id, int quantity)
        {
            byte[] asm = (byte[])DSRAssembly.GetItem.Clone();

            byte[] bytes = BitConverter.GetBytes(category);
            Array.Copy(bytes, 0, asm, 0x1, 4);
            bytes = BitConverter.GetBytes(quantity);
            Array.Copy(bytes, 0, asm, 0x7, 4);
            bytes = BitConverter.GetBytes(id);
            Array.Copy(bytes, 0, asm, 0xD, 4);
            bytes = BitConverter.GetBytes((ulong)ChrClassBasePtr.Resolve());
            Array.Copy(bytes, 0, asm, 0x19, 8);
            bytes = BitConverter.GetBytes((ulong)ItemGetAddr.Resolve());
            Array.Copy(bytes, 0, asm, 0x46, 8);

            return Execute(asm);
        }
        #endregion

        #region Cheats
        public bool GetPlayerDeadMode()
        {
            return ChrData1.ReadFlag32((int)DSROffsets.ChrData1.ChrFlags1 + Offsets.ChrData1Boost1, (uint)DSROffsets.ChrFlags1.SetDeadMode);
        }

        public bool SetPlayerDeadMode(bool value)
        {
            return ChrData1.WriteFlag32((int)DSROffsets.ChrData1.ChrFlags1 + Offsets.ChrData1Boost1, (uint)DSROffsets.ChrFlags1.SetDeadMode, value);
        }

        public bool SetPlayerNoDead(bool value)
        {
            return ChrDbgAddr.WriteBoolean((int)DSROffsets.ChrDbg.PlayerNoDead, value);
        }

        public bool SetPlayerDisableDamage(bool value)
        {
            return ChrData1.WriteFlag32((int)DSROffsets.ChrData1.ChrFlags1 + Offsets.ChrData1Boost1, (uint)DSROffsets.ChrFlags1.DisableDamage, value);
        }

        public bool SetPlayerNoHit(bool value)
        {
            return ChrData1.WriteFlag32((int)DSROffsets.ChrData1.ChrFlags2 + Offsets.ChrData1Boost2, (uint)DSROffsets.ChrFlags2.NoHit, value);
        }

        public bool SetPlayerNoStamina(bool value)
        {
            return ChrData1.WriteFlag32((int)DSROffsets.ChrData1.ChrFlags2 + Offsets.ChrData1Boost2, (uint)DSROffsets.ChrFlags2.NoStaminaConsumption, value);
        }

        public bool SetPlayerSuperArmor(bool value)
        {
            return ChrData1.WriteFlag32((int)DSROffsets.ChrData1.ChrFlags1 + Offsets.ChrData1Boost1, (uint)DSROffsets.ChrFlags1.SetSuperArmor, value);
        }

        public bool SetPlayerHide(bool value)
        {
            return ChrDbgAddr.WriteBoolean((int)DSROffsets.ChrDbg.PlayerHide, value);
        }

        public bool SetPlayerSilence(bool value)
        {
            return ChrDbgAddr.WriteBoolean((int)DSROffsets.ChrDbg.PlayerSilence, value);
        }

        public bool SetPlayerExterminate(bool value)
        {
            return ChrDbgAddr.WriteBoolean((int)DSROffsets.ChrDbg.PlayerExterminate, value);
        }

        public bool SetPlayerNoGoods(bool value)
        {
            return ChrData1.WriteFlag32((int)DSROffsets.ChrData1.ChrFlags2 + Offsets.ChrData1Boost2, (uint)DSROffsets.ChrFlags2.NoGoodsConsume, value);
        }

        public bool SetAllNoArrow(bool value)
        {
            return ChrDbgAddr.WriteBoolean((int)DSROffsets.ChrDbg.AllNoArrowConsume, value);
        }

        public bool SetAllNoMagicQty(bool value)
        {
            return ChrDbgAddr.WriteBoolean((int)DSROffsets.ChrDbg.AllNoMagicQtyConsume, value);
        }

        public bool SetAllNoDead(bool value)
        {
            return ChrDbgAddr.WriteBoolean((int)DSROffsets.ChrDbg.AllNoDead, value);
        }

        public bool SetAllNoDamage(bool value)
        {
            return ChrDbgAddr.WriteBoolean((int)DSROffsets.ChrDbg.AllNoDamage, value);
        }

        public bool SetAllNoHit(bool value)
        {
            return ChrDbgAddr.WriteBoolean((int)DSROffsets.ChrDbg.AllNoHit, value);
        }

        public bool SetAllNoStamina(bool value)
        {
            return ChrDbgAddr.WriteBoolean((int)DSROffsets.ChrDbg.AllNoStaminaConsume, value);
        }

        public bool SetAllNoAttack(bool value)
        {
            return ChrDbgAddr.WriteBoolean((int)DSROffsets.ChrDbg.AllNoAttack, value);
        }

        public bool SetAllNoMove(bool value)
        {
            return ChrDbgAddr.WriteBoolean((int)DSROffsets.ChrDbg.AllNoMove, value);
        }

        public bool SetAllNoUpdateAI(bool value)
        {
            return ChrDbgAddr.WriteBoolean((int)DSROffsets.ChrDbg.AllNoUpdateAI, value);
        }
        #endregion

        #region Graphics
        public bool SetDrawMap(bool value)
        {
            return GroupMaskAddr.WriteBoolean((int)DSROffsets.GroupMask.Map, value);
        }

        public bool SetDrawObjects(bool value)
        {
            return GroupMaskAddr.WriteBoolean((int)DSROffsets.GroupMask.Objects, value);
        }

        public bool SetDrawCharacters(bool value)
        {
            return GroupMaskAddr.WriteBoolean((int)DSROffsets.GroupMask.Characters, value);
        }

        public bool SetDrawSFX(bool value)
        {
            return GroupMaskAddr.WriteBoolean((int)DSROffsets.GroupMask.SFX, value);
        }

        public bool SetDrawCutscenes(bool value)
        {
            return GroupMaskAddr.WriteBoolean((int)DSROffsets.GroupMask.Cutscenes, value);
        }

        public bool SetFilterOverride(bool value)
        {
            return GraphicsData.WriteBoolean((int)DSROffsets.GraphicsData.FilterOverride, value);
        }

        public void SetBrightness(float brightR, float brightG, float brightB)
        {
            GraphicsData.WriteSingle((int)DSROffsets.GraphicsData.FilterBrightnessR, brightR);
            GraphicsData.WriteSingle((int)DSROffsets.GraphicsData.FilterBrightnessG, brightG);
            GraphicsData.WriteSingle((int)DSROffsets.GraphicsData.FilterBrightnessB, brightB);
        }

        public void SetContrast(float contR, float contG, float contB)
        {
            GraphicsData.WriteSingle((int)DSROffsets.GraphicsData.FilterContrastR, contR);
            GraphicsData.WriteSingle((int)DSROffsets.GraphicsData.FilterContrastG, contG);
            GraphicsData.WriteSingle((int)DSROffsets.GraphicsData.FilterContrastB, contB);
        }
        
        public void SetSaturation(float saturation)
        {
            GraphicsData.WriteSingle((int)DSROffsets.GraphicsData.FilterSaturation, saturation);
        }

        public void SetHue(float hue)
        {
            GraphicsData.WriteSingle((int)DSROffsets.GraphicsData.FilterHue, hue);
        }
        #endregion

        #region Misc
        private static Dictionary<string, int> eventFlagGroups = new Dictionary<string, int>()
        {
            {"0", 0x00000},
            {"1", 0x00500},
            {"5", 0x05F00},
            {"6", 0x0B900},
            {"7", 0x11300},
        };

        private static Dictionary<string, int> eventFlagAreas = new Dictionary<string, int>()
        {
            {"000", 00},
            {"100", 01},
            {"101", 02},
            {"102", 03},
            {"110", 04},
            {"120", 05},
            {"121", 06},
            {"130", 07},
            {"131", 08},
            {"132", 09},
            {"140", 10},
            {"141", 11},
            {"150", 12},
            {"151", 13},
            {"160", 14},
            {"170", 15},
            {"180", 16},
            {"181", 17},
        };

        private int getEventFlagOffset(int ID, out uint mask)
        {
            string idString = ID.ToString("D8");
            if (idString.Length == 8)
            {
                string group = idString.Substring(0, 1);
                string area = idString.Substring(1, 3);
                int section = Int32.Parse(idString.Substring(4, 1));
                int number = Int32.Parse(idString.Substring(5, 3));

                if (eventFlagGroups.ContainsKey(group) && eventFlagAreas.ContainsKey(area))
                {
                    int offset = eventFlagGroups[group];
                    offset += eventFlagAreas[area] * 0x500;
                    offset += section * 128;
                    offset += (number - (number % 32)) / 8;

                    mask = 0x80000000 >> (number % 32);
                    return offset;
                }
            }
            throw new ArgumentException("Unknown event flag ID: " + ID);
        }

        public bool ReadEventFlag(int ID)
        {
            int offset = getEventFlagOffset(ID, out uint mask);
            return EventFlags.ReadFlag32(offset, mask);
        }

        public bool WriteEventFlag(int ID, bool state)
        {
            int offset = getEventFlagOffset(ID, out uint mask);
            return EventFlags.WriteFlag32(offset, mask, state);
        }
        #endregion

        #region Hotkeys
        public void MenuKick()
        {
            MenuMan.WriteInt32((int)DSROffsets.MenuMan.MenuKick, 2);
        }
        #endregion

    }
}
