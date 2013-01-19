#!/usr/bin/env python
"""
The VidICN Model Solver

REMARK:
1. The unit used in the model is megabyte (MB)

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
P = 100     # Number of chunks in a file
K = 1       # Number of copies on the path
C = 100     # Cache size

LOG = "result_modeldynamic_partial"

# Help functions: Prepare model parameters before solving the LIP problem

def prepare_file_popularity():
    k = 0.513
    filePopularity = array([ k * x**(k - 1) * exp(-x**k) for x in range(50, N+50) ]) * 100
    return filePopularity

def prepare_filesize_distrib():
    random.seed(SEED + 5)
    fileSize = random.uniform(size=N) * 10 + 20
    return fileSize

def prepare_chunk_popularity():
    random.seed(SEED + 7)
    chunkPopularity = array([sort(x)[::-1] for x in random.uniform(size=(N, P))]) * 100
    #chunkPopularity = array([sort(random.weibull(1.0, P))[::-1] for x in range(N)]) * 100
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


# Model Solver

class ModelDynamic(object):
    """The vidicn LP solver"""
    def __init__(self):
        self.usedtime = time.time()
        pass

    def init_model(self):
        self.filePopularity = prepare_file_popularity()
        self.fileSize = prepare_filesize_distrib()
        self.chunkPopularity = prepare_chunk_popularity()
        self.chunkSize = prepare_chunksize_distrib(self.fileSize)
        self.cache = prepare_cachesize()
        self.Y = prepare_content_distrib_var()
        self.X = prepare_decision_var()
        self.req = (25, 11)
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

        # The problem data is written to an .lp file
        self.problem.writeLP(LOG + ".lp")
        # The problem is solved using PuLP's choice of Solver
        self.problem.solve(GLPK(options=['--mipgap','0.01', '--cuts']))

        self.usedtime = time.time() - self.usedtime
        print "Time overheads: %.3f s" % (self.usedtime)

        pass

    def set_objective(self):
        objective = []
        for i in range(N):
            for j in range(P):
                tmp1 = self.chunkSize[i,j] * self.chunkPopularity[i,j] * self.filePopularity[i]
                for k in range(M):
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
                    constraints.append(self.chunkSize[i,j] * self.x_vars[i_j_k])
            t, u = self.req
            constraints.append(self.chunkSize[t,u] * (1 - self.Y[t,u,k]))
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

    def output_result(self):
        # The status of the solution is printed to the screen
        print "Status:", LpStatus[self.problem.status]
        # Each of the variables is printed with it's resolved optimum value
        f = open(LOG + ".sol", "w")
        for v in self.problem.variables():
            f.write("%s = %.2f\n" % (v.name, v.varValue))
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
    obj = ModelDynamic()
    obj.init_model()
    obj.solve()
    obj.output_result()
    obj.output_chunk_info(obj.chunkSize, obj.chunkPopularity)

    sys.exit(0)
