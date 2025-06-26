# tests/test_network.py 
import pytest
import socket
from unittest.mock import patch, MagicMock
import json
import numpy as np

from distributed_aco.network.coordinator import Coordinator
from distributed_aco.network.worker import Worker
from distributed_aco.core.cidade import Cidade

# --- Testes do Worker ---

@patch('socket.socket')
def test_worker_falha_ao_conectar(mock_socket_class):
    mock_socket_instance = MagicMock()
    mock_socket_instance.connect.side_effect = ConnectionRefusedError("Test refusal")
    mock_socket_class.return_value = mock_socket_instance
    worker = Worker("worker-fail", "localhost", 8000)
    assert worker.connect() is False

@patch.object(Worker, 'connect', return_value=True)
@patch('socket.socket')
def test_worker_lida_com_tipos_de_mensagem(mock_socket_class, mock_connect):
    mock_socket_instance = MagicMock()
    mock_socket_class.return_value = mock_socket_instance
    worker = Worker("worker-1", "localhost", 8000)
    worker.engine = MagicMock()
    worker.sock = mock_socket_instance
    msg_update = {"tipo": "atualizar_feromonios", "feromonios": np.ones((5, 5)).tolist()}
    msg_unknown = {"tipo": "tipo_desconhecido"}
    msg_disconnect = b''
    mock_socket_instance.recv.side_effect = [
        json.dumps(msg_update).encode(),
        json.dumps(msg_unknown).encode(),
        msg_disconnect
    ]
    worker.loop()
    worker.engine.integrar_feromonio_externo.assert_called_once()
    assert worker.running is False

# --- Testes do Coordenador ---

#  Adicionado patch no 'threading.Thread' para evitar o warning
@patch('threading.Thread')
@patch('time.sleep')
@patch('socket.socket')
def test_coordinator_nao_inicia_run_sem_clientes(mock_socket, mock_sleep, mock_thread):
    """Testa se o coordenador encerra se nenhum worker conectar."""
    coordinator = Coordinator(port=8000)
    coordinator._run = MagicMock()
    coordinator.start()
    coordinator._run.assert_not_called()
    # Garante que a thread de aceitar conexões foi iniciada
    mock_thread.assert_called_once()


@patch('socket.socket')
def test_coordinator_lida_com_cliente_morto(mock_socket_class):
    coordinator = Coordinator(port=8000)
    good_worker_sock, dead_worker_sock = MagicMock(), MagicMock()
    dead_worker_sock.send.side_effect = BrokenPipeError("Test broken pipe")
    coordinator.clients = {"good-worker": good_worker_sock, "dead-worker": dead_worker_sock}
    coordinator._broadcast({"tipo": "teste"})
    assert "dead-worker" not in coordinator.clients
    assert "good-worker" in coordinator.clients

@patch('socket.socket')
def test_coordinator_lida_com_registro_e_desconexao(mock_socket_class):
    """Testa o ciclo de vida completo de um cliente no _handle_client."""
    mock_client_socket = MagicMock()
    coordinator = Coordinator(port=8000)
    coordinator.running = True
    registro_msg = {"tipo": "registro", "node_id": "worker-1"}
    mock_client_socket.recv.side_effect = [json.dumps(registro_msg).encode(), b'']
    
    # Adicionado o argumento 'addr' que faltava na chamada
    dummy_addr = ('127.0.0.1', 12345)
    coordinator._handle_client(mock_client_socket, dummy_addr)
    
    mock_client_socket.close.assert_called_once()
    assert "worker-1" not in coordinator.clients


