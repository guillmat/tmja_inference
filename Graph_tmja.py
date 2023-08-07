import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from Toy_instance import *
import math



class Graph_tmja:

    def __init__(self, toy, path_to_graph, pourc, model):
        if toy:
            self.pourc = pourc
            self.nb_traj = 10000
            self.t_i = Toy_instance()
            self.t_i.define_tmja(self.nb_traj)
            self.t_i.delete_tmja(self.pourc)
            G = self.t_i.G_next
        else:
            G = nx.read_graphml(path_to_graph)
            self.create_list_edges()
            self.prune_graph()
        print(type(G))
        self.model = model
        self.G = G
        self.create_list_nodes()
        # self.duplicate_tmja()
        self.get_flows()
        self.print_graph_infos()

    def duplicate_tmja(self):
        nb_before = 0
        nb_ajout = 0
        for (u, v) in self.G.edges():
            if self.G[u][v]['tmja'] != -1:
                nb_before += 1
                if (v, u) in self.G.edges():
                    nb_ajout += 1
                    self.G[v][u]['tmja'] = self.G[u][v].get('tmja') / 2
                    self.G[u][v]['tmja'] = self.G[v][u].get('tmja')
        print("we had " + str(nb_before) + " tmja")
        print("we have added " + str(nb_ajout) + " tmja")

    def create_list_edges(self):
        curr_id = 0
        for (u, v) in self.G.edges():
            if len(self.G[u][v]) == 1 or (len(self.G[u][v]) == 2 and self.G[u][v]['tmja'] == 0):
                self.G[u][v]['tmja'] = -1
                self.G[u][v]['is_set'] = False
            else:
                self.G[u][v]['is_set'] = True
            self.G[u][v]['id'] = curr_id
            curr_id += 1

    def create_list_nodes(self):
        curr_id = 0
        for u in self.G.nodes():
            self.G.nodes[u]['id'] = curr_id
            self.G.nodes[u]['in_flows'] = []
            self.G.nodes[u]['out_flows'] = []
            curr_id += 1

    def get_subgraph(self, nodes, curr_G):
        node_isolated = [x for x in nodes if curr_G.out_degree(x) == 0 and curr_G.in_degree(x) == 0]
        node_root = [x for x in nodes if curr_G.out_degree(x) > 0 and curr_G.in_degree(x) == 0]
        node_leaf = [x for x in nodes if curr_G.out_degree(x) == 0 and curr_G.in_degree(x) > 0]
        print("isolated = " + str(len(node_isolated)))
        print("root = " + str(len(node_root)))
        print("leaf = " + str(len(node_leaf)))
        to_delete = []
        for x in node_isolated:
            for (u, v) in curr_G.out_edges(x):
                if len(curr_G[u][v]) == 2:
                    break
            to_delete.append(x)
        for x in node_root:
            for (u, v) in curr_G.out_edges(x):
                if len(curr_G[u][v]) == 2:
                    break
            to_delete.append(x)
        for x in node_leaf:
            for (u, v) in curr_G.out_edges(x):
                if len(curr_G[u][v]) == 2:
                    break
            to_delete.append(x)
        subnodes = [x for x in curr_G.nodes() if x not in to_delete]
        return curr_G.subgraph(subnodes), len(to_delete)

    def prune_graph(self):
        nb_deleted_all = 0
        graph = self.G
        nb_deleted = -1
        while nb_deleted != 0:
            graph, nb_deleted = self.get_subgraph(graph.nodes(), graph)
            nb_deleted_all += nb_deleted
        self.G = graph
        print("we have pruned " + str(nb_deleted_all) + " nodes")
        return graph

    def get_flows(self):
        for (u, v) in self.G.edges():
            self.G.nodes[u]['out_flows'].append(self.G[u][v]['id'])
            self.G.nodes[v]['in_flows'].append(self.G[u][v]['id'])

    def print_graph_infos(self):
        print("number of nodes : " + str(len(self.G.nodes())))
        print("number of edges : " + str(len(self.G.edges())))
        res = [x for x in self.G.nodes() if self.G.out_degree(x) > 0 and self.G.in_degree(x) == 0]
        print("number of roots : " + str(len(res)))
        nb_tmja = 0
        for (u, v) in self.G.edges():
            if self.G[u][v]['tmja'] != -1:
                nb_tmja += 1
        print("nb_tmja = " + str(nb_tmja / len(self.G.edges()) * 100) + "%")
        print("nb strongly connex component = " + str(nx.number_strongly_connected_components(self.G)))

    def test_graph(self):
        res = [x for x in self.G.nodes() if self.G.out_degree(x) == 0 and self.G.in_degree(x) > 0]
        # nb = nx.number_strongly_connected_components(self.G)

    def print_graph(self):
        pos = nx.spring_layout(self.G)  # Seed for reproducible layout
        nx.draw_networkx_nodes(self.G, pos, node_size = 10 )
        nx.draw_networkx_edges(self.G, pos)
        plt.show()

    def write_infered_tmja(self, sol_opt):
        for (u, v) in self.G.edges():
            self.G[u][v]['tmja'] = sol_opt.get_value("f_" + str(self.G[u][v]['id']))

    def get_pourcentage_tight(self, sol_opt):
        log = open("values_gap.csv", "w")
        log.write("i;value\n")
        log_z = open("z.csv", "w")
        log_z.write("i;value\n")
        epsilon = 0.001
        nb = 0
        values = []
        for u in self.G.nodes():
            diff_flows = sum(sol_opt.get_value("f_" + str(e_out)) for e_out in self.G.nodes[u]['out_flows']) - sum(
                sol_opt.get_value("f_" + str(e_in)) for e_in in self.G.nodes[u]['in_flows'])
            if abs(diff_flows - sol_opt.get_value("z_" + str(self.G.nodes[u]['id']))) < epsilon:
                nb += 1
            values.append(diff_flows)
            log.write(str(self.G.nodes[u]['id']) + ";" + str(
                abs(diff_flows - sol_opt.get_value("z_" + str(self.G.nodes[u]['id'])))) + "\n")
            log_z.write(
                str(self.G.nodes[u]['id']) + ";" + str(sol_opt.get_value("z_" + str(self.G.nodes[u]['id']))) + "\n")
        # plt.hist(values)
        # plt.show()
        log.close()
        log_z.close()
        return nb / len(self.G.nodes)

    def analyse_toy(self):
        log_0 = open("pourc_0_" + str(self.pourc) + "_" + str(self.nb_traj)+ "_" + str(self.model) + ".csv", "w")
        log_0.write("nb_non_set;nb_0;pourc_0\n")
        log = open("toy_diff_tmja_" + str(self.pourc) + "_" + str(self.nb_traj)+ "_" + str(self.model) + ".csv", "w")
        hist_diff = []
        log.write("i;tmja_avant;tmja_apres;diff_tmja\n")
        e = 0
        diff_0: int = 0
        mape = 0
        rmse = 0
        nb_points = 0
        for (u, v) in self.G.edges():
            self.G[u][v]['tmja_before'] = self.t_i.G_nx[u][v]['tmja']
            diff_tmja = abs(self.G[u][v]['tmja_before'] - self.G[u][v]['tmja'])
            self.G[u][v]['tmja_diff'] = diff_tmja
            if not self.G[u][v]['is_set']:
                e += 1
                if (self.G[u][v]['tmja_before'] != 0 and (diff_tmja != 0 or (diff_tmja == 0 and self.G[u][v]['tmja_before'] != 0))):
                    nb_points +=1
                    hist_diff.append(diff_tmja)
                    if diff_tmja == 0:
                        diff_0 += 1
                    log.write(
                        str(e) + ";" + str(self.G[u][v]['tmja_before']) + ";" + str(self.G[u][v]['tmja']) + ";" + str(
                            diff_tmja) + "\n")
                    mape += diff_tmja/self.G[u][v]['tmja_before']
                    rmse += diff_tmja*diff_tmja
        mape *= 100
        mape /= nb_points
        rmse /= nb_points

        rmse = math.sqrt(rmse)

        print("rmse = " + str(rmse))
        print("mape = " + str(mape))
        print("e = " + str(e))
        if e != 0:
            log_0.write(str(e) + ";" + str(diff_0) + ";" + str(diff_0 / e) + "\n")
        limit1, limit2 = 200, 1000
        binwidth1, binwidth2 = 1, 2

        counts, bins = np.histogram(hist_diff)
        plt.hist(bins[:-1], bins=bins, weights=counts)
        plt.xlabel('valeurs')
        plt.ylabel('nombres')
        plt.title('TMJA diff ' + str(self.pourc))
        plt.savefig('img/fig_hist_pourc=' + str(self.pourc) + "_" + str(self.nb_traj) + "_" + str(self.model)+".png")
        plt.clf()
