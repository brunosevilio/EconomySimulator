import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def construir_grafo_producao(tabelas):
    """
    Constrói o grafo das relações produtivas a partir das tabelas de dados.
    
    Args:
        tabelas (dict): Dicionário contendo os DataFrames com as informações de produção.
    
    Returns:
        G (networkx.DiGraph): Grafo dirigido das relações produtivas.
    """
    G = nx.DiGraph()  # Grafo dirigido
    
    for etapa, tabela in tabelas.items():
        for _, linha in tabela.iterrows():
            produto_final = linha['Produto']
            
            # Adicionar o nó do produto final
            G.add_node(produto_final, etapa=etapa)
            
            # Processar matérias-primas
            materia_colunas = [col for col in tabela.columns if col.startswith("Materia")]
            for materia_coluna in materia_colunas:
                materia_prima = linha.get(materia_coluna, None)
                if pd.notna(materia_prima):
                    # Adicionar o nó da matéria-prima e a aresta
                    G.add_node(materia_prima)
                    G.add_edge(materia_prima, produto_final)
    
    return G
def exibir_grafo_com_etapas_highlight_centralizado(G, produtos_destacados, titulo="Fluxo Produtivo com Destaque"):
    """
    Exibe o grafo das relações produtivas organizando os produtos por etapas produtivas,
    com espaçamento ajustado, nós centralizados e produtos destacados em vermelho.
    
    Args:
        G (networkx.DiGraph): Grafo dirigido das relações produtivas.
        produtos_destacados (list): Lista de produtos para destacar no grafo.
        titulo (str): Título do gráfico.
    """
    # Atribuir etapa padrão para nós sem etapa
    etapas = nx.get_node_attributes(G, 'etapa')
    for no in G.nodes:
        if no not in etapas:
            etapas[no] = "Sem Etapa"
    nx.set_node_attributes(G, etapas, "etapa")

    # Definir a sequência desejada de etapas
    sequencia_etapas = ['Extrativism', 'Beneficiamento', 'Processamento', 'Envase', 'Bens', 'Pesada', 'Sem Etapa']
    etapas_unicas = [etapa for etapa in sequencia_etapas if etapa in etapas.values()]

    # Criar posição personalizada para o layout com centralização
    pos = {}
    spacing_vertical = 3  # Espaçamento vertical entre as linhas
    max_nodes_in_line = max(
        len([n for n, e in etapas.items() if e == etapa])
        for etapa in etapas_unicas
    )
    for i, etapa in enumerate(etapas_unicas):
        # Filtrar os nós dessa etapa
        nos_etapa = [n for n, e in etapas.items() if e == etapa]
        num_nos = len(nos_etapa)
        offset = (max_nodes_in_line - num_nos) / 2  # Centralização
        for j, no in enumerate(nos_etapa):
            pos[no] = ((j + offset) * 5, -i * spacing_vertical)

    # Garantir que todos os nós tenham uma posição
    for no in G.nodes:
        if no not in pos:
            pos[no] = (0, -len(etapas_unicas) * spacing_vertical)  # Colocar nós sem posição no final

    # Destacar produtos na lista
    node_colors = [
        "red" if node in produtos_destacados else "lightblue"
        for node in G.nodes
    ]

    # Configurações do gráfico
    fig, ax = plt.subplots(figsize=(16, 10))
    nx.draw(
        G, pos, with_labels=True, ax=ax, node_size=2000, node_color=node_colors,
        font_size=20, font_weight="bold", arrowsize=15, edge_color="gray"
    )
    
    # Ajustar limites e título
    ax.set_title(titulo, fontsize=16)
    ax.margins(0.2)  # Margem extra ao redor do gráfico
    plt.tight_layout()
    
    # Habilitar zoom e interatividade
    def on_click(event):
        if event.button == 'up':  # Zoom in
            ax.set_xlim(ax.get_xlim()[0] / 1.2, ax.get_xlim()[1] / 1.2)
            ax.set_ylim(ax.get_ylim()[0] / 1.2, ax.get_ylim()[1] / 1.2)
        elif event.button == 'down':  # Zoom out
            ax.set_xlim(ax.get_xlim()[0] * 1.2, ax.get_xlim()[1] * 1.2)
            ax.set_ylim(ax.get_ylim()[0] * 1.2, ax.get_ylim()[1] * 1.2)
        plt.draw()

    fig.canvas.mpl_connect('scroll_event', on_click)
    plt.show()

