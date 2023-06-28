
import xml.etree.ElementTree as ET
import requests
import json
from weighted_graph import *
from reader import *

reader = Reader()

# implementação sem api
def get_relationship_graph(df):
    graph = Weighted_Graph()

    for _, linha in df.iterrows():
        print(linha)
        id_votacao = linha['idVotacao']
        voto = linha['voto']
        deputado_id = linha['deputado_id']
        deputado_nome = linha['deputado_nome']

        graph.add_node(deputado_nome)
        
        outros_deputados = df[(df['idVotacao'] == id_votacao) & (df['deputado_id'] != deputado_id)]

        for _, outro in outros_deputados.iterrows():
            outro_deputado_nome = outro['deputado_nome']
            
            if outro['voto'] == voto:
                graph.add_two_way_edge(deputado_nome, outro_deputado_nome, 1)

    return graph

# implementação por api
def data_api_requests():
    print("Processando...")
    response = requests.get("https://dadosabertos.camara.leg.br/api/v2/votacoes")
    data = json.loads(response.text)
    # list_votacoes = {}
    dados = []

    for votacoes in data['dados']:
        id_votacao = votacoes['id']
        url = f"https://dadosabertos.camara.leg.br/api/v2/votacoes/{id_votacao}/votos"
        print(url)

        try:
            content = requests.get(url)
            vote_data = json.loads(content.text)

            if not vote_data['dados']:
                continue
            
            dados.extend(vote_data['dados'])

        except:
            print("Conteúdo indisponível")

    dados_final = pd.DataFrame(dados)

    for index, votacao in dados_final.iterrows():
        print(votacao)
        voto = votacao['tipoVoto']
        deputado_nome = votacao['deputado_']['nome']

        graph.add_node(deputado_nome)

        # Filtrar os outros deputados com o mesmo voto
        outros_deputados = dados_final[(dados_final['tipoVoto'] == voto) & (dados_final['deputado_'].apply(lambda x: x['nome'] != deputado_nome))]

        for _, outro in outros_deputados.iterrows():
            outro_deputado_nome = outro['deputado_']['nome']

            graph.add_two_way_edge(deputado_nome, outro_deputado_nome, 1)
    return graph

# processamento e armazenamento dos arquivos
def save_files_to_csv(graph):
    # Salvar os arquivos
    output_filename_edges = 'concordancia_deput_arestas.csv'
    output_filename_participation = 'concordancia_deput_participacao.csv'
    
    # Gerar o conteúdo do arquivo de arestas
    edges_content = []
    for node1, edges in graph.adj_list.items():
        for node2, weight in edges.items():
            edges_content.append([node1.replace(' ', '_'), node2.replace(' ', '_'), int(weight/2)])

    with open(output_filename_edges, 'w', encoding='utf-8') as file_edges:
        file_edges.write(f"Nós: {graph.node_count} Arestas: {graph.edge_count}\n")
        for nodes in edges_content:
            file_edges.write(' '.join(map(str, nodes)) + '\n')

    with open(output_filename_participation, 'w', encoding='utf-8') as file_participation:
        file_participation.write(f"Numero de participantes das votações: {graph.node_count}\n")
        for node, num_participations in graph.adj_list.items():
            file_participation.write(f"{node.replace(' ', '_')} {len(num_participations)}\n")

    print(f"Arquivos '{output_filename_edges}' e '{output_filename_participation}' salvos com sucesso.")


graph = Weighted_Graph()
graph = data_api_requests()
save_files_to_csv(graph)