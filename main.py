
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



import pandas as pd

def save_files_to_csv(graph):
    # Gerar o conteúdo do arquivo de arestas
    edges_content = []
    for node1, edges in graph.adj_list.items():
        for node2, weight in edges.items():
            edges_content.append([node1, node2, int(weight/2)])

    # Gerar o conteúdo do arquivo de participação
    participation_content = []
    for node, edges in graph.adj_list.items():
        num_participations = sum(weight for _, weight in edges.items())
        participation_content.append([node, num_participations])

    # Formatar nomes dos nós substituindo espaços por "_"
    edges_content = [[node1.replace(' ', '_'), node2.replace(' ', '_'), weight] for node1, node2, weight in edges_content]
    participation_content = [[node.replace(' ', '_'), num_participations] for node, num_participations in participation_content]

    # Criar DataFrame para as arestas
    df_edges = pd.DataFrame(edges_content, columns=['deputado1', 'deputado2', 'peso'])

    # Criar DataFrame para a participação
    df_participation = pd.DataFrame(participation_content, columns=['deputado', 'num_votacoes'])

    # Gerar o conteúdo do arquivo de arestas
    edges_content = [f"{node1} {node2} {weight}" for node1, node2, weight in edges_content]

    # Gerar o conteúdo do arquivo de participação
    participation_content = [f"{node} {num_participations}" for node, num_participations in participation_content]

    # Salvar os arquivos
    output_filename_edges = 'concordancia_deput_arestas.csv'
    output_filename_participation = 'concordancia_deput_participacao.csv'

    with open(output_filename_edges, 'w', encoding='utf-8') as file_edges:
        file_edges.write(f"{graph.node_count} {graph.edge_count}\n")
        file_edges.write('\n'.join(edges_content))

    with open(output_filename_participation, 'w', encoding='utf-8') as file_participation:
        file_participation.write(f"{graph.node_count}\n")
        file_participation.write('\n'.join(participation_content))

    print(f"Arquivos '{output_filename_edges}' e '{output_filename_participation}' salvos com sucesso.")

graph = Weighted_Graph()
graph = data_api_requests()
save_files_to_csv(graph)