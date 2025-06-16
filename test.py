# import the library
from pynq import Overlay  # import the overlay
from pynq import allocate  # import for CMA (contingeous memory allocation)
from pynq import DefaultIP  # import the ip connector library for extension



overlay = Overlay('/media/tanawin/tanawin1701e/project6/hardwares/demoDfx/system.bit', download=False)
help(overlay)
