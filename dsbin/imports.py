import clr
import sys
from os.path import dirname, realpath
sys.path.append(dirname(realpath(__file__)))
clr.AddReference("GameHook")
# noinspection PyUnresolvedReferences
from DarkShellRemastered import DSRHook, Stats
# noinspection PyUnresolvedReferences
from System import Type, Enum


def get_clr_type(obj):
    full_name = obj.__module__ + "." + obj.__name__ + ", GameHook"
    return Type.GetType(full_name)

