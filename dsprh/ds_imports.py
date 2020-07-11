import clr
import sys
from os.path import dirname, realpath
sys.path.append(dirname(realpath(__file__)))
clr.AddReference("GameHook")
# noinspection PyUnresolvedReferences
from DarkShellRemastered import DSRHook
