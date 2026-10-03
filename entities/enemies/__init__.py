from .enemy import Enemy
from .cinder_imp import CinderImp
from .gorehound import Gorehound
from .bloodwing import Bloodwing
from .spikeborn import Spikeborn

# Registre des classes d'ennemis instanciables depuis rooms.json
ENEMIES_CLASS = {
    "CinderImp": CinderImp,
    "Gorehound": Gorehound,
    "Bloodwing": Bloodwing,
    "Spikeborn": Spikeborn,
}


def create_enemy(enemy_type: str, pos: tuple[float, float], **kwargs) -> Enemy | None:
    """Fabrique une instance d'ennemi à partir de son nom de classe."""
    cls = ENEMIES_CLASS.get(enemy_type)
    if cls is not None:
        return cls(pos=pos, **kwargs)
    return None