def main_grafo_producao_com_highlight(estoque):
    """
    Cria um grafo das relações produtivas destacando produtos específicos e com nós centralizados.
    
    Args:
        estoque (dict): Dicionário do estoque contendo os nomes dos produtos e quantidades.
    """
    # Obter lista de produtos para destaque
    produtos_destacados = list(estoque.keys())

    # Configuração inicial: carregar tabelas de dados
    tabelas = {
        'Extrativism': pd.read_excel('Data_Products.ods', sheet_name='Extrativism'),
        'Beneficiamento': pd.read_excel('Data_Products.ods', sheet_name='Beneficiamento'),
        'Processamento': pd.read_excel('Data_Products.ods', sheet_name='Processamento'),
        'Envase': pd.read_excel('Data_Products.ods', sheet_name='Envase'),
        'Bens': pd.read_excel('Data_Products.ods', sheet_name='Bens'),
        'Pesada': pd.read_excel('Data_Products.ods', sheet_name='Pesada'),
    }

    # Construir o grafo
    grafo_producao = construir_grafo_producao(tabelas)
    
    # Exibir o grafo com os nós centralizados e destacados
    exibir_grafo_com_etapas_highlight_centralizado(
        grafo_producao, produtos_destacados,
        titulo="Fluxo Produtivo com Destaque e Centralização"
    )

# Exemplo de uso com o estoque fornecido
estoque = {'Agua': 9999585776.194927, 'Energia': 1999808431.8397954, 'Bovino': 1999999594.7, 'Ave': 3333332947.3333335, 'Graos': 4999998784.099999, 'Frutas': 4999999594.7, 'Vegetal': 4999999459.6, 'Flor': 1666666634.2426667, 'Cana': 4999999530.624, 'Canna': 3333333329.4733334, 'Algodao': 4999998670.23, 'Madeira-resina': 3333332692.148733, 'Madeira-tora': 4999944255.424, 'Ouro-ore': 3333333333.3333335, 'Cobre-ore': 3333333143.2476335, 'Ferro-ore': 3333330676.8755436, 'Aluminio-ore': 3333328197.6033335, 'Titanio-ore': 3333333333.3333335, 'Cobalto': 3333333328.1609335, 'Limestone': 3333318750.2533336, 'Agregados': 3333181741.6763334, 'Calcario': 3333333331.0173335, 'Enxofre': 3333333327.5433335, 'Sal': 4999999938.82672, 'Uranio': 3333333333.3333335, 'Petroleo': 1999999585.1465, 'Carvao': 3333330025.2370987, 'Carvao-pro': 0.0, 'Diesel': 0.0, 'Gasolina': 0.0, 'Carne-cons': 0.0, 'Ave-cons': 0.0, 'Frutas-cons': 0.0, 'Graos-cons': 0.0, 'Vegetais-cons': 0.0, 'Aluminio': 5.684341886080802e-14, 'Cobre': 0.0, 'Ferro': 0.0, 'Areia': 0.0, 'Calcario-pro': 0.0, 'Cobalto-pro': 0.0, 'Enxofre-pro': 0.0, 'Limestone-pro': 0.0, 'Sal-refinado': 0.0, 'Cachaça': 0.0, 'Especiaria': 0.0, 'Etanol': 0.0, 'Açucar': 0.0, 'Ganja': 6.616929226765933e-14, 'Borracha': 0.0, 'Papel': 0.0, 'Resina': 0.0, 'Madeira-barata': 3.5491609651217004e-12, 'Madeira-boa': 9.78772618509538e-13, 'Tecido': 0.0, 'Polimero': 0.0, 'Poliresina': 2.4158453015843406e-13, 'Latao': 0.0, 'Ferro-aluminio': 0.0, 'Condutora-sim': 0.0, 'Soda': 0.0, 'Vidro': 0.0}
main_grafo_producao_com_highlight(estoque)
