from __future__ import division

import networkx as nx

from ga.restricted_eval import restricted_eval

# class Topology(object):
    # def __init__(self, sink=None, source=None):
        # self._nodes = {}
        # self._edges = []
        # self._sink = sink
        # self._source = source

    # @property
    # def nodes(self):
        # return self._nodes

    # @property
    # def edges(self):
        # return self._edges


# class GridTopology(Topology):
    # def __init__(self, width, height, sink=None, source=None):
        # sink = (width//2, height//2) if sink is None else sink
        # source = (0, 0) if source is None else source
        # super(GridTopology, self).__init__(self, sink=sink, source=source)
        # for j in xrange(height):
            # for i in xrange(width):
                # self._nodes[i + j*width] = (i, j)
                # for nx, ny in [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]:
                    # if nx < 0 or nx >= width or ny < 0 or ny >= height:
                        # continue
                    # else:
                        # self._edges.append( (i + j*width, nx + ny*width) )


class Topology(object):
    def __init__(self, sink=None, source=None):
        self._g = nx.Graph(sink=sink, source=source)

    @property
    def network(self):
        return self._g

    def add_node(self, node, coord):
        self._g.add_node(node, attr_dict={"coord": coord})
        # print("Added node {}".format(node))

    def add_edge(self, start_node, end_node):
        if start_node not in self._g.node.keys() or end_node not in self._g.node.keys():
            raise RuntimeError("Edge node does not exist in topology")
        self._g.add_edge(start_node, end_node)
        # print("Added edge {}->{}".format(start_node, end_node))


class GridTopology(Topology):
    def __init__(self, width, height, sink=None, source=None):
        edges = []
        sink = (width//2) + (height//2)*width if sink is None else sink
        source = 0 if source is None else source
        super(GridTopology, self).__init__(sink=sink, source=source)

        for j in xrange(height):
            for i in xrange(width):
                self.add_node(i + j*width, (i, j))
                for nex, ney in [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]:
                    if nex < 0 or nex >= width or ney < 0 or ney >= height:
                        continue
                    else:
                        edges.append( (i + j*width, nex + ney*width) )

        for e in edges:
            self.add_edge(*e)

        nx.freeze(self._g)


def models():
    return Topology.__subclasses__() # pylint: disable=no-member

def eval_input(source):
    result = restricted_eval(source, models())

    if result in models():
        raise RuntimeError("The topology ({}) is not valid (Did you forget the brackets after the name?).".format(source))

    if not isinstance(result, Topology):
        raise RuntimeError("The topology ({}) is not valid.".format(source))

    return result
