from Graph_tmja import *
from Model_inference import *
from Toy_instance import *

if __name__ == '__main__':
    model = "robust"
    p = 0.9
    G_tmja = Graph_tmja(True, None, p, model)
    m_i = Model_inference(G_tmja)
    sol_opt = m_i.create_model(model, 1000)
    G_tmja.write_infered_tmja(sol_opt)
    G_tmja.analyse_toy()
    tight_pour = G_tmja.get_pourcentage_tight(sol_opt)
    print("tight_pourc = " + str(tight_pour))




