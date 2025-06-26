from __future__ import annotations
from typing import List, Set

class Formiga:
    """Uma única formiga que constrói rotas."""

    def __init__(self, id: int, cidade_inicial: int) -> None:
        self.id = id
        self.cidade_atual = cidade_inicial
        self.caminho: List[int] = [cidade_inicial]
        self.visitadas: Set[int] = {cidade_inicial}
        self.distancia_total: float = 0.0

    # -----------------------------------------------------------------
    def pode_visitar(self, cidade: int) -> bool:
        return cidade not in self.visitadas

    def visitar(self, cidade: int, distancia: float) -> None:
        self.cidade_atual = cidade
        self.caminho.append(cidade)
        self.visitadas.add(cidade)
        self.distancia_total += distancia

    def finalizar_tour(self, distancia_retorno: float) -> None:
        self.distancia_total += distancia_retorno
        self.caminho.append(self.caminho[0])
