from distributed_aco.core.cidade import Cidade
import math

def test_distancia_euclidiana():
    a = Cidade(0, 0, 0, "A")
    b = Cidade(1, 3, 4, "B")
    assert math.isclose(a.distancia_para(b), 5.0, rel_tol=1e-6)
    assert math.isclose(b.distancia_para(a), 5.0, rel_tol=1e-6)


def test_serializacao_e_deserializacao_cidade():
    """Testa os métodos to_dict e from_dict."""
    cidade_original = Cidade(10, 150.5, 250.7, "Teste")
    dados_dict = cidade_original.to_dict()
    
    # Verifica o conteúdo do dicionário
    assert dados_dict == {"id": 10, "x": 150.5, "y": 250.7, "nome": "Teste"}
    
    # Cria uma nova cidade a partir do dicionário
    cidade_recriada = Cidade.from_dict(dados_dict)
    
    # Verifica se a cidade recriada é idêntica à original
    assert cidade_recriada.id == cidade_original.id
    assert cidade_recriada.nome == cidade_original.nome
    assert math.isclose(cidade_recriada.x, cidade_original.x)