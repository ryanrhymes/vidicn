#!/usr/bin/env python
"""
The VidICN Model Solver for tree topology

REMARK:
1. The unit used in the model is megabyte (MB)

USAGE: app.py request_trace distribution_trace

Liang Wang @ Dept. of Computer Science, University of Helsinki, Finland
2013.02.08
"""

import os
import sys
import time
import networkx as nx

from numpy import *
from pulp import *

# Model constants

SEED = 123   # Random seed for the simulation
M = None     # Number of routers
L = None     # Number of leaves
N = 100      # Number of files
P = 1        # Number of chunks in a file
K = 1        # Number of copies on the path
C = 50       # Cache size

GAP = 0.01   # MIP gap for the solver
LOG = "tree_modeldynamic_partial"
TKN = str(P) # time.strftime("%Y%m%d%H%M%S")

# Help functions: Prepare model parameters before solving the LIP problem

def weibull(k, lmd, x):
    k, lmd, x = (1.0 * k, 1.0 * lmd, 1.0 * x)
    y = (k/lmd) * (x/lmd)**(k - 1) * exp(-(x/lmd)**k)
    return y

def prepare_file_popularity():
    k = 0.513; lmd = 40.0
    filePopularity = array([ weibull(k, lmd, x) for x in range(10, N+10) ]) * 100
    return filePopularity

def prepare_filesize_distrib():
    random.seed(SEED + 5)
    fileSize = random.uniform(size=N) * 10 + 20
    return fileSize

def prepare_chunk_popularity_integral():
    chunkPopularity = ones([N, P])
    return chunkPopularity

def prepare_chunk_popularity_weibull():
    k = 0.5; lmd = 1.0;
    chunkPopularity = array([ [ weibull(k, lmd, 0.1+1.0*x/(P-1)) for x in range(P) ] for y in range(N)]) * 100
    return chunkPopularity

def prepare_chunk_popularity_linear():
    random.seed(SEED + 7)
    chunkPopularity = array([sort(x)[::-1] for x in random.uniform(size=(N, P))]) * 100
    return chunkPopularity

def prepare_chunksize_distrib(fileSize):
    chunkSize = array([ [x / P] * P for x in fileSize ])
    return chunkSize

def prepare_cachesize():
    cache = zeros((M), dtype = float64) + C
    return cache

def prepare_content_distrib_var():
    topology = construct_topology()
    M = len(topology.nodes())
    Y = zeros((N, P, M, M), dtype = int64)
    for i in range(N):
        for j in range(P):
            for k in range(M):
                Y[i,j,k,0] = 1
    return Y

def prepare_decision_var():
    X = [ "%i_%i_%i_%i" % (i, j, k, l) for i in range(N) for j in range(P) for k in range(M) for l in range(M) ]
    return X

def construct_topology():
    edgelist = [(0,1), (1,2), (1,3), (2,4), (2,5), (3,6), (3,7)]
    G = nx.Graph(edgelist)
    return G

def cost_func(G, x, y):
    c = len(nx.shortest_path(G, x, y))
    c = c+100 if x*y == 0 else c
    return c

def load_content_distrib_var(ifn):
    Y = zeros((N, P, M, M), dtype = int64)
    for line in open(ifn, 'r').readlines():
        w, x, y, z, c = line.strip().split()
        Y[int(w),int(x),int(y),int(z)] = int(c)
    return Y

def load_request(ifn):
    request = []
    for line in open(ifn, 'r').readlines():
        f, c = line.split()
        request.append([int(f), 0])
    return array(request)

def start_optimization(reqs, varY):
    obj = ModelDynamic()
    obj.init_model(None, varY)
    obj.output_chunk_info(obj.chunkSize, obj.chunkPopularity)
    i = 1
    for req in reqs:
        obj.reset_model(req, obj.Y)
        obj.solve()
        obj.output_result(str(i))
        i += 1
    pass


# Model Solver