@patch('distributed_aco.network.coordinator.Coordinator._broadcast')
def test_coordinator_executa_ciclo_run_completo(mock_broadcast):
    """
    Testa a lógica principal de orquestração do método _run,
    simulando a resposta dos workers de forma correta.
    """
    coordinator = Coordinator(port=8000, max_iters=1)
    coordinator.running = True
    coordinator.clients = {"w1": MagicMock(), "w2": MagicMock()}

    resultado1 = {'melhor_distancia': 100, 'node_id': 'w1', 'melhor_caminho': [0, 1], 'feromonios': [[1, 1], [1, 1]]}
    resultado2 = {'melhor_distancia': 90, 'node_id': 'w2', 'melhor_caminho': [1, 0], 'feromonios': [[2, 2], [2, 2]]}

    def wait_and_populate_results(*args, **kwargs):
        coordinator.iter_results = {'w1': resultado1, 'w2': resultado2}

    with patch.object(coordinator, '_wait_results', side_effect=wait_and_populate_results):
        coordinator._run()

    # --- Verificações Finais ---
    assert coordinator.global_best['distance'] == 90
    assert coordinator.global_best['node_id'] == 'w2'

    # 1. Verifica se o broadcast foi chamado 3 vezes
    assert mock_broadcast.call_count == 3

    # 2. Verificamos o conteúdo de cada chamada para garantir
    calls = mock_broadcast.call_args_list
    
    # Primeira chamada deve ser para executar a iteração
    assert calls[0].args[0]['tipo'] == 'executar_iteracao'
    
    # Segunda chamada deve ser para atualizar feromônios
    assert calls[1].args[0]['tipo'] == 'atualizar_feromonios'
    
    # Terceira chamada deve ser para finalizar
    assert calls[2].args[0]['tipo'] == 'finalizar'


@patch('socket.socket')
def test_coordinator_handle_client_com_erro_de_json(mock_socket_class):
    """Testa se o _handle_client encerra corretamente ao receber um JSON inválido."""
    mock_client_socket = MagicMock()
    # Simula o recebimento de dados que não são um JSON válido
    mock_client_socket.recv.return_value = b'{"tipo": "registro", "node_id": "worker-1"' # JSON quebrado
    
    coordinator = Coordinator()
    # Chama o handler, que deve capturar a exceção e encerrar sem quebrar
    coordinator._handle_client(mock_client_socket, ('127.0.0.1', 12345))
    
    # A verificação é que o teste roda até o fim sem erros
    mock_client_socket.close.assert_called_once()

@patch('socket.socket')
def test_coordinator_accept_loop_com_erro(mock_socket_class):
    """Testa se o _accept_loop para de rodar ao ocorrer um erro no socket."""
    mock_server_socket = MagicMock()
    # Simula um erro quando o accept é chamado
    mock_server_socket.accept.side_effect = OSError("Test socket error")
    mock_socket_class.return_value = mock_server_socket
    
    coordinator = Coordinator()
    coordinator.running = True
    coordinator._accept_loop() # Chama o loop
    
    # A verificação é que o teste termina e o erro foi tratado,
    # fazendo com que o 'break' no _accept_loop seja ativado.
    assert True # O teste não quebrar já é o resultado esperado

@patch('time.time', side_effect=[0, 1, 2, 3, 4, 6]) # Simula a passagem de 6s
@patch('time.sleep')
def test_coordinator_wait_results_com_timeout(mock_sleep, mock_time):
    """Testa se a função _wait_results respeita o timeout."""
    coordinator = Coordinator()
    coordinator.iter_results.clear()
    
    # Espera por 2 resultados, mas nenhum chegará. O timeout de 5s deve ser atingido.
    coordinator._wait_results(n=2, timeout=5.0)
    
    # A verificação é que a função terminou após o tempo simulado
    # sem ficar em loop infinito.
    assert len(coordinator.iter_results) == 0

