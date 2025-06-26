# Sistema Distribuído de Otimização de Rotas com Colônia de Formigas (ACO)

## Visão Geral

Este projeto acadêmico, desenvolvido para a disciplina de Computação Distribuída, implementa uma solução para o Problema do Caixeiro Viajante (TSP) utilizando a meta-heurística de Otimização por Colônia de Formigas (ACO). A solução foi arquitetada como um sistema distribuído no modelo Mestre-Trabalhador (Coordinator-Worker) para explorar conceitos de paralelismo e comunicação em rede.

A comunicação entre os nós é realizada através de sockets TCP puros, com um protocolo customizado baseado em mensagens JSON. A concorrência no nó Coordenador é gerenciada por threads.

## Tecnologias Utilizadas

* **Linguagem:** Python 3.9+
* **Comunicação em Rede:** `socket` (TCP/IP)
* **Concorrência:** `threading`
* **Computação Numérica:** `NumPy`
* **Visualização de Dados:** `Matplotlib` e `Plotly`
* **Testes:** `unittest` e `pytest`

## Estrutura do Projeto

```
.
├── distributed_aco/       # Pacote principal da aplicação
│   ├── core/              # Lógica do algoritmo ACO (engine, cidade, formiga)
│   ├── network/           # Lógica de rede (coordinator, worker)
│   └── cli.py             # Interface de linha de comando
├── tests/                 # Suíte de testes automatizados
├── requirements.txt       # Dependências do projeto
└── ...
```

## Como Configurar o Ambiente

Siga os passos abaixo para preparar o ambiente de execução.

**1. Clone o Repositório (se aplicável)**
```bash
git clone https://github.com/hernanevelozo/cd_tpfinal/
cd distributed_aco_finalTP
```

**2. Crie e Ative um Ambiente Virtual**
É altamente recomendado usar um ambiente virtual para isolar as dependências.
```bash
# Criar o ambiente
python3 -m venv venv

# Ativar o ambiente
# No macOS/Linux:
source venv/bin/activate
# No Windows:
# venv\Scripts\activate
```

**3. Instale as Dependências**
Com o ambiente virtual ativado, instale todas as bibliotecas necessárias.
```bash
pip install -r requirements.txt
```

## Como Executar o Sistema

Para executar o sistema distribuído, você precisará de pelo menos dois terminais, um para o Coordenador e outro para o(s) Worker(s).

#### **1. Iniciar o Coordenador**

No primeiro terminal (com o ambiente virtual ativado), inicie o Coordenador. Ele ficará aguardando as conexões dos workers.

```bash
python -m distributed_aco.cli --mode coordenador
```
* **Para testes rápidos**, você pode especificar o número de iterações:
```bash
python -m distributed_aco.cli --mode coordenador --iters 20
```

#### **2. Iniciar um ou mais Workers**

Em um ou mais terminais novos (também com o ambiente virtual ativado), inicie os processos Worker.

* **Se o Worker estiver na mesma máquina que o Coordenador:**
    ```bash
    python -m distributed_aco.cli --mode trabalhador --id worker-local-01
    ```

* **Se o Worker estiver em outra máquina na mesma rede local:**
    Você precisa especificar o endereço IP da máquina do Coordenador.
    ```bash
    # Substitua <IP_DO_COORDENADOR> pelo IP real
    python -m distributed_aco.cli --mode trabalhador --id worker-remoto-01 --host <IP_DO_COORDENADOR>
    ```

## Como Rodar os Testes

Com o ambiente configurado, você pode rodar a suíte de testes automatizados para verificar a integridade dos módulos.

```bash
python -m unittest discover -v
```