class ModelDynamic(object):
    """The vidicn LP solver"""
    def __init__(self):
        pass

    def init_model(self, req = None, varY = None):
        global M, L
        self.topology = construct_topology()
        deg = math.log(len(self.topology.nodes()), 2)
        L = range(int(2**(deg-1)), int(2**deg))
        M = len(self.topology.nodes())
        self.filePopularity = prepare_file_popularity()
        self.fileSize = prepare_filesize_distrib()
        self.chunkPopularity = prepare_chunk_popularity_integral()
        self.chunkSize = prepare_chunksize_distrib(self.fileSize)
        self.cache = prepare_cachesize()
        self.X = prepare_decision_var()
        self.Y = varY
        self.req = req
        pass

    def reset_model(self, req, varY):
        self.req = req
        self.Y = varY
        pass

    def solve(self):
        # Create the 'prob' variable to contain the problem data
        self.problem = LpProblem("The vidicn LP Problem", LpMinimize)
        self.x_vars = LpVariable.dicts('x', self.X, lowBound = 0, upBound = 1, cat = LpInteger)

        # Set objective, first function added to the prob
        print "Set objectives:", time.ctime()
        self.set_objective()

        # Set constraints
        self.set_cache_constraints()
        self.set_ncopy_constraints()
        self.set_server_constraints()
        self.set_natural_constraints_1()
        self.set_natural_constraints_2()

        # The problem data is written to an .lp file
        self.problem.writeLP(LOG + ".lp." + TKN)
        # The problem is solved using PuLP's choice of Solver
        self.problem.solve(GLPK(options=['--mipgap',str(GAP), '--cuts']))

        pass

    def set_objective(self):
        objective = []
        u, v = self.req
        for i in range(N):
            for j in range(P):
                tmp1 = self.chunkSize[i,j] * self.chunkPopularity[i,j] * self.filePopularity[i]
                for k in L:
                    if (i == u and j == v) or (len(where(self.Y[i,j,k]==1)[0]) != 0):
                        for l in range(M):
                            i_j_k_l = '%i_%i_%i_%i' % (i, j, k, l)
                            objective.append(tmp1 * cost_func(self.topology, k, l) * self.x_vars[i_j_k_l])
        self.problem += lpSum(objective), "Maximize byte hit rate and footprint reduction"
        pass

    def set_cache_constraints(self):
        for k in range(1, M):
            constraints = []
            for i in range(N):
                for j in range(P):
                    i_j_k_k = '%i_%i_%i_%i' % (i, j, k, k)
                    constraints.append(self.chunkSize[i,j] * self.x_vars[i_j_k_k])
            u, v = self.req
            u_v_k_k = '%i_%i_%i_%i' % (u, v, k, k)
            constraints.append(self.chunkSize[u,v] * self.x_vars[u_v_k_k] * (1 - self.Y[u,v,k,k]))
            self.problem += lpSum(constraints) <= self.cache[k], ("cache %i capacity constraint" % k)
        pass

    def set_ncopy_constraints(self):
        for i in range(N):
            for j in range(P):
                constraints = []
                for k in range(1, M):
                    i_j_k_k = '%i_%i_%i_%i' % (i, j, k, k)
                    constraints.append(self.x_vars[i_j_k_k])
                self.problem += lpSum(constraints) <= K, ("chunk %i_%i KCopy constraint" % (i,j))
        pass

    def set_server_constraints(self):
        constraints = []
        for i in range(N):
            for j in range(P):
                i_j_0_0 = '%i_%i_0_0' % (i, j)
                self.problem += self.x_vars[i_j_0_0] == 1, ("server constraint %i_%i" % (i,j))
        pass

    def set_natural_constraints_1(self):
        for i in range(N):
            for j in range(P):
                for k in range(M):
                    for l in range(M):
                        i_j_k_l = '%i_%i_%i_%i' % (i, j, k, l)
                        i_j_l_l = '%i_%i_%i_%i' % (i, j, l, l)
                        self.problem += self.x_vars[i_j_k_l] <= self.x_vars[i_j_l_l], ("natural constraint 1 %i_%i_%i_%i" % (i,j,k,l))
        pass

    def set_natural_constraints_2(self):
        for i in range(N):
            for j in range(P):
                for k in L:
                    constraints = []
                    for l in range(M):
                        i_j_k_l = '%i_%i_%i_%i' % (i, j, k, l)
                        constraints.append(self.x_vars[i_j_k_l])
                    self.problem += lpSum(constraints) >= 1, ("natural constraint 2 %i_%i_%i_%i" % (i,j,k,l))
        pass

    def output_result(self, ifn):
        # The status of the solution is printed to the screen
        print "Status:", LpStatus[self.problem.status]
        # Each of the variables is printed with it's resolved optimum value
        varX = zeros((N, P, M, M), dtype = int64)
        for v in self.problem.variables():
            _, i, j, k, l = v.name.split('_')
            varX[int(i), int(j), int(k), int(l)] = int(v.varValue)

        f1 = open(LOG + ".sol." + ifn, "w")
        f2 = open(LOG + ".dis." + ifn, "w")
        for i in range(N):
            for j in range(P):
                for k in range(M):
                    for l in range(M):
                        self.Y[i,j,k,l] = varX[i,j,k,l]
                        f1.write("%i %i %i %i %i\n" % (int(i), int(j), int(k), int(l), int(varX[i,j,k])))
                        f2.write("%i %i %i %i %i\n" % (int(i), int(j), int(k), int(l), int(self.Y[i,j,k])))
        pass

    def output_chunk_info(self, chunkSize, chunkPopularity):
        f = open(LOG + ".chunk", "w")
        for i in range(N):
            for j in range(P):
                f.write("%i %i %f %f\n" % (i, j, chunkSize[i][j], chunkPopularity[i][j]))
        pass

    pass


# Main function, start the solver here. Let's rock!

if __name__ == "__main__":
    reqs = load_request(sys.argv[1])[:10:] # Liang: temp code
    #varY = load_content_distrib_var(sys.argv[2])
    varY = prepare_content_distrib_var()
    start_optimization(reqs, varY)
    sys.exit(0)