from weighted_graph import *

graph = Weighted_Graph()

input_file = input("Informe o arquivo de votações: ")
relationship_output = "./apifiles/relacionamento-deputados-2023-papi.csv"
influency_output = "./apifiles/influencia-deputados-papi.csv"
# por API
graph.data_api_requests()
# sem API
# graph.get_relationship_graph(pd.read_csv(input_file, sep=';'))
graph.write_graph(influency_output)
graph.write_dpts_lenVotes(input_file, relationship_output)
print("O grafo foi escrito nos arquivos:", "\n-", relationship_output, "\n-", influency_output )
