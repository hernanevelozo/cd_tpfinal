from __future__ import annotations
import math
from typing import Dict

class Cidade:
    """Representa uma cidade no problema TSP"""

    def __init__(self, id: int, x: float, y: float, nome: str = "") -> None:
        self.id = id
        self.x = x
        self.y = y
        self.nome = nome or f"Cidade_{id}"

    # ---------------------------------------------------------
    #  Helpers
    # ---------------------------------------------------------
    def distancia_para(self, outra: "Cidade") -> float:
        """Distância euclidiana 2‑D para outra cidade"""
        return math.hypot(self.x - outra.x, self.y - outra.y)

    def to_dict(self) -> Dict:
        return {"id": self.id, "x": self.x, "y": self.y, "nome": self.nome}

    @classmethod
    def from_dict(cls, data: Dict) -> "Cidade":
        return cls(data["id"], data["x"], data["y"], data.get("nome", ""))
