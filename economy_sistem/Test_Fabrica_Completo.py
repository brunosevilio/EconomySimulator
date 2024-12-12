import pandas as pd

# Classes Básicas
class Produto:
    def __init__(self, nome, dificuldade, disponibilidade, mao_de_obra):
        self.nome = nome
        self.dificuldade = dificuldade
        self.disponibilidade = disponibilidade  # Disponível na natureza ou estoque inicial
        self.mao_de_obra = mao_de_obra  # Mão de obra alocada para o produto
    
    def __repr__(self):
        return (f"Produto({self.nome}, Dificuldade: {self.dificuldade}, "
                f"Disponibilidade: {self.disponibilidade}, Mão de Obra: {self.mao_de_obra})")

class Industria:
    def __init__(self, nome, produtividade):
        self.nome = nome
        self.produtividade = produtividade  # Produtividade da indústria
        self.produtos = []  # Lista de produtos que a indústria pode produzir
    
    def adicionar_produto(self, produto):
        self.produtos.append(produto)
    
    def produzir(self, estoque):
        """
        Produz produtos com base nos parâmetros fornecidos e atualiza o estoque.
        """
        for produto in self.produtos:
            capacidade_producao = (self.produtividade * produto.mao_de_obra) / produto.dificuldade
            quantidade_produzida = min(capacidade_producao, produto.disponibilidade)
            estoque.adicionar(produto.nome, quantidade_produzida)
            produto.disponibilidade -= quantidade_produzida

class Estoque:
    def __init__(self):
        self.produtos = {}  # Nome do produto -> Quantidade disponível
    
    def adicionar(self, nome, quantidade):
        if nome in self.produtos:
            self.produtos[nome] += quantidade
        else:
            self.produtos[nome] = quantidade
    
    def consumir(self, nome, quantidade):
        if nome in self.produtos and self.produtos[nome] >= quantidade:
            self.produtos[nome] -= quantidade
            return True
        return False  # Insuficiência no estoque
    
    def disponibilidade(self, nome):
        return self.produtos.get(nome, 0)
    
    def __repr__(self):
        return f"Estoque({self.produtos})"

# Função para inicializar indústrias e associar produtos
def inicializar_industrias_multietapas(tabelas, df_industrias):
    industrias = {}
    estoque = Estoque()
    
    for etapa, tabela in tabelas.items():
        for _, linha in tabela.iterrows():
            nome_industria = linha['Industria']
            
            # Obter produtividade da indústria do df_industrias
            if nome_industria not in industrias:
                produtividade = df_industrias.loc[
                    df_industrias['Industria'] == nome_industria, 'Produtividade'
                ].values
                produtividade = produtividade[0] if len(produtividade) > 0 else 0
                industrias[nome_industria] = Industria(nome_industria, produtividade)
            
            # Criar o produto e associá-lo à indústria
            produto = Produto(
                nome=linha['Produto'],
                dificuldade=linha['Dificuldade'],
                disponibilidade=linha.get('Disponibilidade', 0),
                mao_de_obra=linha['Mao_Obra']
            )
            industrias[nome_industria].adicionar_produto(produto)
    
    return industrias, estoque


# Função para calcular a demanda acumulada
def calcular_demanda_i(tabelas, industrias, populacao):
    demanda_acumulada = {}
    
    for tabela in tabelas.values():
        for _, linha in tabela.iterrows():
            produto = linha['Produto']
            if produto not in demanda_acumulada:
                demanda_acumulada[produto] = 0

    fator_populacao = populacao / 1000
    for tabela in tabelas.values():
        for _, linha in tabela.iterrows():
            produto = linha['Produto']
            demanda_popular = linha.get('Demanda_Popular', 0)
            if pd.notna(demanda_popular):
                demanda_acumulada[produto] += demanda_popular * fator_populacao

    for etapa in reversed(list(tabelas.keys())):
        tabela = tabelas[etapa]
        for _, linha in tabela.iterrows():
            produto = linha['Produto']
            demanda_direta = linha.get('Demanda', None)
            
            if pd.notna(demanda_direta):
                demanda_acumulada[produto] += demanda_direta
            
            materia_colunas = [col for col in tabela.columns if col.startswith("Materia")]
            qtd_colunas = [f"Qtd{col[-1]}" for col in materia_colunas]
            
            for materia_coluna, qtd_coluna in zip(materia_colunas, qtd_colunas):
                materia = linha.get(materia_coluna, None)
                qtd = linha.get(qtd_coluna, 0)
                if pd.notna(materia):
                    if materia not in demanda_acumulada:
                        demanda_acumulada[materia] = 0
                    demanda_acumulada[materia] += demanda_acumulada[produto] * qtd
    
    return demanda_acumulada

