# tests/test_cli.py
import pytest
from unittest.mock import patch, MagicMock

# Importa a função main do seu script CLI
from distributed_aco.cli import main

@patch('distributed_aco.cli.Coordinator')
def test_cli_inicia_coordenador(mock_coordinator):
    """Verifica se o modo 'coordenador' instancia e inicia o Coordenador."""
    # Simula os argumentos de linha de comando
    with patch('sys.argv', ['cli.py', '--mode', 'coordenador', '--port', '8001']):
        main()
        # Verifica se a classe Coordenador foi chamada com os argumentos 
        mock_coordinator.assert_called_once_with(port=8001, max_iters=100)
        # Verifica se o método start() foi chamado
        mock_coordinator.return_value.start.assert_called_once()

@patch('distributed_aco.cli.Worker')
def test_cli_inicia_worker(mock_worker):
    """Verifica se o modo 'trabalhador' instancia e inicia o Worker."""
    with patch('sys.argv', ['cli.py', '--mode', 'trabalhador', '--host', 'testhost', '--port', '8002', '--id', 'test-worker']):
        main()
        mock_worker.assert_called_once_with('test-worker', host='testhost', port=8002, ants=20)
        mock_worker.return_value.loop.assert_called_once()

@patch('distributed_aco.cli.Worker')
def test_cli_inicia_worker_com_id_aleatorio(mock_worker):
    """Verifica se um ID é gerado quando não fornecido."""
    with patch('sys.argv', ['cli.py', '--mode', 'trabalhador']):
        main()
        # Verifica se o Worker foi chamado. O primeiro argumento é o ID.
        args, _ = mock_worker.call_args
        worker_id = args[0]
        # Apenas verificamos que um ID foi gerado (não é nulo e é uma string)
        assert worker_id is not None
        assert isinstance(worker_id, str)
