import pandas as pd

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