@patch.object(Worker, 'connect', return_value=True)
@patch('socket.socket')
def test_worker_executa_iteracao_e_envia_resultado(mock_socket_class, mock_connect):
    """Testa se o worker executa uma iteração e envia o resultado."""
    mock_socket_instance = MagicMock()
    mock_socket_class.return_value = mock_socket_instance
    
    worker = Worker("worker-1", "localhost", 8000)
    # Usamos um mock para o engine para controlar o resultado
    worker.engine = MagicMock()
    worker.engine.executar_iteracao.return_value = {"distancia": 123}
    worker.sock = mock_socket_instance
    
    # Simula o recebimento da mensagem 'executar_iteracao'
    msg_exec = {"tipo": "executar_iteracao"}
    # O segundo valor do side_effect simula a desconexão para parar o loop
    mock_socket_instance.recv.side_effect = [json.dumps(msg_exec).encode(), b'']
    
    worker.loop()
    
    # Verifica se o método do engine foi chamado
    worker.engine.executar_iteracao.assert_called_once()
    # Verifica se o resultado foi enviado de volta pelo socket
    mock_socket_instance.send.assert_called_once()
    sent_data = json.loads(mock_socket_instance.send.call_args[0][0].decode())
    assert sent_data['tipo'] == 'resultado_iteracao'
    assert sent_data['dados']['distancia'] == 123

@patch('socket.socket')
def test_coordinator_recebe_resultado_do_worker(mock_socket_class):
    """Testa se o coordenador armazena o resultado de uma iteração recebida."""
    mock_client_socket = MagicMock()
    coordinator = Coordinator()
    coordinator.running = True

    # Mensagens que o worker "enviaria"
    msg_registro = {"tipo": "registro", "node_id": "worker-1"}
    msg_resultado = {
        "tipo": "resultado_iteracao",
        "dados": {"distancia": 555}
    }
    
    # Simula o recebimento em sequência: registro, resultado, desconexão
    mock_client_socket.recv.side_effect = [
        json.dumps(msg_registro).encode(),
        json.dumps(msg_resultado).encode(),
        b''
    ]
    
    # Executa o handler que deveria processar as mensagens
    coordinator._handle_client(mock_client_socket, ('127.0.0.1', 12345))
    
    # A verificação principal: o resultado foi armazenado corretamente?
    assert "worker-1" in coordinator.iter_results
    assert coordinator.iter_results["worker-1"]["distancia"] == 555


@patch('socket.socket')
def test_worker_connect_com_config_invalida(mock_socket_class):
    """
    Testa o que acontece se o worker recebe uma mensagem de configuração
    com o tipo incorreto do coordenador.
    """
    mock_socket_instance = MagicMock()
    # Simula o recebimento de uma mensagem que não é de configuração
    config_invalida = {"tipo": "tipo_errado"}
    mock_socket_instance.recv.return_value = json.dumps(config_invalida).encode()
    mock_socket_class.return_value = mock_socket_instance
    
    worker = Worker("worker-cfg-invalida")
    # O método connect deve retornar False ao não reconhecer a configuração
    assert worker.connect() is False

@patch('socket.socket')
def test_worker_connect_com_host_invalido(mock_socket_class):
    """Testa o tratamento de exceção geral no connect (ex: host não encontrado)."""
    mock_socket_instance = MagicMock()
    # Simula um erro de DNS/rede ao tentar conectar
    mock_socket_instance.connect.side_effect = socket.gaierror("Test host not found")
    mock_socket_class.return_value = mock_socket_instance

    worker = Worker("worker-host-invalido")
    # O bloco except Exception deve ser ativado, retornando False
    assert worker.connect() is False

@patch.object(Worker, 'connect', return_value=True)
@patch('socket.socket')
def test_worker_loop_com_erro_de_rede(mock_socket_class, mock_connect):
    """
    Testa se o loop do worker para corretamente se ocorrer um erro de rede
    durante o recebimento de dados.
    """
    mock_socket_instance = MagicMock()
    mock_socket_class.return_value = mock_socket_instance
    
    worker = Worker("worker-loop-err")
    worker.sock = mock_socket_instance
    
    # Simula um erro de conexão durante a chamada a recv()
    mock_socket_instance.recv.side_effect = ConnectionResetError("Test connection reset")
    
    # Chama o loop, que deve entrar no bloco 'except' e parar
    worker.loop()
    
    # A verificação principal é que o worker parou de rodar
    assert worker.running is False