
import xml.etree.ElementTree as ET
import requests
from weighted_graph import *
from reader import *
reader = Reader()

def get_relationship_graph(df):
    graph = Weighted_Graph()

    for _, linha in df.iterrows():
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


res = requests.get("https://dadosabertos.camara.leg.br/api/v2/votacoes?ordem=DESC&ordenarPor=dataHoraRegistro")
root = ET.fromstring(res.content)




# Ler os df do arquivo CSV utilizando o Pandas
df = pd.read_csv('votacoesVotos-2023-clean.csv')
# df = pd.read_csv("tester.csv")

# reader.set_relationship("tester.csv")

# Criar o graph ponderado
weighted_graph = get_relationship_graph(df)

# Salvar as informações em um novo arquivo CSV
data = []
for node1, edges in weighted_graph.adj_list.items():
    for node2, weight in edges.items():
        data.append([node1, node2, int(weight/2)])

df = pd.DataFrame(data, columns=['deputado1', 'deputado2', 'peso'])
df.to_csv('concordancia_deputados.csv', index=False)
