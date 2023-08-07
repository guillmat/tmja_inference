import copy
import random

import networkx as nx
import osmnx as ox
import matplotlib.pyplot as plt
import copy

class Toy_instance:

    def __init__(self):
        #self.G_nx = ox.graph_from_place("Piedmont, CA, USA", network_type="drive")
        G_nx = ox.graph_from_place("Montmorency, France", network_type="drive")
        self.G_nx = nx.DiGraph(G_nx)
        self.prune_graph()
        print("nb_nodes = " + str(len(self.G_nx.nodes)))
        print("nb_edges = " + str(len(self.G_nx.edges)))
    def plot_graph(self):
        pos = nx.spring_layout(self.G_nx)
        nx.draw_networkx_nodes(self.G_nx, pos, node_size=10, alpha=0.9)

        # edges
        nx.draw_networkx_edges(self.G_nx, pos, width=1)

        plt.axis('off')
        plt.savefig('fig_mcy.png')
        #plt.show()

    def define_tmja(self, nb_trajectories):
        random.seed(4)
        for (u,v) in self.G_nx.edges():
            self.G_nx[u][v]['tmja'] = 0
        print(type(self.G_nx.nodes))
        nb_path = 0
        while nb_path < nb_trajectories:
            u = random.randint(0, len(self.G_nx.nodes)-1)
            v = random.randint(0, len(self.G_nx.nodes)-1)
            list_nodes = list(self.G_nx)
            s = list_nodes[u]
            t = list_nodes[v]
            if nx.has_path(self.G_nx, source=s, target=t):
                nb_path +=1
                sp = nx.shortest_path(self.G_nx, source=s, target=t, weight = 'length')
                for i in range(len(sp)-1):
                    self.G_nx[sp[i]][sp[i+1]]['tmja'] += 1
        curr_id = 0
        nb_non_set = 0
        for (u,v) in self.G_nx.edges():
            if self.G_nx[u][v]['tmja'] == 0:
                self.G_nx[u][v]['is_set'] = False
                nb_non_set +=1
            else:
                self.G_nx[u][v]['is_set'] = True
            self.G_nx[u][v]['id'] = curr_id
            curr_id += 1
        print("nb_non_set = " + str(nb_non_set/curr_id) + "%")

    def delete_tmja(self, pourc):
        edges_tmja = []
        for (u,v) in self.G_nx.edges():
            if self.G_nx[u][v]['tmja'] > 0:
                edges_tmja.append((u,v))
        print("nb_tmja before = " + str(len(edges_tmja)))
        sample_tmja = random.sample(edges_tmja, int(pourc*len(edges_tmja)))
        self.G_next = copy.deepcopy(self.G_nx)
        for (u_d, v_d) in sample_tmja:
            self.G_next[u_d][v_d]['tmja'] = -1
            self.G_next[u_d][v_d]['is_set'] = False



    def get_subgraph(self, nodes, curr_G):
        node_isolated = [x for x in nodes if curr_G.out_degree(x) == 0 and curr_G.in_degree(x) == 0]
        node_root = [x for x in nodes if curr_G.out_degree(x) > 0 and curr_G.in_degree(x) == 0]
        node_leaf = [x for x in nodes if curr_G.out_degree(x) == 0 and curr_G.in_degree(x) > 0]
        print("isolated = " + str(len(node_isolated)))
        print("root = " + str(len(node_root)))
        print("leaf = " + str(len(node_leaf)))
        to_delete = []
        for x in node_isolated:
            for (u,v) in curr_G.out_edges(x):
                if len(curr_G[u][v]) == 2:
                    break
            to_delete.append(x)
        for x in node_root:
            for (u,v) in curr_G.out_edges(x):
                if len(curr_G[u][v]) == 2:
                    break
            to_delete.append(x)
        for x in node_leaf:
            for (u,v) in curr_G.out_edges(x):
                if len(curr_G[u][v]) == 2:
                    break
            to_delete.append(x)
        subnodes = [x for x in curr_G.nodes() if x not in to_delete]
        return curr_G.subgraph(subnodes), len(to_delete)

    def prune_graph(self):
        nb_deleted_all = 0
        graph = self.G_nx
        nb_deleted = -1
        while nb_deleted != 0:
            graph, nb_deleted = self.get_subgraph(graph.nodes(), graph)
            nb_deleted_all += nb_deleted
        self.G_nx = graph
        print("we have pruned " + str(nb_deleted_all) + " nodes")
        return graph
