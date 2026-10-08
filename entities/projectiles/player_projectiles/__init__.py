from .base import Base
from .ice import Ice


# Registre des classes d'attacques
ATTACK_TYPE_CLASS = {
    "Base": Base,
    "Ice": Ice,
}
