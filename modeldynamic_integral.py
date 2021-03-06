#!/usr/bin/env python
"""
The VidICN Model Solver

REMARK:
1. The unit used in the model is megabyte (MB)

USAGE: app.py request_trace distribution_trace

Liang Wang @ Dept. of Computer Science, University of Helsinki, Finland
2013.01.11
"""

import os
import sys
import time

from numpy import *
from pulp import *


# Model constants

SEED = 123  # Random seed for the simulation
M = 5       # Number of routers
N = 100     # Number of files
P = 1       # Number of chunks in a file
K = 1       # Number of copies on the path
C = 50      # Cache size

GAP = 0.01   # MIP gap for the solver
LOG = "result_modeldynamic_integral"
TKN = time.strftime("%Y%m%d%H%M%S")

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

def prepare_chunk_popularity():
    chunkPopularity = ones([N, P])
    return chunkPopularity

def prepare_chunksize_distrib(fileSize):
    chunkSize = array([ [x / P] * P for x in fileSize ])
    return chunkSize

def prepare_cachesize():
    cache = zeros((M), dtype = float64) + C
    return cache

def prepare_content_distrib_var():
    Y = zeros((N, P, M), dtype = int64)
    return Y

def prepare_decision_var():
    X = [ "%i_%i_%i" % (i, j, k) for i in range(N) for j in range(P) for k in range(M) ]
    return X

def load_content_distrib_var(ifn):
    Y = zeros((N, P, M), dtype = int64)
    for line in open(ifn, 'r').readlines():
        x, y, z, c = line.strip().split()
        Y[int(x),0,int(z)] = int(c)
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
        self.usedtime = time.time()
        pass

    def init_model(self, req = None, varY = None):
        self.filePopularity = prepare_file_popularity()
        self.fileSize = prepare_filesize_distrib()
        self.chunkPopularity = prepare_chunk_popularity()
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
        self.problem = LpProblem("The vidicn LP Problem", LpMaximize)
        self.x_vars = LpVariable.dicts('x', self.X, lowBound = 0, upBound = 1, cat = LpInteger)

        # Set objective, first function added to the prob
        print "Set objectives:", time.ctime()
        self.set_objective()

        # Set constraints
        self.set_cache_constraints()
        self.set_ncopy_constraints()
        self.set_natural_constraints()

        # The problem data is written to an .lp file
        self.problem.writeLP(LOG + ".lp")
        # The problem is solved using PuLP's choice of Solver
        self.problem.solve(GLPK(options=['--mipgap', str(GAP), '--cuts']))

        self.usedtime = time.time() - self.usedtime
        print "Time overheads: %.3f s" % (self.usedtime)

        pass

    def set_objective(self):
        objective = []
        u, v = self.req
        for i in range(N):
            for j in range(P):
                tmp1 = self.chunkSize[i,j] * self.chunkPopularity[i,j] * self.filePopularity[i]
                for k in range(M):
                    if (i == u and j == v) or (self.Y[i,j,k] == 1):
                        i_j_k = '%i_%i_%i' % (i, j, k)
                        objective.append(tmp1 * (M - k) * self.x_vars[i_j_k])
        self.problem += lpSum(objective), "Maximize byte hit rate and footprint reduction"
        pass

    def set_cache_constraints(self):
        for k in range(M):
            constraints = []
            for i in range(N):
                for j in range(P):
                    i_j_k = '%i_%i_%i' % (i, j, k)
                    constraints.append(self.Y[i,j,k] * self.chunkSize[i,j] * self.x_vars[i_j_k])
            u, v = self.req
            u_v_k = '%i_%i_%i' % (u, v, k)
            constraints.append(self.chunkSize[u,v] * self.x_vars[u_v_k] * (1 - self.Y[u,v,k]))
            self.problem += lpSum(constraints) <= self.cache[k], ("cache %i capacity constraint" % k)
        pass

    def set_ncopy_constraints(self):
        for i in range(N):
            for j in range(P):
                constraints = []
                for k in range(M):
                    i_j_k = '%i_%i_%i' % (i, j, k)
                    constraints.append(self.x_vars[i_j_k])
                self.problem += lpSum(constraints) <= K, ("chunk %i_%i KCopy constraint" % (i,j))
        pass

    def set_natural_constraints(self):
        constraints = []
        u, v = self.req
        for i in range(N):
            for j in range(P):
                for k in range(M):
                    if not ( (i == u and j == v) or (self.Y[i,j,k] == 1) ):
                        i_j_k = '%i_%i_%i' % (i, j, k)
                        constraints.append(self.x_vars[i_j_k])
        self.problem += lpSum(constraints) == 0, "natural constraint"
        pass

    def output_result(self, ifn):
        # The status of the solution is printed to the screen
        print "Status:", LpStatus[self.problem.status]
        # Each of the variables is printed with it's resolved optimum value
        varX = zeros((N, P, M), dtype = int64)
        for v in self.problem.variables():
            _, i, j, k = v.name.split('_')
            varX[int(i), int(j), int(k)] = int(v.varValue)

        f1 = open(LOG + ".sol." + ifn, "w")
        f2 = open(LOG + ".dis." + ifn, "w")
        for i in range(N):
            for j in range(P):
                for k in range(M):
                    self.Y[i,j,k] = varX[i,j,k]
                    f1.write("%i %i %i %i\n" % (i, j, k, varX[i,j,k]))
                    f2.write("%i %i %i %i\n" % (i, j, k, self.Y[i,j,k]))
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
    reqs = load_request(sys.argv[1])[:20000:] # Liang: temp code
    varY = load_content_distrib_var(sys.argv[2])
    start_optimization(reqs, varY)
    sys.exit(0)
