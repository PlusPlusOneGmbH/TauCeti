# Makre sure subpackages are imported so they can be accesses via the mod. method.
from . import PresetManager
from . import Tweener

# Future Proofing
__minimum_td_version__ = "2023.1200"

# Futureprrofing for automated search of toxfiles and imports.
_ToxFiles = {
    "PresetManager" : PresetManager.ToxFile,
    "Tweener" : Tweener.ToxFile
}