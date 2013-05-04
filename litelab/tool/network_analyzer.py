#!/usr/bin/env python
#
# This script is used to analyse the network topology.
#
# Usage: network_analyzer.py topology_file
#
# Liang Wang @ Dept. of Computer Science, University of Helsinki, Finland
# 2013.05.02
#

import re
import os
import sys
import random
import networkx as nx


def parse_topology_file(ifn):
    G = nx.Graph()
    for line in open(ifn, 'r'):
        if line.startswith('#'):
            continue
        x = int(line.split('->')[0])
        y = int(line.split('->')[1].split('\t')[0])
        G.add_edge(x, y)
    return G

def node_with_highest_degree(G):
    node = G.nodes()[0]
    for n in G.nodes():
        if G.degree(n) > G.degree(node):
            node = n
    return node

def server_to_client(G, server, percent):
    dlist = []
    for n in G.nodes():
        if n != server:
            dlist.append(len(nx.shortest_path(G, server, n)))
    print "Avg.Hops (SERVER to ALL) = ", 1.0*sum(dlist) / len(dlist)

    dlist0 = []
    dlist1 = []
    cnum = int((len(G.nodes()) - 1) * percent)
    clients = random.sample(G.nodes(), cnum)
    for n in clients:
        dlist0.append(len(nx.shortest_path(G, server, n)))
        dlist1.append(nx.shortest_path(G, server, n))
    print "Avg.Hops (SERVER to Rdm %.1f%%) = %.4f" % (100*percent, 1.0*sum(dlist0) / len(dlist0))

    edge_set = set()
    tot_edge = 0.0
    node_set = set()
    tot_node = 0.0
    for path in dlist1:
        tot_edge += len(path) - 1
        tot_node += len(path)
        for i in range(len(path)-1):
            x, y = path[i], path[i+1]
            edge_set.add(tuple(sorted((x,y))))
            node_set.add(x)
            node_set.add(y)
    print "Edge_Overlap (SERVER to Rdm %.1f%%) = %.4f" % (100*percent,  (tot_edge - len(edge_set)) / tot_edge)
    print "Node_Overlap (SERVER to Rdm %.1f%%) = %.4f" % (100*percent,  (tot_node - len(node_set)) / tot_node)

    edge_traffic = 0.0
    for edge in G.neighbors(server):
        edge = tuple(sorted((server,edge)))
        if edge in edge_set:
            edge_traffic += 1
    print "Link_Traffic (SERVER to Rdm %.1f%%) = %.4f" % (100*percent,  edge_traffic / len(G.neighbors(server)))
    pass


if __name__=="__main__":
    G = parse_topology_file(sys.argv[1])
    server = node_with_highest_degree(G)
    print "nodes: %i\t edges: %i\t server_deg: %i" % \
        (len(G.nodes()), len(G.edges()), G.degree(server))
    server_to_client(G, server, 0.3)

    sys.exit(0)
