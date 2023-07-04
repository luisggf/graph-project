from weighted_graph import *

class Reader:
    def __init__(self) -> None:
        pass

    def file_treatment(self, filename, output_filename):
        columns = ["idVotacao", "voto", "deputado_id", "deputado_nome"]
        df = pd.read_csv(filename, sep=";")
        df = df[columns]
        df.to_csv(output_filename, index=False)
        print("Clean file: 'votacoesVotos-2023-clean.csv' created")

    def defrag_idVotes(self, filename):
        chunksize_list = []
        chunksize = 0
        df = pd.read_csv(filename)
        num_id = None
        for index, row in df.iterrows():
            if num_id != row['idVotacao']:
                num_id = row['idVotacao']
                chunksize_list.append(chunksize)
                chunksize = 1
            else:
                chunksize += 1
        chunksize_list.append(chunksize)
        chunksize_list.pop(0)
        return chunksize_list
        

    def create_partitions(self, filename, chunk_size_list):
        partition_counter = 1
        chunk_start = 0
        partitions = []
        df = pd.read_csv(filename)

        for chunk_size in chunk_size_list:
            chunk_end = chunk_start + chunk_size
            chunk = df.iloc[chunk_start:chunk_end]
            partition_filename = f'./partitions/partition-{partition_counter}.csv'
            chunk.to_csv(partition_filename, index=False)
            partitions.append(chunk)
            partition_counter += 1
            chunk_start = chunk_end

        combined_df = pd.concat(partitions, ignore_index=True)  # Combina os DataFrames da lista
        return combined_df
    
    

    def set_relationship_partitioned(self, list_df):
        graph = Weighted_Graph()
        compliance_list = []
        for _, row in list_df.iterrows():  
            dp_names = row['deputado_nome']
            graph.add_node(dp_names)

            if row['voto'] == "Sim":
                compliance_list.append(dp_names)

        for i in range(len(compliance_list)):
            for j in range(i+1, len(compliance_list)):
                name1 = compliance_list[i]
                name2 = compliance_list[j]
                if name1 != name2:
                    if not graph.there_is_edge(name1, name2):
                        graph.add_two_way_edge(name1, name2, 1)
                    graph.adj_list[name1][name2] += 1

        return graph



    def set_relationship(self, filename):
        graph_union = Weighted_Graph()
        print("Processando...")
        chunksize_list = self.defrag_idVotes(filename)
        # partitions = []  
        partitions = self.create_partitions(filename, chunksize_list)
        graph_partition = self.set_relationship_partitioned(partitions)
        graph_union = graph_union.union(graph_partition)
        self.create_file(graph_union)

        return graph_union

    def create_file(self, relationship_graph):
        with open("relationship_test.csv", 'w', encoding='utf-8') as arquivo:
            for node, neighbors in relationship_graph.adj_list.items():
                # line = f"{relationship_graph.node_count},{relationship_graph.edge_count},{relationship_graph.weight}\n"
                # arquivo.write(line)
                for neighbor, weight in neighbors.items():
                    linha = f"{node},{neighbor},{weight}\n"
                    arquivo.write(linha)
        print("O grafo foi escrito nos arquivos: ""relationship_test.csv""")

