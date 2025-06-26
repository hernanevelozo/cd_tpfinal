
import socket
import threading
import json
import time
from typing import Dict, List
import numpy as np

from ..core.cidade import Cidade
from ..plotting import plotar_solucao, plotar_solucao_3d_plotly

class Coordinator:
    def __init__(self, port: int = 8000, max_iters: int = 100) -> None:
        self.port = port
        self.max_iters = max_iters
        self.clients: Dict[str, socket.socket] = {}
        self.iter_results: Dict[str, dict] = {}
        self.global_best = {"distance": float("inf"), "path": [], "node_id": ""}
        self.global_pheromone: np.ndarray | None = None
        self.cities = self._sample_cities()
        self.running = False
        self.lock = threading.Lock()
        self.start_event = threading.Event()

    def _sample_cities(self) -> List[Cidade]:
        coords = [
            (0, 0, "São Paulo"), (100, 200, "Rio de Janeiro"),
            (300, 100, "Belo Horizonte"), (500, 300, "Salvador"),
            (200, 500, "Recife"), (600, 100, "Brasília"),
        ]
        return [Cidade(i, x, y, n) for i, (x, y, n) in enumerate(coords)]

    def start(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", self.port))
        sock.listen(10)
        self.running = True
        
        print(f"🏛️  Coordinator listening on :{self.port}. Pressione Ctrl+C para sair.")
        
        orchestrator_thread = threading.Thread(target=self._orchestration_loop, daemon=True)
        orchestrator_thread.start()

        try:
            while self.running:
                client_sock, addr = sock.accept()
                threading.Thread(target=self._handle_client, args=(client_sock, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\n🔌 Encerrando o coordenador...")
        finally:
            
            self.running = False
            self.start_event.set()
            sock.close()

    def _handle_client(self, sock: socket.socket, addr) -> None:
        node_id = None
        try:
            data = sock.recv(4096).decode()
            msg = json.loads(data)
            if msg.get("tipo") != "registro": return
            
            node_id = msg.get("node_id")
            with self.lock:
                self.clients[node_id] = sock
            
            conf = {"tipo": "configuracao", "cidades": [c.to_dict() for c in self.cities]}
            sock.send(json.dumps(conf).encode())
            print(f"✅ Worker {node_id} conectado de {addr}")

            while self.running:
                self.start_event.wait()
                if not self.running: break

                pheromones = self.global_pheromone.tolist() if self.global_pheromone is not None else []
                sock.send(json.dumps({"tipo": "executar_iteracao", "feromonios": pheromones}).encode())
                
                result_data = sock.recv(8192).decode()
                if not result_data: break
                
                rsp = json.loads(result_data)
                if rsp.get("tipo") == "resultado_iteracao":
                    with self.lock:
                        self.iter_results[node_id] = rsp["dados"]
        except (json.JSONDecodeError, ConnectionResetError, BrokenPipeError, OSError):
            pass
        finally:
            if node_id:
                with self.lock:
                    self.clients.pop(node_id, None)
                print(f"➖ Worker {node_id} desconectado.")
            sock.close()

    def _orchestration_loop(self):
        lobby_wait_seconds = 15
        print(f"🏛️  Sala de espera aberta por {lobby_wait_seconds} segundos...")
        time.sleep(lobby_wait_seconds)

        with self.lock:
            num_workers = len(self.clients)
        if num_workers == 0:
            print("❌ Nenhum worker se conectou. Encerrando.")
            self.running = False
            return
            
        print(f"🚀 Iniciando otimização com {num_workers} worker(s).")
        
        self.global_pheromone = np.ones((len(self.cities), len(self.cities))) * 0.1

        for it in range(self.max_iters):
            if not self.running: break

            with self.lock:
                self.iter_results.clear()
            
            self.start_event.clear()
            self.start_event.set()
            
            time.sleep(1)
            
            self.start_event.clear()
            
            with self.lock:
                self._aggregate()

            if (it + 1) % 5 == 0 or it == self.max_iters - 1:
                self._print_status(it + 1)
        
        self.running = False
        self.start_event.set()
        self._finish_plotting()

    def _aggregate(self):
        if not self.iter_results: return

        best_iter = min(self.iter_results.values(), key=lambda r: r["melhor_distancia"])
        if best_iter["melhor_distancia"] < self.global_best["distance"]:
            self.global_best.update({
                "distance": best_iter["melhor_distancia"],
                "path": best_iter["melhor_caminho"],
                "node_id": best_iter["node_id"],
            })

        all_pheromones = [np.array(r['feromonios']) for r in self.iter_results.values() if r.get('feromonios')]
        if all_pheromones:
            self.global_pheromone = np.mean(np.array(all_pheromones), axis=0)

    def _print_status(self, it: int):
        print(f"--- Iteração {it:3d}/{self.max_iters} | Melhor Global: {self.global_best['distance']:.2f} (Worker: {self.global_best.get('node_id', 'N/A')}) ---")


    def _finish_plotting(self):
        """
        Este método é chamado ao final da otimização para gerar 
        os resultados visuais.
        """
        print("🏁 Otimização finalizada.")
        if self.global_best["path"]:
            titulo = f"Melhor Rota Global (Distância: {self.global_best['distance']:.2f})"

            print("\nGerando gráfico 2D estático...")
            plotar_solucao(self.cities, self.global_best["path"], titulo)

            print("\nGerando gráfico 3D interativo...")
            plotar_solucao_3d_plotly(self.cities, self.global_best["path"], titulo)