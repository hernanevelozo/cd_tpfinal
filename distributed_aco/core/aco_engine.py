from __future__ import annotations
import random, math
from typing import List, Dict

import numpy as np

from .cidade import Cidade
from .formiga import Formiga

class ACOEngine:
    """Algoritmo de Colônia de Formigas (ACO) para TSP, autocontido.

    Não sabe nada sobre rede; pode ser testado isoladamente.
    """

    def __init__(self,
                 node_id: str,
                 cidades: List[Cidade],
                 num_formigas: int = 20,
                 alpha: float = 1.0,
                 beta: float = 2.0,
                 rho: float = 0.1,
                 Q: float = 100.0,
                 seed: int | None = None) -> None:

        self.node_id = node_id
        self.cidades = cidades
        self.num_cidades = len(cidades)
        self.num_formigas = num_formigas

        self.alpha, self.beta, self.rho, self.Q = alpha, beta, rho, Q
        self.rng = random.Random(seed)

        self.distancias = self._calcular_distancias()
        self.heuristica = np.divide(1.0, self.distancias,
                                    out=np.zeros_like(self.distancias),
                                    where=self.distancias != 0)
        self.feromonios = np.ones_like(self.distancias) * 0.1

        self.melhor_caminho: List[int] = []
        self.melhor_distancia: float = float("inf")
        self.iteracao_atual = 0
        self.historico_melhores: List[float] = []

    # -----------------------------------------------------------------
    def _calcular_distancias(self) -> np.ndarray:
        dist = np.zeros((self.num_cidades, self.num_cidades))
        for i in range(self.num_cidades):
            for j in range(self.num_cidades):
                if i != j:
                    dist[i, j] = self.cidades[i].distancia_para(self.cidades[j])
        return dist

    # -----------------------------------------------------------------
    def executar_iteracao(self) -> Dict:
        formigas = [Formiga(i, self.rng.randrange(self.num_cidades))
                    for i in range(self.num_formigas)]

        for ant in formigas:
            self._construir_solucao(ant)

        self._atualizar_feromonios(formigas)

        melhor_formiga = min(formigas, key=lambda f: f.distancia_total)
        if melhor_formiga.distancia_total < self.melhor_distancia:
            self.melhor_distancia = melhor_formiga.distancia_total
            self.melhor_caminho = melhor_formiga.caminho[:-1]

        self.iteracao_atual += 1
        self.historico_melhores.append(self.melhor_distancia)

        return {
            "node_id": self.node_id,
            "iteracao": self.iteracao_atual,
            "melhor_distancia": self.melhor_distancia,
            "melhor_caminho": self.melhor_caminho,
            "media_iteracao": sum(a.distancia_total for a in formigas) / len(formigas),
            "feromonios": self.feromonios.tolist(),
        }

    # -----------------------------------------------------------------
    def _construir_solucao(self, ant: Formiga) -> None:
        while len(ant.visitadas) < self.num_cidades:
            nxt = self._selecionar_proxima_cidade(ant)
            dist = self.distancias[ant.cidade_atual, nxt]
            ant.visitar(nxt, dist)

        dist_retorno = self.distancias[ant.cidade_atual, ant.caminho[0]]
        ant.finalizar_tour(dist_retorno)

    def _selecionar_proxima_cidade(self, ant: Formiga) -> int:
        disponiveis = [i for i in range(self.num_cidades) if ant.pode_visitar(i)]
        if not disponiveis:
            return ant.caminho[0]

        probs = []
        total = 0.0
        for j in disponiveis:
            tau = self.feromonios[ant.cidade_atual, j]
            eta = self.heuristica[ant.cidade_atual, j]
            p = (tau ** self.alpha) * (eta ** self.beta)
            probs.append(p)
            total += p

        if total == 0:
            return self.rng.choice(disponiveis)

        probs = [p / total for p in probs]
        r = self.rng.random()
        cumul = 0.0
        for idx, p in enumerate(probs):
            cumul += p
            if r <= cumul:
                return disponiveis[idx]
        return disponiveis[-1] # pragma: no cover
    # -----------------------------------------------------------------
    def _atualizar_feromonios(self, formigas: List[Formiga]) -> None:
        self.feromonios *= (1 - self.rho)
        for ant in formigas:
            delta = self.Q / ant.distancia_total
            for i in range(len(ant.caminho) - 1):
                a, b = ant.caminho[i], ant.caminho[i + 1]
                self.feromonios[a, b] += delta
                self.feromonios[b, a] += delta

    # -----------------------------------------------------------------
    def integrar_feromonio_externo(self, externo, peso: float = 0.1) -> None:
        self.feromonios = (1 - peso) * self.feromonios + peso * externo
