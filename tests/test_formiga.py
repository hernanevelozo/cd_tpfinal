from distributed_aco.core.formiga import Formiga

def test_visita():
    ant = Formiga(0, 0)
    assert ant.caminho == [0]
    ant.visitar(1, 10.0)
    assert ant.caminho == [0, 1]
    assert 1 in ant.visitadas
    assert ant.distancia_total == 10.0
    ant.finalizar_tour(10.0)
    # retorna à origem
    assert ant.caminho[-1] == 0
    assert ant.distancia_total == 20.0

