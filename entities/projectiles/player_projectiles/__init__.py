from .base import Base
from .ice import Ice
from .air import Air
from .blood import Blood
from .lightning import Lightning
from .radiation import Radiation
from .fire import Fire


# Registre des classes d'attacques
ATTACK_TYPE_CLASS = {
    "Base": Base,
    "Ice": Ice,
    "Air": Air,
    "Blood": Blood,
    "Lightning": Lightning,
    "Radiation": Radiation,
    "Fire": Fire
}