# Função para processar etapas considerando a demanda
def processar_etapa(industria, estoque, tabela, etapa, demanda_acumulada):
    materia_colunas = [col for col in tabela.columns if col.startswith("Materia")]
    qtd_colunas = [f"Qtd{col[-1]}" for col in materia_colunas]

    produtos_nao_produzidos = []

    for _, linha in tabela.iterrows():
        if linha['Industria'] != industria.nome:
            continue
        
        produto = linha['Produto']
        demanda = demanda_acumulada.get(produto, 0)
        
        if demanda == 0:
            continue
        
        insumos = [
            ('Agua', linha.get('Qtd1', 0)),
            ('Energia', linha.get('Qtd2', 0)),
        ]
        materias = [
            (linha.get(materia_coluna, None), linha.get(qtd_coluna, 0))
            for materia_coluna, qtd_coluna in zip(materia_colunas, qtd_colunas)
            if pd.notna(linha.get(materia_coluna))
        ]
        insumos.extend(materias)

        # Limitar a produção pela fórmula: Mao_de_Obra * Produtividade / Dificuldade
        producao_maxima = (industria.produtividade * linha['Mao_Obra']) / linha['Dificuldade']

        insumos_insuficientes = []
        for insumo, qtd in insumos:
            if pd.notna(insumo):
                disponivel = estoque.disponibilidade(insumo)
                qtd_necessaria = qtd * demanda
                if disponivel < qtd_necessaria:
                    insumos_insuficientes.append((insumo, qtd_necessaria - disponivel))
                producao_maxima = min(producao_maxima, disponivel / qtd if qtd > 0 else float('inf'))

        quantidade_a_produzir = min(producao_maxima, demanda)
        if quantidade_a_produzir > 0:
            for insumo, qtd in insumos:
                if pd.notna(insumo):
                    estoque.consumir(insumo, quantidade_a_produzir * qtd)
            estoque.adicionar(produto, quantidade_a_produzir)
        else:
            produtos_nao_produzidos.append((produto, insumos_insuficientes))

    return produtos_nao_produzidos

def calcular_demanda(tabelas, populacao):
    """
    Calcula a demanda acumulada para cada produto, incluindo Água e Energia.
    """
    demanda_acumulada = {}
    fator_populacao = populacao / 1000

    # Incluir demanda popular e direta
    for tabela in tabelas.values():
        for _, linha in tabela.iterrows():
            produto = linha['Produto']
            demanda_popular = linha.get('Demanda_Popular', 0)
            if pd.notna(demanda_popular):
                demanda_acumulada[produto] = demanda_acumulada.get(produto, 0) + demanda_popular * fator_populacao

    # Propagar demandas através das etapas
    for etapa in reversed(list(tabelas.keys())):
        tabela = tabelas[etapa]
        for _, linha in tabela.iterrows():
            produto = linha['Produto']
            demanda_direta = linha.get('Demanda', 0)
            if pd.notna(demanda_direta):
                demanda_acumulada[produto] = demanda_acumulada.get(produto, 0) + demanda_direta

            # Água e Energia (Insumo1 e Insumo2)
            insumo1, qtd1 = linha.get('Insumo1'), linha.get('Qtd1', 0)
            insumo2, qtd2 = linha.get('Insumo2'), linha.get('Qtd2', 0)
            if pd.notna(insumo1):
                demanda_acumulada[insumo1] = demanda_acumulada.get(insumo1, 0) + demanda_acumulada.get(produto, 0) * qtd1
            if pd.notna(insumo2):
                demanda_acumulada[insumo2] = demanda_acumulada.get(insumo2, 0) + demanda_acumulada.get(produto, 0) * qtd2

            # Outras matérias-primas
            materia_colunas = [col for col in tabela.columns if col.startswith("Materia")]
            qtd_colunas = [f"Qtd{col[-1]}" for col in materia_colunas]
            for materia_coluna, qtd_coluna in zip(materia_colunas, qtd_colunas):
                materia = linha.get(materia_coluna, None)
                qtd = linha.get(qtd_coluna, 0)
                if pd.notna(materia):
                    demanda_acumulada[materia] = demanda_acumulada.get(materia, 0) + demanda_acumulada.get(produto, 0) * qtd

    return demanda_acumulada

def calcular_produtividade_minima(tabelas, demanda_acumulada):
    """
    Calcula a produtividade mínima necessária para cada produto, incluindo Água e Energia.
    """
    produtividade_minima = pd.DataFrame(columns=["Industria", "Produto", "Produtividade_Minima"])
    
    for etapa, tabela in tabelas.items():
        for _, linha in tabela.iterrows():
            nome_industria = linha['Industria']
            produto = linha['Produto']
            mao_de_obra = linha['Mao_Obra']
            dificuldade = linha['Dificuldade']
            demanda_total = demanda_acumulada.get(produto, 0)
            
            if demanda_total > 0:
                produtividade_necessaria = (demanda_total * dificuldade) / mao_de_obra
                produtividade_minima = pd.concat([
                    produtividade_minima,
                    pd.DataFrame([{
                        "Industria": nome_industria,
                        "Produto": produto,
                        "Produtividade_Minima": produtividade_necessaria
                    }])
                ], ignore_index=True)

        # Incluir Água e Energia como produtos
        for insumo, coluna_qtd in [('Agua', 'Qtd1'), ('Energia', 'Qtd2')]:
            if insumo in demanda_acumulada:
                produtividade_minima = pd.concat([
                    produtividade_minima,
                    pd.DataFrame([{
                        "Industria": f"{insumo}_Industry",
                        "Produto": insumo,
                        "Produtividade_Minima": demanda_acumulada[insumo]
                    }])
                ], ignore_index=True)

    return produtividade_minima

