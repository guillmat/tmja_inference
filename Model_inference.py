import time
from docplex.mp.model import Model


class Model_inference:

    def __init__(self, G):
        self.G_tmja = G

    def create_model(self, model, time_limit):
        start_time = time.time()
        G = self.G_tmja.G
        m = Model(name='tmja_inference')

        f_dict = [e for e in range(len(self.G_tmja.G.edges()))]
        f = m.continuous_var_dict(f_dict, name="f")

        z_bar = m.continuous_var(name = "z_bar")
        for (u, v) in G.edges():
            if G[u][v]['is_set']:
                #print(G[u][v]['tmja'])
                f[G[u][v]['id']].ub = G[u][v]['tmja']
                f[G[u][v]['id']].lb = G[u][v]['tmja']
                #print(G[u][v]['tmja'])

        z_dict = [v for v in range(len(self.G_tmja.G.nodes()))]
        z = m.continuous_var_dict(z_dict, name="z")

        #expr_min = m.sum(z[v] for v in z_dict)
        if model == "robust":
            m.minimize(z_bar)
        elif model == "sum":
            m.minimize(m.sum(z[i] for i in z_dict))


        #tmja = m.add_constraints((f[G[u][v]['id']] == G[u][v]['tmja'] for (u,v) in G.edges() if G[u][v]['is_set']), names="tmja")
        #for u in G.nodes():
        #   print("---")
        #    print(G.nodes[u]['out_flows'])
        #    print(G.nodes[u]['in_flows'])


        #flow_constraint = m.add_constraints((m.sum(f[e_out] for e_out in G.nodes[u]['out_flows']) == z[G.nodes[u]['id']]) for u in G.nodes())
        flow_constraint = m.add_constraints((m.sum(f[e_out] for e_out in G.nodes[u]['out_flows']) - m.sum(f[e_in] for e_in in G.nodes[u]['in_flows']) <= z[G.nodes[u]['id']]) for u in G.nodes())

        z_bar_constraint = m.add_constraints(z_bar >= z[v] for v in z_dict)

        #m.context.cplex_parameters.timelimit = time_limit - (time.time() - start_time)
        #m.parameters.mip.tolerances.mipgap = 0.0001
        sol_opt = m.solve(log_output=False)
        if sol_opt is None:
            print("tmja inference INFEASIBLE")
            return
        #m.print_solution(print_zeros=False)

        return sol_opt

    '''
    def time_is_elapsed(self, start_time, time_limit):
        if time.time() - start_time > time_limit:
            return True
        return False
    '''