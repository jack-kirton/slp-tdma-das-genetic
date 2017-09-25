
from ga.genome import __get_two_hop_neighbourhood

def das(genome):
    g = genome.n
    success = True
    for n in g.nodes_iter():
        if n == g.graph["sink"]:
            continue
        elif g.node[n]["parent"] is None:
            print("{} has no parent".format(g.node[n]["coord"]))
            success = False
        elif g.node[n]["slot"] >= g.node[g.node[n]["parent"]]["slot"]:
            print("{} has slot greater than parent {}".format(g.node[n]["coord"], g.node[g.node[n]["parent"]]["coord"]))
            success = False
    return success

def collisions(genome):
    g = genome.n
    success = True
    skip = set()
    for n in g.nodes_iter():
        twohop = __get_two_hop_neighbourhood(g, n)
        for ne in twohop:
            if (ne, n) in skip or n == ne:
                continue
            else:
                skip.add((n, ne))
                if g.node[n]["slot"] == g.node[ne]["slot"]:
                    print("{} collides with {}".format(g.node[n]["coord"], g.node[ne]["coord"]))
                    success = False
    return success

