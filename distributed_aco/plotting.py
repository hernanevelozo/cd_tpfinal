

import matplotlib.pyplot as plt # type: ignore
import numpy as np
import plotly.graph_objects as go # type: ignore
from .core.cidade import Cidade
from typing import List

import matplotlib # type: ignore
matplotlib.use('Agg')  # Define o backend para não-gráfico
import numpy as np

def plotar_solucao(cidades: List[Cidade], caminho: List[int], titulo: str):
    """
    Plota as cidades e o caminho encontrado com um estilo visual aprimorado (Matplotlib).
    """
    COR_PONTOS = '#003f5c'
    COR_INICIO = '#00a676'
    COR_ROTA = '#ffa600'
    COR_TEXTO = '#333333'

    fig, ax = plt.subplots(figsize=(14, 10))

    # Plota as cidades como pontos
    for i, cidade in enumerate(cidades):
        if i == caminho[0]:
            ax.scatter(cidade.x, cidade.y, c=COR_INICIO, s=250, zorder=5, label='Cidade Inicial', edgecolor='black', linewidth=1)
        else:
            ax.scatter(cidade.x, cidade.y, c=COR_PONTOS, s=150, zorder=5, edgecolor='white', linewidth=1)
        
        # --- MELHORIA AQUI: Adiciona um fundo para melhor legibilidade ---
        ax.text(cidade.x, cidade.y, f" {cidade.nome}", fontsize=9, color=COR_TEXTO,
                fontweight='bold', ha='left', va='bottom',
                bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', boxstyle='round,pad=0.2'))

    x_coords = [cidades[i].x for i in caminho]
    y_coords = [cidades[i].y for i in caminho]
    x_coords.append(cidades[caminho[0]].x)
    y_coords.append(cidades[caminho[0]].y)

    ax.plot(x_coords, y_coords, color=COR_ROTA, linewidth=2, linestyle='-',
            marker='o', markersize=4, markerfacecolor=COR_ROTA, alpha=0.8, label='Melhor Rota')

    ax.set_title(titulo, fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel("Longitude (Coordenada X)", fontsize=12)
    ax.set_ylabel("Latitude (Coordenada Y)", fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, linestyle='--', alpha=0.5, which='both')
    ax.legend()
    fig.tight_layout()

    nome_arquivo = "melhor_rota_estilizada.png"
    plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
    print(f"\n📊 Gráfico 2D estilizado salvo como '{nome_arquivo}'")
    plt.close()


def plotar_convergencia(historico_distancias: List[float]):
    """
    Plota o histórico da melhor distância encontrada ao longo das iterações.
    """
    if not historico_distancias:
        print("⚠️ Histórico de distâncias vazio, não foi possível gerar o gráfico de convergência.")
        return
        
    plt.figure(figsize=(12, 6))
    plt.plot(historico_distancias, color='#003f5c', linewidth=2,
             marker='o', markersize=5, markerfacecolor='#ffa600')
    plt.title("Convergência do Algoritmo ACO", fontsize=16, fontweight='bold')
    plt.xlabel("Iteração", fontsize=12)
    plt.ylabel("Melhor Distância Encontrada", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    nome_arquivo = "convergencia_aco.png"
    plt.savefig(nome_arquivo, dpi=300)
    print(f"📈 Gráfico de convergência salvo como '{nome_arquivo}'")
    plt.close()


def plotar_solucao_3d_plotly(cidades: List[Cidade], caminho: List[int], titulo: str):
    """
    Plota as cidades e o caminho em um gráfico 3D interativo usando Plotly.
    O eixo Z representa a ordem de visitação.
    """
    cidades_ordenadas = [cidades[i] for i in caminho]
    x_coords = [c.x for c in cidades_ordenadas]
    y_coords = [c.y for c in cidades_ordenadas]
    z_coords = list(range(len(cidades_ordenadas)))
    
    x_coords.append(cidades_ordenadas[0].x)
    y_coords.append(cidades_ordenadas[0].y)
    z_coords.append(0)

    # Prepara os textos que aparecem FIXOS no gráfico
    text_labels_fixos = [c.nome for c in cidades_ordenadas]
    # Prepara os textos que aparecem no HOVER (ao passar o mouse)
    text_labels_hover = [f"{c.nome}<br>Ordem: {i+1}" for i, c in enumerate(cidades_ordenadas)]

    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=x_coords, y=y_coords, z=z_coords,
        mode='lines',
        line=dict(color='#1f77b4', width=4),
        hoverinfo='none',
        name='Rota'
    ))

    fig.add_trace(go.Scatter3d(
        x=x_coords[:-1], y=y_coords[:-1], z=z_coords[:-1],
        mode='markers+text', # <--- MUDANÇA PRINCIPAL: Adiciona 'text'
        marker=dict(
            size=8,
            color=z_coords[:-1],
            colorscale='Viridis',
            opacity=0.9,
            showscale=True,
            colorbar=dict(title='Ordem de Visita')
        ),
        text=text_labels_fixos, # <--- Texto que aparece fixo
        textposition='top center',
        textfont=dict(size=10, color='#000000'),
        hovertext=text_labels_hover, # <--- Texto que aparece no hover
        hoverinfo='text',
        name='Cidades'
    ))

    fig.update_layout(
        title=dict(text=f'<b>{titulo}</b>', x=0.5, font=dict(size=20)),
        scene=dict(
            xaxis_title='Longitude (X)',
            yaxis_title='Latitude (Y)',
            zaxis_title='Sequência da Rota (Z)'
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        legend=dict(yanchor="top", y=0.9, xanchor="left", x=0.1)
    )
    
    nome_arquivo = "melhor_rota_3d_interativa.html"
    fig.write_html(nome_arquivo)
    print(f"🌍 Gráfico 3D interativo salvo como '{nome_arquivo}'")