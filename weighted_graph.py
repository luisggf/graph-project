import pandas as pd
import xml.etree.ElementTree as ET
import requests
import json

class Weighted_Graph:
    def __init__(self):
        self.adj_list = {}
        self.node_count = 0
        self.edge_count = 0

    def add_node(self, node):
        if node not in self.adj_list:
            self.adj_list[node] = {}
            self.node_count += 1

    def add_edge(self, node1, node2, weight):
        if node1 not in self.adj_list:
            self.add_node(node1)
        if node2 not in self.adj_list:
            self.add_node(node2)
        self.adj_list[node1][node2] = weight
        self.edge_count += 1

    def add_two_way_edge(self, node1, node2, weight):
        self.add_edge(node1, node2, weight)
        self.add_edge(node2, node1, weight)

    def remove_node(self, node):
        for node2 in self.adj_list:
            if node in self.adj_list[node2]:
                self.adj_list[node2].pop(node)
                self.edge_count -= 1
        self.edge_count -= len(self.adj_list[node])
        self.node_count -= 1
        self.adj_list.pop(node)

    def remove_edge(self, node1, node2):
        try:
            del self.adj_list[node1][node2]
            self.edge_count -= 1
        except KeyError as e:
            print(f"WARN: Node {e} does not exist")
        except ValueError as e:
            print(f"WARN: Edge {node1} -> {node2} does not exist")

    def there_is_edge(self, node1, node2):
        if node1 == node2:
            return False
        if node1 in self.adj_list and node2 in self.adj_list[node1]:
            return True
        return False

    def get_edge_weight(self, node1, node2):
        if node1 in self.adj_list and node2 in self.adj_list[node1]:
            return self.adj_list[node1][node2]
        return None

    def degree_out(self, node):
        return len(self.adj_list[node])
    
    def union(self, other_graph):
        result_graph = Weighted_Graph()

        for node in self.adj_list:
            result_graph.add_node(node)

        for node in other_graph.adj_list:
            if node not in result_graph.adj_list:
                result_graph.add_node(node)

        for node1 in self.adj_list:
            for node2, weight in self.adj_list[node1].items():
                result_graph.add_edge(node1, node2, weight)

        for node1 in other_graph.adj_list:
            for node2, weight in other_graph.adj_list[node1].items():
                if node1 not in result_graph.adj_list or node2 not in result_graph.adj_list[node1]:
                    result_graph.add_edge(node1, node2, weight)

        return result_graph
    
    def get_neighbors(self, node):
        try:
            return iter(self.adj_list[node])
        except KeyError:
            print("Node doesnt exist!")
            
    
    # implementação sem api, recebe grafo vazio e dataframe completo lido por arquivo csv e retorna o grafo pronto com todas relações e pesos
    def get_relationship_graph(self, df):
       for _, linha in df.iterrows():
           print(linha)
           id_votacao = linha['idVotacao']
           voto = linha['voto']
           deputado_nome = linha['deputado_nome']
           self.add_node(deputado_nome)
           outros_deputados = df[(df['idVotacao'] == id_votacao) & (df['deputado_nome'] != deputado_nome)]
           for _, outro in outros_deputados.iterrows():
               outro_deputado_nome = outro['deputado_nome']
               if outro['voto'] == voto:
                   if not self.there_is_edge(deputado_nome, outro_deputado_nome):
                       self.add_two_way_edge(deputado_nome, outro_deputado_nome, 1)
                   if self.there_is_edge(deputado_nome, outro_deputado_nome):
                       self.adj_list[deputado_nome][outro_deputado_nome] += 1
                       self.adj_list[outro_deputado_nome][deputado_nome] += 1
       return self
    

    # implementação por api recebe somente grafo vazio, dados são lidos por requisições a api e 
    # dados são coletados e usados para montar relações e pesos, por fim retorna o grafo
    def data_api_requests(self):
        print("Processando...")
        response = requests.get("https://dadosabertos.camara.leg.br/api/v2/votacoes?dataInicio=2023-01-01")
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

        # dados_final = pd.DataFrame(dados)

        for votacao in dados:
            voto = votacao['tipoVoto']
            id_votacao = votacao['id_votacao']
            deputado_nome = votacao['deputado_']['nome']

            self.add_node(deputado_nome)

            outros_deputados = [outro for outro in dados if outro['id_votacao'] == id_votacao and outro['deputado_']['nome'] != deputado_nome]

            for outro in outros_deputados:
                outro_deputado_nome = outro['deputado_']['nome']

                if outro['tipoVoto'] == voto and not self.there_is_edge(deputado_nome, outro_deputado_nome):
                    self.add_two_way_edge(deputado_nome, outro_deputado_nome, 1)

                if self.there_is_edge(deputado_nome, outro_deputado_nome) and outro['tipoVoto'] == voto:
                    self.adj_list[deputado_nome][outro_deputado_nome] += 1
                    self.adj_list[outro_deputado_nome][deputado_nome] += 1
        return self, dados

          
    # realiza leitura do grafo e então cria o arquivo no formato dp1_nome, votacoes_participadas
    def write_dpts_numVotes(graph, df, output_filename):
        with open(output_filename, 'w', encoding='utf-8') as file:
            file.write(f"Numero de participantes:  {graph.node_count}\n")
            vote_cont = 0
            for node in graph.adj_list:
                for votacao in df:
                    deputado_nome = votacao['deputado_']['nome']
                    if node == deputado_nome:
                        vote_cont += 1
                file.write(f"{node.replace(' ', '_')} {vote_cont}\n")
                vote_cont = 0

    # realiza leitura do grafo e então cria o arquivo no formato dp1_nome dp2_nome peso_entre_dpts
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
    
