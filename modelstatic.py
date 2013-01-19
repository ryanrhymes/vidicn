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


# Help functions: Prepare model parameters before solving the LIP problem

def prepare_file_popularity():
    filePopularity = sort(random.weibull(0.513, N))[::-1]
    return filePopularity

def prepare_filesize_distrib():
    fileSize = random.uniform(size=N) * 10 + 20
    return fileSize

def prepare_chunk_popularity():
    #chunkPopularity = array([sort(x)[::-1] for x in random.uniform(size=(N, P))])
    chunkPopularity = array([sort(random.weibull(1.0, P))[::-1] for x in range(N)])
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

class ModelStatic(object):
    """The vidicn LP solver"""
    def __init__(self):
        self.usedtime = time.time()
        pass

    def init_model(self):
        random.seed(SEED)
        self.filePopularity = prepare_file_popularity()
        self.fileSize = prepare_filesize_distrib()
        self.chunkPopularity = prepare_chunk_popularity()
        self.chunkSize = prepare_chunksize_distrib(self.fileSize)
        self.cache = prepare_cachesize()
        self.Y = prepare_content_distrib_var()
        self.X = prepare_decision_var()
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
        self.problem.writeLP("result_modelstatic.lp")
        # The problem is solved using PuLP's choice of Solver
        #self.problem.solve(COIN())
        self.problem.solve(GLPK())

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
        self.problem += lpSum(objective), "Maximize byt hit rate and footprint reduction"
        pass

    def set_cache_constraints(self):
        for k in range(M):
            constraints = []
            for i in range(N):
                for j in range(P):
                    i_j_k = '%i_%i_%i' % (i, j, k)
                    constraints.append(self.chunkSize[i,j] * self.x_vars[i_j_k])
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
        f = open("result_modelstatic.sol", "w")
        for v in self.problem.variables():
            f.write("%s = %.2f\n" % (v.name, v.varValue))
        pass

    pass


# Main function, start the solver here. Let's rock!

if __name__ == "__main__":
    obj = ModelStatic()
    obj.init_model()
    obj.solve()
    obj.output_result()

    sys.exit(0)
