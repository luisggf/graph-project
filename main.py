from weighted_graph import *

# declarações e inicializações
graph = Weighted_Graph()
votes_output = "./apifiles/votacoesVotos-deputados.csv"
relationship_output = "./apifiles/votacoesVotos-grafo.csv"

# recolhe dados (tupla) gerados pela api (grafo completo e dados validos)
data = graph.data_api_requests()

# faz arquivo das relações entre deputados (baseado no grafo preenchido)
data[0].write_graph(relationship_output)

# faz arquivo do deputado seguido do numero de pautas participadas por ele de acordo com o que foi requerido na api
data[0].write_dpts_numVotes(data[1], votes_output)

print("O grafo foi escrito nos arquivos:", "\n-", votes_output, "\n-", relationship_output )
