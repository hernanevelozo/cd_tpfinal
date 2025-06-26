
import pytest
import numpy as np

# Importa as classes principais do seu projeto
from distributed_aco.core.cidade import Cidade
from distributed_aco.core.formiga import Formiga
from distributed_aco.core.aco_engine import ACOEngine
# Importa as funções de plotagem
from distributed_aco.plotting import plotar_solucao, plotar_convergencia, plotar_solucao_3d_plotly

@pytest.fixture
def cidades_brasil():
    """
    Fornece uma lista de cidades brasileiras com coordenadas (lat, lon)
    tratadas como (y, x) em um plano 2D para o teste.
    """
    # Latitude e Longitude aproximadas
    return [
        Cidade(0, -23.55, -46.63, "São Paulo"),       # SP
        Cidade(1, -22.90, -43.17, "Rio de Janeiro"),  # RJ
        Cidade(2, -19.92, -43.94, "Belo Horizonte"),  # MG
        Cidade(3, -20.32, -40.34, "Vitória"),         # ES
        Cidade(4, -15.78, -47.93, "Brasília"),        # DF
        Cidade(5, -12.97, -38.50, "Salvador"),        # BA
        Cidade(6, -25.43, -49.27, "Curitiba"),        # PR
        Cidade(7, -30.03, -51.23, "Porto Alegre"),    # RS
    ]


def test_inicializacao_engine(cidades_brasil):
    """
    Verifica se o engine inicializa suas matrizes com as dimensões 
    usando a lista de cidades do Brasil.
    """
    engine = ACOEngine("test_init", cidades_brasil, num_formigas=10)
    num_cidades = len(cidades_brasil)

    assert engine.distancias.shape == (num_cidades, num_cidades)
    assert engine.feromonios.shape == (num_cidades, num_cidades)
    assert np.all(np.diag(engine.distancias) == 0)
    assert engine.melhor_distancia == float("inf")


@pytest.mark.parametrize("alpha, beta", [
    (1.0, 3.0),
])
def test_engine_executa_com_cidades_do_brasil_e_plota(cidades_brasil, alpha, beta):
    """
    Testa se o engine converge para uma solução válida com dados reais e,
    ao final, gera os gráficos da melhor rota encontrada.
    """
    engine = ACOEngine(
        node_id="test_run_brasil",
        cidades=cidades_brasil,
        num_formigas=20,
        alpha=alpha,
        beta=beta,
        seed=42
    )
    
    distancia_nao_otimizada = 0
    for i in range(len(cidades_brasil) - 1):
        distancia_nao_otimizada += engine.distancias[i, i + 1]
    distancia_nao_otimizada += engine.distancias[len(cidades_brasil) - 1, 0]

    for _ in range(100):
        engine.executar_iteracao()

    caminho_final = engine.melhor_caminho
    distancia_final = engine.melhor_distancia

    assert distancia_final < float("inf")
    assert distancia_final < distancia_nao_otimizada
    assert len(caminho_final) == len(cidades_brasil)
    assert set(caminho_final) == set(range(len(cidades_brasil)))

    # --- Geração dos Gráficos ---
    if caminho_final:
        titulo_grafico = f"Melhor Rota Encontrada (Distância: {distancia_final:.2f})"
        
        # Gera os gráficos 2D com matplotlib
        plotar_solucao(cidades_brasil, caminho_final, titulo_grafico)
        plotar_convergencia(engine.historico_melhores)
        
        # Gera o novo gráfico 3D com Plotly
        plotar_solucao_3d_plotly(cidades_brasil, caminho_final, titulo_grafico)


def test_integracao_feromonio_externo(cidades_brasil):
    """
    Testa se a matriz de feromônios externa é integrada corretamente à matriz do engine.
    """
    engine = ACOEngine("test_pheromones", cidades_brasil, seed=1)
    feromonios_originais = engine.feromonios.copy()

    feromonios_externos = np.ones_like(feromonios_originais) * 5.0
    peso = 0.5

    engine.integrar_feromonio_externo(feromonios_externos, peso=peso)

    feromonios_esperados = (1 - peso) * feromonios_originais + peso * feromonios_externos
    assert np.allclose(engine.feromonios, feromonios_esperados)


def test_selecao_proxima_cidade_com_probabilidade_zero(cidades_brasil):
    """
    Testa o caso extremo onde todas as probabilidades de escolha são zero.
    """
    engine = ACOEngine("test_edge_case", cidades_brasil)
    engine.feromonios.fill(0)
    
    ant = Formiga(0, cidade_inicial=0)
    ant.visitar(1, 10)

    proxima_cidade = engine._selecionar_proxima_cidade(ant)

    disponiveis = set(range(len(cidades_brasil))) - {0, 1}
    assert proxima_cidade in disponiveis