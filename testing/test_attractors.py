import logic
from unittest import TestCase
import graphs
import sympy
from collections import namedtuple
import random
from attractors import find_num_attractors_onestage
from utility import binary_necklaces

ExperimentParameters = namedtuple("ExperimentParameters", "G T P n_attractors")


class TestAttractors(TestCase):
    def test_find_num_attractors_onestage(self):
        experiments = []
        tests_dict = dict() # keys are tuples of graph, T, P

        """test on known toy models"""
        G = graphs.Network(vertex_names=["A"], edges=[("A", "A")],
                           vertex_functions=[sympy.Nand])
        experiments.append(ExperimentParameters(G=G, T=1, P=1, n_attractors=0))
        experiments.append(ExperimentParameters(G=G, T=2, P=3, n_attractors=1))

        G = graphs.Network(vertex_names=["A"], edges=[("A", "A")],
                           vertex_functions=[sympy.And])
        experiments.append(ExperimentParameters(G=G, T=1, P=2, n_attractors=2))
        experiments.append(ExperimentParameters(G=G, T=3, P=1, n_attractors=1))

        G = graphs.Network(vertex_names=["A", "B"], edges=[("A", "B"), ("B", "A")],
                           vertex_functions=[sympy.Nand, sympy.And])
        experiments.append(ExperimentParameters(G=G, T=2, P=3, n_attractors=0))
        experiments.append(ExperimentParameters(G=G, T=4, P=2, n_attractors=1))
        experiments.append(ExperimentParameters(G=G, T=4, P=1, n_attractors=1))

        G = graphs.Network(vertex_names=["A", "B"], edges=[("A", "B"), ("B", "A")],
                           vertex_functions=[sympy.Nand, sympy.Nand])
        experiments.append(ExperimentParameters(G=G, T=1, P=3, n_attractors=2))
        experiments.append(ExperimentParameters(G=G, T=2, P=3, n_attractors=3))
        experiments.append(ExperimentParameters(G=G, T=15, P=15, n_attractors=3))

        G = graphs.Network(vertex_names=["A", "B"], edges=[("A", "B"), ("B", "A")],
                           vertex_functions=[lambda x: True, lambda x: False])
        experiments.append(ExperimentParameters(G=G, T=4, P=2, n_attractors=1))
        experiments.append(ExperimentParameters(G=G, T=1, P=2, n_attractors=1))

        G = graphs.Network(vertex_names=["A", "B", "C"], edges=[("A", "B"), ("B", "A"), ("C", "A")],
                           vertex_functions=[logic.SymmetricThresholdFunction.from_function(sympy.Nand, 2),
                                             logic.SymmetricThresholdFunction.from_function(sympy.Nand, 1),
                                             logic.SymmetricThresholdFunction.from_function(sympy.Nand, 0)])
        experiments.append(ExperimentParameters(G=G, T=1, P=3, n_attractors=3))
        experiments.append(ExperimentParameters(G=G, T=1, P=4, n_attractors=3))
        experiments.append(ExperimentParameters(G=G, T=2, P=3, n_attractors=3))
        experiments.append(ExperimentParameters(G=G, T=2, P=4, n_attractors=4))
        experiments.append(ExperimentParameters(G=G, T=3, P=4, n_attractors=4))

        G = graphs.Network(vertex_names=["A", "B", "C"], edges=[("A", "B"), ("B", "C"), ("C", "A")],
                           vertex_functions=[sympy.Nand]*3)
        experiments.append(ExperimentParameters(G=G, T=6, P=2, n_attractors=2))
        experiments.append(ExperimentParameters(G=G, T=10, P=10, n_attractors=2))
        experiments.append(ExperimentParameters(G=G, T=5, P=10, n_attractors=1))

        # acyclic, should have 2**#input_nodes attractors of length 1
        G = graphs.Network(vertex_names=["v1", "v2", "v3", "v4", "v5", "v6"],
                           edges=[("v1", "v4"), ("v2", "v4"), ("v1", "v5"), ("v4", "v6")],
                           vertex_functions=[lambda *args: sympy.Nand(*args)]*6)
        experiments.append(ExperimentParameters(G=G, T=1, P=10, n_attractors=8))
        experiments.append(ExperimentParameters(G=G, T=6, P=10, n_attractors=8))

        G = graphs.Network(vertex_names=["A1", "B1", "B2", "C1", "C2"],
                           edges=[("A1", "A1"), ("B1", "B2"), ("B2", "B1"), ("C1", "C2"), ("C2", "C1")],
                           vertex_functions=[sympy.And]*5)
        experiments.append(ExperimentParameters(G=G, T=1, P=10, n_attractors=8))
        experiments.append(ExperimentParameters(G=G, T=2, P=18, n_attractors=18))
        experiments.append(ExperimentParameters(G=G, T=3, P=40, n_attractors=20))  # offsets!

        for _ in range(5):
            size = 35
            G = graphs.Network(vertex_names=list(range(size)),
                               edges=[(i, random.choice(list(range(i+1, size)))) for i in range(size)
                                      if random.random() < 0.8 and i != size-1],
                               vertex_functions=[random.choice([sympy.And, sympy.Nand, sympy.Or, sympy.Xor])
                                                 for _ in range(size)])
            input_nodes = 0
            for v in G.vertices:
                is_input = True
                for e in G.edges:
                    if e[1] == v:
                        is_input = False
                        break
                if is_input:
                    input_nodes += 1
            attractor_number = 2**input_nodes
            experiments.append(ExperimentParameters(G=G, T=1, P=3, n_attractors=min(3, attractor_number)))
            experiments.append(ExperimentParameters(G=G, T=2, P=10, n_attractors=min(10, attractor_number)))
            experiments.append(ExperimentParameters(G=G, T=10, P=3, n_attractors=min(3, attractor_number)))

        # TODO: figure out how disjoint long attractors work together (multiplying doesn't account for offsets)
        # """test on basic semi-random networks: create connectivity components of acyclis networks and simple cycles"""
        # n_random_experiment = 0
        # while n_random_experiment < 10:
        #     n_components = random.randint(1, 3)
        #     attractor_number = 1
        #     max_attractor_len = 0
        #     cur_graph = None
        #     for n_component in range(n_components):  # TODO: change to graph union method
        #         comp_size = random.randint(1, 5)
        #         V = [i for i in range(comp_size)]
        #         E = []
        #         comp_type =random.choice(["cycle", "acyclic"])
        #         if comp_type == "acyclic":
        #             for i in range(len(V) - 1): # create only forward facing edges
        #                 for j in range(i+1, len(V)):
        #                     if random.random() <= 0.8:
        #                         E.append((V[i], V[j]))
        #             component_graph = graphs.Network(vertex_names=V, edges=E)
        #             restriction_level = random.choice([graphs.FunctionTypeRestriction.NONE,
        #                                                graphs.FunctionTypeRestriction.SYMMETRIC_THRESHOLD,
        #                                                graphs.FunctionTypeRestriction.SIMPLE_GATES])
        #             component_graph.randomize_functions(function_type_restriction=restriction_level)
        #             input_nodes = 0
        #             for v in V:
        #                 is_input = True
        #                 for e in E:
        #                     if e[1] == v:
        #                         is_input = False
        #                         break
        #                 if is_input:
        #                     input_nodes += 1
        #             attractor_number *= 2**input_nodes
        #             max_attractor_len = max(max_attractor_len, 1)
        #         elif comp_type == "cycle":
        #             """currently supports only a cycle of identity function, using a group theory theorem from
        #             https://www.quora.com/How-many-unique-binary-matrices-are-there-up-to-rotations-translations-and-flips
        #             , can later add negation cycles"""
        #             for i in range(len(V)):
        #                 E.append((V[i], V[(i + 1) % len(V)]))
        #             component_graph = graphs.Network(vertex_names=V, edges=E, vertex_functions=[sympy.And]*len(V))
        #             attractor_number *= binary_necklaces(len(V))
        #             max_attractor_len = max(max_attractor_len, len(V))
        #         cur_graph = component_graph if cur_graph is None else cur_graph + component_graph
        #     if attractor_number * len(cur_graph.vertices) * max_attractor_len <= 250:
        #         experiments.append(ExperimentParameters(G=cur_graph, T=max_attractor_len,
        #                                                 P=attractor_number + 1,
        #                                                 n_attractors=attractor_number))
        #         n_random_experiment += 1

        print "number of experiments={}".format(len(experiments))
        for i, experiment in enumerate(experiments):
            print "experiment #{}".format(i)
            print "n={}, T={}, P={}, expected_n_attractors={}".format(len(experiment.G.vertices),
                                                                   experiment.T, experiment.P, experiment.n_attractors)
            # continue
            n_attractors = find_num_attractors_onestage(G=experiment.G, max_len=experiment.T, max_num=experiment.P,
                                                        use_sat=False, verbose=False)  # require_result=experiment.n_attractors
            try:
                self.assertEqual(n_attractors, experiment.n_attractors)
            except AssertionError as e:
                print e
                print experiment.G
                raise e