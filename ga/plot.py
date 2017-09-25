import numpy as np
from math import pi
import networkx as nx
import sqlite3
try:
    import cPickle as pickle
except ImportError:
    import pickle
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Rectangle, RegularPolygon
from matplotlib.collections import PatchCollection
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D

from ga.genome import find_attacker_path, normalise_slots
from ga.output_adapters import sqlite_retrieve_best_genome

plt.rc('font', size=15)

def plot_network(genome):
    """
    Create and display a visualisation of the network
    """
    g = genome.n
    # width = g.graph["size"]
    # height = g.graph["size"]

    # fig = plt.figure(figsize=(width,height))
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    ax = fig.add_subplot(111, aspect='equal')
    # ax.set_axis_off()

    # collision_coords = find_collisions(genome)
    # das_coords = find_das_extended(genome)
    # slp_coords = find_slp(genome)
    slp_nodes = find_attacker_path(genome.n)

    # Plot the parent-child tree
    for n in g.nodes_iter():
        if g.node[n]["parent"] is not None:
            _line(g.node[n]["coord"], g.node[g.node[n]["parent"]]["coord"], zorder=0, color='k')

    for n in g.nodes_iter():
        coord = g.node[n]["coord"]
        shape = _circles
        colour = 'b'
        s = 0.4
        if n in slp_nodes:
            shape = _hexagons
            colour = 'y'
            s = 0.45
        if n == g.graph["source"]:
            shape = _squares
            colour = 'g'
        if n == g.graph["sink"]:
            shape = _octogons
            colour = 'k'
            s = 0.45
        shape(coord[0], coord[1], s, fc="white", ec=colour)
        if(len(str(g.node[n]["slot"])) == 1):
            ax.text(coord[0]-0.15, coord[1]+0.15, str(g.node[n]["slot"]))
        elif(len(str(g.node[n]["slot"])) == 2):
            ax.text(coord[0]-0.25, coord[1]+0.15, str(g.node[n]["slot"]))
        elif(len(str(g.node[n]["slot"])) == 3):
            ax.text(coord[0]-0.4, coord[1]+0.15, str(g.node[n]["slot"]))
        else:
            ax.text(coord[0]-0.5, coord[1]+0.15, str(g.node[n]["slot"]))


    plt.gca().invert_yaxis()
    fig.show()


def plot_network_sqlite(dbname, id):
    genome, generation, slots = sqlite_retrieve_best_genome(dbname, id)
    normalise_slots(genome)
    plot_network(genome)

def plot_generations_sqlite(dbname, id):
    """
    Plot and display the maximum, minimum and average raw fitness scores for each generation,
    collected from an SQLite3 database.
    """
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    query = "SELECT id, generation, rawMax, rawAve, rawMin FROM statistics WHERE id=? ORDER BY generation"

    generations = []
    max_stats = []
    avg_stats = []
    min_stats = []
    for row in c.execute(query, (id,)):
        generations.append(row[1])
        max_stats.append(row[2])
        avg_stats.append(row[3])
        min_stats.append(row[4])

    fig = plt.figure()
    fig.patch.set_facecolor('white')
    plt.plot(generations, max_stats, color='red', label="Maximum", alpha=1.0)
    plt.plot(generations, avg_stats, color='blue', label="Average", alpha=1.0)
    plt.plot(generations, min_stats, color='green', label="Minimum", alpha=1.0)

    plt.legend(loc=4)
    plt.grid(True)
    fig.show()
    conn.close()

def plot_network_animate_sqlite(dbname, id):
    na = NetworkAnimate(dbname, id)
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    ax = fig.add_subplot(111, aspect='equal')
    na.set_ax(ax)
    anim = FuncAnimation(fig, na, frames=na.total_generations, init_func=na.init, interval=100, repeat=False, blit=False)
    na.set_anim(anim)
    fig.canvas.mpl_connect('key_press_event', na.on_click)
    fig.show()

def plot_slot_v_generation_sqlite(dbname, id):
    generations = []
    slots = []
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    retrieve_query = "SELECT id, generation, slots, genome FROM best_individuals WHERE id=? ORDER BY generation ASC"
    query_result = c.execute(retrieve_query, (id,))
    for row in query_result:
        generations.append(int(row[1]))
        slots.append(int(row[2]))

    fig = plt.figure()
    fig.patch.set_facecolor('white')
    plt.plot(generations, slots, color='red', label=id, alpha=1.0)
    plt.legend(loc=4)
    plt.grid(True)
    fig.show()
    c.close()
    conn.close()



# def plot_slot_v_generation(dbname, ids, generations):
    # generation_sums = 0
    # conn = sqlite3.connect(dbname)
    # c = conn.cursor()
    # for base_id in ids:
        # for id in [ base_id + str(i) for i in xrange(generations) ]:
            # generation_count = 0
            # retrieve_query = "SELECT id, generation, slots, genome FROM best_individuals WHERE id=? ORDER BY generation ASC"
            # query_result = c.execute(retrieve_query, (id,))
            # generation_sums = [ 0 for i in xrange(len(query_result)) ]
            # for row in c.execute(retrieve_query, (id,)):
                # generation_sums[int(row[1])] += int(row[2])
        # generations_avg = [ i/generations for i in generation_sums ]

    # c.close()
    # conn.close()

    # # For each run record, retrieve slots used
    # # Average each generation across runs
    # # Plot average total slot against generation
    # return