def processar_industrias(tabelas, produtividade_minima):
    """
    Cria um DataFrame consolidado com informações das indústrias, incluindo Água e Energia.
    """
    industrias_info = []

    for etapa, tabela in tabelas.items():
        for industria_nome, grupo in tabela.groupby('Industria'):
            produtos = grupo['Produto'].tolist()
            insumos = set()

            # Identificar colunas de matérias-primas
            materia_colunas = [col for col in grupo.columns if col.startswith("Materia")]
            for _, linha in grupo.iterrows():
                for materia_coluna in materia_colunas:
                    materia_prima = linha.get(materia_coluna, None)
                    if pd.notna(materia_prima):
                        insumos.add(materia_prima)

            # Calcular produtividade da indústria
            max_produtividade = produtividade_minima[
                produtividade_minima['Industria'] == industria_nome
            ]['Produtividade_Minima'].max()

            taxa_pp = 0.5                              #############Setando Produtividade como metade da PP
            
            max_prod = max_produtividade if not pd.isna(max_produtividade) else 0
            industrias_info.append({
                "Industria": industria_nome,
                "Etapa": etapa,
                "Produtos": produtos,
                "Len_Produtos": len(produtos),
                "Insumos": list(insumos),
                "Len_Insumos": len(insumos),
                "Produtividade_Plena": max_prod,
                "Produtividade" : max_prod * taxa_pp    ############Setando Produtividade como metade da produtividade plena
            })

    # Adicionar Água e Energia como indústrias separadas
    for insumo in ['Agua', 'Energia']:
        if insumo in produtividade_minima['Produto'].values:
            industrias_info.append({
                "Industria": f"{insumo}_Industry",
                "Etapa": "Sem Etapa",
                "Produtos": [insumo],
                "Len_Produtos": 1,
                "Insumos": [],
                "Len_Insumos": 0,
                "Produtividade": produtividade_minima[
                    produtividade_minima['Produto'] == insumo
                ]['Produtividade_Minima'].max()
            })

    return pd.DataFrame(industrias_info)

# Função Main
def main():
    populacao = 193000
    
    tabelas = {
        'Extrativism': pd.read_excel('Data_Products.ods', sheet_name='Extrativism'),
        'Beneficiamento': pd.read_excel('Data_Products.ods', sheet_name='Beneficiamento'),
        'Processamento': pd.read_excel('Data_Products.ods', sheet_name='Processamento'),
        'Envase': pd.read_excel('Data_Products.ods', sheet_name='Envase'),
        'Bens': pd.read_excel('Data_Products.ods', sheet_name='Bens'),
        'Pesada': pd.read_excel('Data_Products.ods', sheet_name='Pesada'),
    }

    #Definindo produtividade#################

    demanda_acumulada = calcular_demanda(tabelas, populacao)
    produtividade_minima = calcular_produtividade_minima(tabelas, demanda_acumulada)
    
    industrias_info = processar_industrias(tabelas, produtividade_minima)

    # Salvar o resultado
    industrias_info.to_excel('industrias_info.ods', index=False)
    print("Arquivo 'industrias_info.ods' salvo com sucesso!")
    
    # Carregar df_industrias contendo a produtividade de cada indústria
    df_industrias = industrias_info
    
    industrias, estoque = inicializar_industrias_multietapas(tabelas, df_industrias)
    
    demanda_acumulada = calcular_demanda_i(tabelas, industrias, populacao)
    produtos_nao_produzidos_geral = []

    for etapa, tabela in tabelas.items():
        for nome, industria in industrias.items():
            if nome in tabela['Industria'].unique():
                if etapa in ['Extrativism']:
                    industria.produzir(estoque)
                else:
                    produtos_nao_produzidos = processar_etapa(industria, estoque, tabela, etapa, demanda_acumulada)
                    produtos_nao_produzidos_geral.extend(produtos_nao_produzidos)
    
    # Exibir o estoque final
    print("\nEstoque final:", estoque)

    # Exibir produtos não produzidos
    if produtos_nao_produzidos_geral:
        print("\n--- Produtos Não Produzidos ---")
        for produto, insumos in produtos_nao_produzidos_geral:
            print(f"Produto: {produto}")
            for insumo, deficit in insumos:
                print(f" - Insumo faltante: {insumo}, Quantidade insuficiente: {deficit}")

# Executar
main()

