
import xml.etree.ElementTree as ET
import requests
import json
from weighted_graph import *
from reader import *


# implementação sem api
def get_relationship_graph(df):
    graph = Weighted_Graph()

    for _, linha in df.iterrows():
        print(linha)
        id_votacao = linha['idVotacao']
        voto = linha['voto']
        deputado_nome = linha['deputado_nome']

        graph.add_node(deputado_nome)
        
        outros_deputados = df[(df['idVotacao'] == id_votacao) & (df['deputado_nome'] != deputado_nome)]

        for _, outro in outros_deputados.iterrows():
            outro_deputado_nome = outro['deputado_nome']
            if outro['voto'] == voto:
                if not graph.there_is_edge(deputado_nome, outro_deputado_nome):
                    graph.add_two_way_edge(deputado_nome, outro_deputado_nome, 1)
                if graph.there_is_edge(deputado_nome, outro_deputado_nome):
                    graph.adj_list[deputado_nome][outro_deputado_nome] += 1
                    graph.adj_list[outro_deputado_nome][deputado_nome] += 1
    return graph

# implementação por api
def data_api_requests():
    print("Processando...")
    response = requests.get("https://dadosabertos.camara.leg.br/api/v2/votacoes")
    data = json.loads(response.text)
    dados = []

    for votacoes in data['dados']:
        id_votacao = votacoes['id']
        votacoes['id_votacao'] = id_votacao  # Adiciona o ID da votação como uma nova chave
        url = f"https://dadosabertos.camara.leg.br/api/v2/votacoes/{id_votacao}/votos"
        print(url)
        try:
            content = requests.get(url)
            vote_data = json.loads(content.text)
            if not vote_data['dados']:
                continue
            for voto in vote_data['dados']:
                voto['id_votacao'] = id_votacao  # Adiciona o ID da votação como uma nova chave
                dados.append(voto)
        except:
            print("Conteúdo indisponível")

    dados_final = pd.DataFrame(dados)
    graph = Weighted_Graph()

    for _, votacao in dados_final.iterrows():
        voto = votacao['tipoVoto']
        id_votacao = votacao['id_votacao']
        deputado_nome = votacao['deputado_']['nome']

        graph.add_node(deputado_nome)

        outros_deputados = dados_final[((dados_final['id_votacao'] == id_votacao) & dados_final['deputado_'].apply(lambda x: x['nome'] != deputado_nome))]

        for _, outro in outros_deputados.iterrows():
            outro_deputado_nome = outro['deputado_']['nome']
            
            if outro['tipoVoto'] == voto and not graph.there_is_edge(deputado_nome, outro_deputado_nome):
                graph.add_two_way_edge(deputado_nome, outro_deputado_nome, 1)
                
            if graph.there_is_edge(deputado_nome, outro_deputado_nome) and outro['tipoVoto'] == voto:
                graph.adj_list[deputado_nome][outro_deputado_nome] += 1
                graph.adj_list[outro_deputado_nome][deputado_nome] += 1

    return graph


def write_node_weight(graph, input_filename,output_filename):
        with open(output_filename, 'w', encoding='utf-8') as file:
            file.write(f"Numero de participantes:  {graph.node_count}\n")
            edge = 0
            cont = 0
            for node in graph.adj_list:
                file2 = open(input_filename, 'r', encoding='utf-8') 
                for line in file2:
                    if cont != 0:
                        content = line.strip().split(",")
                        deputado_nome1 = content[3]
                        if deputado_nome1 == node:
                            edge += 1
                    else:
                        cont += 1
                file.write(f"{node.replace(' ', '_')} {edge}\n")
                edge = 0
        file2.close()

def write_graph(graph, output_filename):
        with open(output_filename, 'w', encoding='utf-8') as file:
            file.write(f"{graph.node_count} {int((graph.edge_count/2))}\n")
            visited_edges = set()  # Keep track of visited edges
            for node1 in graph.adj_list:
                for node2, weight in graph.adj_list[node1].items():
                    edge = tuple(sorted([node1, node2]))  # Sort nodes to ensure consistent order
                    if edge not in visited_edges:
                        file.write(f"{node1.replace(' ', '_')} {node2.replace(' ', '_')} {int(weight/2)}\n")
                        visited_edges.add(edge)

reader = Reader()
graph = Weighted_Graph()
# MAIN POR API (papi)

input_file = "votacoesVotos-2023-clean.csv"
relationship_output = "./apifiles/relacionamento-deputados-2023-papi.csv"
influency_output = "./apifiles/influencia-deputados-papi.csv"
graph = data_api_requests()


### MAIN SEM API (sapi)

# input_file = "votacoesVotos-2023-clean.csv"
# relationship_output = "./resultfiles/relacionamento-deputados-2023-sapi.csv"
# influency_output = "./resultfiles/influencia-deputados-sapi.csv"
# df = pd.read_csv("votacoesVotos-2023-clean.csv")
# graph = get_relationship_graph(df)
write_node_weight(graph, input_file, influency_output)
write_graph(graph, relationship_output)
