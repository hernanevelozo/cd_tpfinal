"""CLI: python -m distributed_aco.cli --mode coordenador|trabalhador ..."""
import argparse, sys, random, string

from distributed_aco.network.coordinator import Coordinator
from distributed_aco.network.worker import Worker

def _rand_id(k=5):
    return "".join(random.choices(string.ascii_uppercase, k=k))

def main():
    parser = argparse.ArgumentParser(description="Distributed ACO for TSP")
    parser.add_argument("--mode", choices=["coordenador", "trabalhador"], required=True)
    parser.add_argument("--id", help="worker id (auto if omitted)")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--ants", type=int, default=20)
    parser.add_argument("--iters", type=int, default=100)

    args = parser.parse_args()
    if args.mode == "coordenador":
        Coordinator(port=args.port, max_iters=args.iters).start()
    else:
        wid = args.id or _rand_id()
        Worker(wid, host=args.host, port=args.port, ants=args.ants).loop()

if __name__ == "__main__":
    main()
