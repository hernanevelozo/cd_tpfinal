"""Worker node: conecta‑se ao coordenador e executa o ACO localmente."""
from __future__ import annotations
import socket, json, time, random
from typing import Optional
import numpy as np
from ..core.cidade import Cidade
from ..core.aco_engine import ACOEngine
from distributed_aco.core.cidade import Cidade
from distributed_aco.core.aco_engine import ACOEngine

class Worker:
    def __init__(self, node_id: str, host="localhost", port=8000, ants=20):
        self.node_id = node_id
        self.host, self.port = host, port
        self.ants = ants
        self.sock: Optional[socket.socket] = None
        self.engine: Optional[ACOEngine] = None
        self.running = False

    # --------------------------------------------------------------
    def connect(self) -> bool:
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.sock.send(json.dumps({
                "tipo": "registro",
                "node_id": self.node_id,
                "num_formigas": self.ants,
            }).encode())
            cfg = json.loads(self.sock.recv(4096).decode())
            if cfg["tipo"] != "configuracao":
                return False
            cities = [Cidade.from_dict(c) for c in cfg["cidades"]]
            self.engine = ACOEngine(self.node_id, cities, self.ants, seed=random.randrange(9999))
            return True
        except Exception as e:
            print(f"❌ Worker {self.node_id} failed to connect: {e}")
            return False



    def loop(self) -> None:
        if not self.connect():
            return
            
        self.running = True
        print(f"🐜 Worker {self.node_id} running")
        
        while self.running:
            try:
                # Recebe os dados do socket
                data = self.sock.recv(8192).decode()

                # Se 'data' for vazio, o servidor desconectou. Paramos o loop.
                if not data:
                    self.running = False
                    continue

                # Apenas se houver dados, tentamos decodificar o JSON
                msg = json.loads(data)
                mtype = msg.get("tipo") # Usar .get() é mais seguro

                if mtype == "executar_iteracao":
                    iter_data = self.engine.executar_iteracao()
                    self.sock.send(json.dumps({"tipo": "resultado_iteracao", "dados": iter_data}).encode())
                elif mtype == "atualizar_feromonios":
                    self.engine.integrar_feromonio_externo(np.array(msg["feromonios"]))
                else:
                    # Mensagem desconhecida, apenas aguarda
                    time.sleep(0.01)

            except (json.JSONDecodeError, ConnectionError, BrokenPipeError):
                # Se qualquer erro de rede ou JSON ocorrer, encerra o loop
                self.running = False