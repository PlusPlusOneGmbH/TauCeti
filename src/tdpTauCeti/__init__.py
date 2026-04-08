# Makre sure subpackages are imported so they can be accesses via the mod. method.
from . import PresetManager, Tweener, PresetDashboard, PresetCuelist, PresetChopMapper, TweenCHOP


# Future Proofing
__minimum_td_version__ = "2025.32460"

# Futureprrofing for automated search of toxfiles and imports.
_ToxFiles = {
    "PresetManager" : PresetManager.ToxFile,
    "Tweener" : Tweener.ToxFile,
    "PresetDashboard" : PresetDashboard.ToxFile,
    "PresetCuelist" : PresetCuelist.ToxFile,
    "PresetChopMapper" : PresetChopMapper.ToxFile,
    "TweenCHOP" : TweenCHOP.ToxFile
}