def _circles(x, y, s, c='b', vmin=None, vmax=None, **kwargs):
    """
    https://gist.github.com/syrte/592a062c562cd2a98a83
    Make a scatter plot of circles.
    Similar to plt.scatter, but the size of circles are in data scale.
    Parameters
    ----------
    x, y : scalar or array_like, shape (n, )
        Input data
    s : scalar or array_like, shape (n, ) 
        Radius of circles.
    c : color or sequence of color, optional, default : 'b'
        `c` can be a single color format string, or a sequence of color
        specifications of length `N`, or a sequence of `N` numbers to be
        mapped to colors using the `cmap` and `norm` specified via kwargs.
        Note that `c` should not be a single numeric RGB or RGBA sequence 
        because that is indistinguishable from an array of values
        to be colormapped. (If you insist, use `color` instead.)  
        `c` can be a 2-D array in which the rows are RGB or RGBA, however. 
    vmin, vmax : scalar, optional, default: None
        `vmin` and `vmax` are used in conjunction with `norm` to normalize
        luminance data.  If either are `None`, the min and max of the
        color array is used.
    kwargs : `~matplotlib.collections.Collection` properties
        Eg. alpha, edgecolor(ec), facecolor(fc), linewidth(lw), linestyle(ls), 
        norm, cmap, transform, etc.
    Returns
    -------
    paths : `~matplotlib.collections.PathCollection`
    Examples
    --------
    a = np.arange(11)
    circles(a, a, s=a*0.2, c=a, alpha=0.5, ec='none')
    plt.colorbar()
    License
    --------
    This code is under [The BSD 3-Clause License]
    (http://opensource.org/licenses/BSD-3-Clause)
    """

    if np.isscalar(c):
        kwargs.setdefault('color', c)
        c = None
    if 'fc' in kwargs:
        kwargs.setdefault('facecolor', kwargs.pop('fc'))
    if 'ec' in kwargs:
        kwargs.setdefault('edgecolor', kwargs.pop('ec'))
    if 'ls' in kwargs:
        kwargs.setdefault('linestyle', kwargs.pop('ls'))
    if 'lw' in kwargs:
        kwargs.setdefault('linewidth', kwargs.pop('lw'))
    # You can set `facecolor` with an array for each patch,
    # while you can only set `facecolors` with a value for all.

    patches = [Circle((x_, y_), s_)
               for x_, y_, s_ in np.broadcast(x, y, s)]
    collection = PatchCollection(patches, **kwargs)
    if c is not None:
        collection.set_array(np.asarray(c))
        collection.set_clim(vmin, vmax)

    ax = plt.gca()
    ax.add_collection(collection)
    ax.autoscale_view()
    plt.draw_if_interactive()
    if c is not None:
        plt.sci(collection)
    return collection

def _squares(x, y, s, c='b', vmin=None, vmax=None, **kwargs):
    if np.isscalar(c):
        kwargs.setdefault('color', c)
        c = None
    if 'fc' in kwargs:
        kwargs.setdefault('facecolor', kwargs.pop('fc'))
    if 'ec' in kwargs:
        kwargs.setdefault('edgecolor', kwargs.pop('ec'))
    if 'ls' in kwargs:
        kwargs.setdefault('linestyle', kwargs.pop('ls'))
    if 'lw' in kwargs:
        kwargs.setdefault('linewidth', kwargs.pop('lw'))
    # You can set `facecolor` with an array for each patch,
    # while you can only set `facecolors` with a value for all.

    patches = [Rectangle((x_-s_, y_-s_), 2*s_, 2*s_)
               for x_, y_, s_ in np.broadcast(x, y, s)]
    collection = PatchCollection(patches, **kwargs)
    if c is not None:
        collection.set_array(np.asarray(c))
        collection.set_clim(vmin, vmax)

    ax = plt.gca()
    ax.add_collection(collection)
    ax.autoscale_view()
    plt.draw_if_interactive()
    if c is not None:
        plt.sci(collection)
    return collection

def _hexagons(x, y, s, c='b', vmin=None, vmax=None, **kwargs):
    return _polygons(x, y, s, c=c, vmin=vmin, vmax=vmax, faces=6, **kwargs)

def _octogons(x, y, s, c='b', vmin=None, vmax=None, **kwargs):
    return _polygons(x, y, s, c=c, vmin=vmin, vmax=vmax, faces=8, **kwargs)

