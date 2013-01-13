#!/usr/bin/env python
"""
The VidICN Model Solver

Liang Wang @ Dept. of Computer Science, University of Helsinki, Finland
2013.01.11
"""

import os
import sys
import time

# Import PuLP modeler functions
from pulp import *


class vidicn(object):
    """The vidicn LP solver"""
    def __init__(self):
        self.x = set(['1', '2'])
        self.lpfile = open('vidicn.lp', 'w')
        self.logf = None
        self.usedtime = time.time()
        pass

    def solve(self):
        # Create the 'prob' variable to contain the problem data
        self.problem = LpProblem("The vidicn LP Problem", LpMinimize)
        self.x_vars = LpVariable.dicts("x", self.x, 0.0, 100, LpContinuous)

        # Set objective, first function added to the prob
        print "Set objectives:", time.ctime()
        self.set_objective()

        # Set constraints
        self.set_memory_constraints()

        # The problem data is written to an .lp file
        self.problem.writeLP("vidicn.lp")
        # The problem is solved using PuLP's choice of Solver
        self.problem.solve(GLPK())

        self.usedtime = time.time() - self.usedtime
        print "Time overheads: %.3f s" % (self.usedtime)
        if self.logf is not None:
            self.logf.write("Time overheads: %.3f s\n" % (self.usedtime))
            self.logf.flush()
        pass

    def set_objective(self):
        self.problem += 0.013 * self.x_vars['1'] + 0.008 * self.x_vars['2'], "Intra- and inter-ISP traffic"
        pass

    def set_memory_constraints(self):
        self.problem += self.x_vars['1'] + self.x_vars['2'] == 100, "PercentagesSum"
        self.problem += 0.100*self.x_vars['1'] + 0.200*self.x_vars['2'] >= 8.0, "ProteinRequirement"
        self.problem += 0.080*self.x_vars['1'] + 0.100*self.x_vars['2'] >= 6.0, "FatRequirement"
        self.problem += 0.001*self.x_vars['1'] + 0.005*self.x_vars['2'] <= 2.0, "FibreRequirement"
        self.problem += 0.002*self.x_vars['1'] + 0.005*self.x_vars['2'] <= 0.4, "SaltRequirement"
        pass

    def set_natural_constraints(self):
        for p in self.path.keys():
            constraints = []
            for r in self.path[p]:
                p_r = '%i_%i' % (p, r)
                constraints.append( str(self.d_vars[p_r]) )
            self.lpfile.write('pnc_%i: %s <= 1.0\n' % (p, ' + '.join(constraints)))
            #self.prob += lpSum(constraints) <= 1.0, ("Path %i natural constraints" % p)
        pass

    def set_processing_constraints(self):
        for r in self.L.keys():
            constraints = []
            for p in self.path.keys():
                if r in self.path[p]:
                    p_r = '%i_%i' % (p, r)
                    constraints.append(self.d_vars[p_r] * self.v[p] / self.avgpkgsize)
            for p, q in self.match.keys():
                if r in self.path[p] and r in self.path[q]:
                    q_r = '%i_%i' % (q, r)
                    constraints.append(self.d_vars[q_r] * self.match[(p, q)])
            self.prob += lpSum(constraints) <= self.L[r], ("Router %i processing constraints" % r)
        pass

    def output_result(self):
        # The status of the solution is printed to the screen
        print "Status:", LpStatus[self.problem.status]
        # Each of the variables is printed with it's resolved optimum value
        for v in self.problem.variables():
            print "%s = %.2f" % (v.name, v.varValue)
        pass

    pass


if __name__ == "__main__":
    obj = vidicn()
    obj.solve()
    obj.output_result()
    sys.exit(0)
