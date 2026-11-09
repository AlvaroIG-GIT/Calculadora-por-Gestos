"""Detección de dedos extendidos, clasificación de gestos y estabilización."""
import math
from collections import Counter, deque


def _dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def fingers_up(lm):
    """Devuelve (pulgar, indice, corazon, anular, menique); 1 = extendido.

    Se comparan distancias en vez de coordenadas 'y', para que funcione
    aunque la mano esté inclinada.
    """
    wrist = lm[0]
    # Pulgar: la punta (4) está más lejos de la base del meñique (17) que la falange (3)
    thumb = int(_dist(lm[4], lm[17]) > _dist(lm[3], lm[17]))
    # Resto: la punta está más lejos de la muñeca que la articulación PIP
    others = tuple(int(_dist(lm[t], wrist) > _dist(lm[t - 2], wrist))
                   for t in (8, 12, 16, 20))
    return (thumb,) + others


# Patrón (pulgar, indice, corazon, anular, menique) -> comando
COMMANDS = {
    (0, 1, 0, 0, 0): "+",
    (0, 1, 1, 0, 0): "-",
    (0, 1, 1, 1, 0): "*",
    (0, 1, 1, 1, 1): "/",
    (1, 1, 1, 1, 1): "=",
    (1, 0, 0, 0, 0): "DELETE",
    (0, 0, 0, 0, 1): "RESET",
}

HOLD_TIMES = {"RESET": 1.5}   # acciones destructivas: más tiempo
DEFAULT_HOLD = 0.8


def classify(hands):
    """hands: lista de tuplas de dedos (una por mano). Devuelve etiqueta o None."""
    if len(hands) == 2:
        total = sum(sum(h) for h in hands)
        return f"DIGIT_{total}" if total <= 9 else None
    if len(hands) == 1:
        return COMMANDS.get(hands[0])
    return None


class Smoother:
    """Voto mayoritario sobre los últimos N fotogramas (reduce parpadeo)."""

    def __init__(self, size=7, min_votes=5):
        self.buffer = deque(maxlen=size)
        self.min_votes = min_votes

    def update(self, label):
        self.buffer.append(label)
        best, votes = Counter(self.buffer).most_common(1)[0]
        return best if votes >= self.min_votes else None


class HoldConfirmer:
    """Confirma un gesto solo si se mantiene estable un tiempo, y una sola vez."""

    def __init__(self):
        self.current = None
        self.start = 0.0
        self.fired = False

    def update(self, label, now):
        """Devuelve (etiqueta_confirmada | None, progreso 0..1)."""
        if label is None:
            self.current, self.fired = None, False
            return None, 0.0
        if label != self.current:
            self.current, self.start, self.fired = label, now, False
        hold = HOLD_TIMES.get(label, DEFAULT_HOLD)
        progress = min((now - self.start) / hold, 1.0)
        if progress >= 1.0 and not self.fired:
            self.fired = True
            return label, 1.0
        return None, (1.0 if self.fired else progress)