def _polygons(x, y, s, c='b', vmin=None, vmax=None, faces=6, **kwargs):
    if np.isscalar(c):
        kwargs.setdefault('color', c)
        c = None
    if 'fc' in kwargs:
        kwargs.setdefault('facecolor', kwargs.pop('fc'))
    if 'ec' in kwargs:
        kwargs.setdefault('edgecolor', kwargs.pop('ec'))
    if 'ls' in kwargs:
        kwargs.setdefault('linestyle', kwargs.pop('ls'))
    if 'lw' in kwargs:
        kwargs.setdefault('linewidth', kwargs.pop('lw'))
    # You can set `facecolor` with an array for each patch,
    # while you can only set `facecolors` with a value for all.

    patches = [RegularPolygon((x_, y_), faces, s_, orientation=(pi/faces))
               for x_, y_, s_ in np.broadcast(x, y, s)]
    collection = PatchCollection(patches, **kwargs)
    if c is not None:
        collection.set_array(np.asarray(c))
        collection.set_clim(vmin, vmax)

    ax = plt.gca()
    ax.add_collection(collection)
    ax.autoscale_view()
    plt.draw_if_interactive()
    if c is not None:
        plt.sci(collection)
    return collection

def _line(x, y, c='b', **kwargs):
    line = Line2D((x[0], y[0]), (x[1], y[1]), **kwargs)
    ax = plt.gca()
    ax.add_line(line)
    ax.autoscale_view()
    plt.draw_if_interactive()
    return line

def _lines(x, y, c='b', vmin=None, vmax=None, **kwargs):
    if np.isscalar(c):
        kwargs.setdefault('color', c)
        c = None
    if 'fc' in kwargs:
        kwargs.setdefault('facecolor', kwargs.pop('fc'))
    if 'ec' in kwargs:
        kwargs.setdefault('edgecolor', kwargs.pop('ec'))
    if 'ls' in kwargs:
        kwargs.setdefault('linestyle', kwargs.pop('ls'))
    if 'lw' in kwargs:
        kwargs.setdefault('linewidth', kwargs.pop('lw'))
    # You can set `facecolor` with an array for each patch,
    # while you can only set `facecolors` with a value for all.

    lines = [Line2D([x_], [y_]) for x_, y_ in np.broadcast(x, y)]
    collection = PatchCollection(lines, **kwargs)
    if c is not None:
        collection.set_array(np.asarray(c))
        collection.set_clim(vmin, vmax)

    ax = plt.gca()
    ax.add_collection(collection)
    ax.autoscale_view()
    plt.draw_if_interactive()
    if c is not None:
        plt.sci(collection)
    return collection


class NetworkAnimate(object):
    def __init__(self, dbname, id):
        self._dbname = dbname
        self._id = id
        self._genomes = []
        self._ax = None
        conn = sqlite3.connect(self._dbname)
        c = conn.cursor()
        retrieve_query = "SELECT id, generation, slots, genome FROM best_individuals WHERE id=? ORDER BY generation ASC"
        for row in c.execute(retrieve_query, (self._id,)):
            g = pickle.loads(str(row[3]))
            normalise_slots(g)
            self._genomes.append(g)
        c.close()
        conn.close()
        self._pause = False
        self._anim = None

    @property
    def total_generations(self):
        return len(self._genomes)

    def set_ax(self, ax):
        self._ax = ax

    def set_anim(self, anim):
        self._anim = anim

    def init(self):
        plt.gca().invert_yaxis()

    def on_click(self, event):
        if event.key == " ":
            self._pause ^= True
            if self._pause:
                self._anim.event_source.stop()
            else:
                self._anim.event_source.start()

    def __call__(self, generation):
        self._ax.clear()

        g = self._genomes[generation].n

        self._ax.text(0, -1, "Generation: " + str(generation) + "/" + str(self.total_generations-1))

        slp_nodes = find_attacker_path(g)

        # Plot the parent-child tree
        for n in g.nodes_iter():
            if g.node[n]["parent"] is not None:
                _line(g.node[n]["coord"], g.node[g.node[n]["parent"]]["coord"], zorder=0, color='k')

        for n in g.nodes_iter():
            coord = g.node[n]["coord"]
            shape = _circles
            colour = 'b'
            s = 0.4
            if n in slp_nodes:
                shape = _hexagons
                colour = 'y'
                s = 0.45
            if n == g.graph["source"]:
                shape = _squares
                colour = 'g'
            if n == g.graph["sink"]:
                shape = _octogons
                colour = 'k'
                s = 0.45
            shape(coord[0], coord[1], s, fc="white", ec=colour)
            if(len(str(g.node[n]["slot"])) == 1):
                self._ax.text(coord[0]-0.15, coord[1]+0.15, str(g.node[n]["slot"]))
            elif(len(str(g.node[n]["slot"])) == 2):
                self._ax.text(coord[0]-0.25, coord[1]+0.15, str(g.node[n]["slot"]))
            elif(len(str(g.node[n]["slot"])) == 3):
                self._ax.text(coord[0]-0.4, coord[1]+0.15, str(g.node[n]["slot"]))
            else:
                self._ax.text(coord[0]-0.5, coord[1]+0.15, str(g.node[n]["slot"]))

        self._ax.autoscale_view()

