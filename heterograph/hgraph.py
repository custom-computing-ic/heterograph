import graph_tool as gt
from graphviz import Digraph
import itertools
import copy
import sys
from heterograph.algorithm.dfs import dfs_traversal
from heterograph.hgraph_props import HGraphProps
import wrapt

@wrapt.decorator
def modifies_graph(wrapped, instance, args, kwargs):
    if instance.read_only:
        raise RuntimeError("cannot modify read-only graph!")
    return wrapped(*args, **kwargs)



class HGraph:
    """Provides a high-level interface to analyse and manipulate arbitrary graph data structures.

    :class:`HGraph` encapsulates complex functionalities of the `graph-tool` library, and adds additional features like property maps for vertices and edges to capture arbitrary data and styling options.  Unlike `graph-tool`, vertices and edges maintain their original references when the graph is manipulated.

    Here are some key benefits:

    - **Property Mapping**: Each vertex and edge in the graph can have a custom property map associated with it. This allows you to associate arbitrary data with each element of your graph.

    - **Read-Only Mode**: You can set the graph into read-only mode, which will make any modifications fail with an error, preventing accidental changes.

    - **Styling Support**: The class provides support for styling both at a high level and individual elements. It uses Graphviz's Digraph module to generate SVG files of the graph, and it also supports viewing graphs directly on a webpage with interactive features such as zooming and panning.

    - **Subgraph Operations**: The class provides methods for adding/removing vertices and edges from the graph, which includes checking if a vertex or edge is valid before performing operations. It also supports copying of subgraphs, removal of subgraphs, and other operations.

    - **DFS Support**: It uses the DFS algorithm to find connected components, which can be useful for various tasks like graph partitioning.

    - **Rendering and Viewing**: The class provides methods for rendering the graph into different formats (like SVG) and viewing it directly on a webpage through a built-in HTTP server with interactive features.

    """
    def __init__(self, *, ginit=None, vinit=None, einit=None):
        """Initializes an instance of HGraph.

        This function sets up the initial state of the graph. It also allows optional initialization functions for graph, vertices, and edges to intialize the corresponding attributes in property maps. Note that a graph is initialized as **not** read-only.

        Args:
            ginit (function, optional): A function that takes in the HGraph instance and initializes it. Defaults to None.
            vinit (function, optional): A function that takes in the HGraph instance and a vertex ID, and initializes the properties of this vertex. Defaults to None.
            einit (function, optional): A function that takes in the HGraph instance and an edge tuple, and initializes the properties of this edge. Defaults to None.
        """


        self.__g = gt.Graph(g=None, directed=True, prune=False, vorder=None)
        """
        an instance of graph_tool's Graph object which represents the actual directed graph.
        """

        self.__ginit = ginit
        """stores initial user-defined graph properties."""

        self.__vinit = vinit
        """stores initial user-defined vertex properties."""

        self.__einit = einit
        """stores initial user-defined edge properties."""

        self.__vx_counter = None
        """keeps track of the total number of vertices added to the graph. Each vertex gets a unique id generated from this counter."""

        self.__ivx = None
        """a dictionary that maps internal vertex IDs (as used by graph_tool) to persistent vertex IDs (as seen by users)."""

        self.__vx = None
        """
        the reverse of __ivx, mapping persistent vertex IDs (as seen by users) to internal vertex IDs (as used by graph_tool).
        """

        self.__in = None
        """dictionary that stores incoming neighbors of each vertex."""

        self.__out = None
        """dictionary that stores outgoing neighbors of each vertex."""

        # graph map properties
        self.__properties = None
        """an instance of HGraphProps that manages property maps for graph, vertices and edges."""

        self.read_only = None
        """indicates whether the graph is in read-only mode. If True, any graph modification raises an error."""

        self.__reset() # initialize attributes

    @property
    def igraph(self):
        """ Returns the internal Graph (graph-tool) object."""
        return self.__g

    @property
    def to_ivx(self):
        """ Returns a dictionary mapping internal vertex IDs to persistent vertex IDs."""
        return self.__ivx

    @property
    def to_vx(self):
        """ Returns a dictionary mapping persistent vertex IDs to internal vertex IDs."""
        return self.__vx


    #################################### style

    @property
    def style(self):
        """
        Get or set the `graph` style.

        When setting the style to ``None``, the current style is cleared.
        Otherwise, the provided style is added or updated.
        """

        return self.__gstyle

    @style.setter
    def style(self, gstyle):
        if gstyle is None:
            self.__gstyle = { }
        else:
            if type(gstyle) != dict:
               raise RuntimeError("style must be a dict type")
            self.__gstyle.update(gstyle)

    @property
    def vstyle(self):
        """
        Get or set the `vertex` style.

        When setting the style to ``None``, the current style is cleared.
        Otherwise, the provided style is added or updated.
        """

        return self.__vstyle

    @vstyle.setter
    def vstyle(self, vstyle):
        if vstyle is None:
            self.__vstyle = { }
        else:
            if type(vstyle) != dict:
               raise RuntimeError("vstyle must be a dict type")
            self.__vstyle.update(vstyle)

    @property
    def estyle(self):
        """
        Get or set the `edge` style.

        When setting the style to ``None``, the current style is cleared.
        Otherwise, the provided style is added or updated.
        """
        return self.__estyle

    @estyle.setter
    def estyle(self, estyle):
        if estyle is None:
            self.__estyle = { }
        else:
            if type(estyle) != dict:
               raise RuntimeError("estyle must be a dict type")
            self.__estyle.update(estyle)

    #################################### property maps

    #

    @property
    def pmap(self):
        """
        Gets/sets property maps of graph, vertices and edges.

           * ``g.pmap``: get/set graph properties
           * ``g.pmap[vx]``: get/set vertex ``vx`` properties
           * ``g.pmap[edge]``: get/set edge ``edge`` properties

        """
        return self.__properties

    @pmap.setter
    def pmap(self, value):
        self.__properties.clear()
        if type(value) != dict:
            raise RuntimeError("property map must be set using a dictionary!")
        self.__properties.update(value)


    ################################# vertex
    @property
    def num_vx(self):
        """
        This property returns the total number of vertices in the graph.
        """
        return self.__g.num_vertices()

    @property
    def vertices(self):
        """
        This property returns a list of all vertex IDs in the graph.
        """
        return [*self.__ivx]

    @property
    def source(self):
        """
        Get list of source vertices (vertices with no incoming edges) in the graph.
        """

        return [v for v in self.vertices if len(self.in_vx(v)) == 0]

    @property
    def sink(self):
        """Get list of sink vertices (vertices with no outgoing edges) in the graph."""
        return [v for v in self.vertices if len(self.out_vx(v)) == 0]


    def num_in_vx(self, vx):
        """
        Calculates and returns the number of incoming edges for a given vertex.

        Args:
            vx (int): The ID of the vertex whose in-degree is to be calculated.

        Returns:
            int: Number of incoming edges for the specified vertex `vx`.

        Raises:
            RuntimeError: If the provided vertex ID `vx` does not exist.

        Example:
            >>> g = HGraph()
            >>> v1 = g.add_vx()
            >>> v2 = g.add_vx()
            >>> e = g.add_edge(v1, v2)
            >>> g.num_in_vx(v2)
            1
        """
        ret = self.__in.get(vx, [])
        return len(ret)

    def num_out_vx(self, vx):
        """
        Returns the number of vertices that are connected to this vertex
        via outgoing edges.

        Args:
            vx (int): The ID of the vertex whose out-degree is to be calculated.

        Returns:
            int: Number of vertices that are connected to the specified vertex `vx`.

        Raises:
            RuntimeError: If the provided vertex ID `vx` does not exist.

        Example:
            >>> g = HGraph()
            >>> vs = g.add_vx(3)
            >>> e = g.add_edge(0, [1, 2])
            >>> g.num_out_vx(0)
            2
        """
        ret = self.__out.get(vx, [])
        return len(ret)

    def out_vx(self, vx, *, order=None, after=True, anchor=None):
        """
        Returns a list of vertices that are connected to vertex `vx` via outgoing edges.
        This includes all vertices that can be reached by following directed edges starting from `vx`.
        The ordering is controlled by the `order` parameter.

        If `order` is provided, this method will first remove the list of vertices specified in `order`, and then
        append after or before the `anchor` according to the value of `after`. If the `anchor` is None,
        then the `anchor` is assumed to be the last element.

        Args:
            vx (int): The ID of the vertex whose out-neighbours are to be retrieved.
            order (list of ints, optional): A list of neighbouring vertices in their desired order. Defaults to None.
            after (bool, optional): If True and an anchor is provided, append the ordered neighbours to it,
                                    else prepend them. Defaults to True.
            anchor (int, optional): The vertex ID around which we should arrange our neighbours. Ignored if order is not provided. Defaults to None.

        Returns:
            list of ints: A list of vertices that are connected to the specified `vx` via outgoing edges in the requested order (if any).

        Raises:
            RuntimeError: If the vertex ID `vx` does not exist, or if the ordered neighbours provided in the 'order' argument do not form a subset of those connected to `vx`.
                        Also raised if an invalid anchor is specified (not an integer).

        Example:
            >>> g = HGraph()
            >>> vs = g.add_vx(4)  # adds 4 vertices and returns their IDs in a list [0, 1, 2, 3]
            >>> e = g.add_edge(0, [1, 2, 3])  # connects vertex 0 to vertices [1, 2, 3]
            >>> g.out_vx(0)  # gets the out-neighbours of vertex 0
            [1, 2, 3]
            >>> g.out_vx(0, order=[2,1,3])
            [2, 1, 3]
            >>> g.out_vx(0, order=[3,2], after=True, anchor=1)
            [1, 3, 2]
            >>> g.out_vx(0, order=[3,2], after=False, anchor=1)
            [3, 2, 1]
            >>> g.out_vx(0, order=[2,3], after=True)
            [1, 2, 3]
        """
        if order is not None and self.read_only:
           raise RuntimeError("cannot modify read-only graph!")
        return self.__neighbours(_in=False, vx=vx, order=order, after=after, anchor=anchor)


    def in_vx(self, vx, *, order=None, after=True, anchor=None):
        """
        Returns a list of vertices that are connected to vertex `vx` via incoming edges.

        This includes all vertices from which directed edges point to `vx`. The ordering is
        controlled by the `order` parameter.

        If `order` is provided, this method will first remove the list of vertices specified in `order`, and then
        append after or before the `anchor` according to the value of `after`. If the `anchor` is None,
        then the `anchor` is assumed to be the last element.

        Args:
            vx (int): The ID of the vertex whose in-neighbours are to be retrieved.
            order (list of ints, optional): A list of neighbouring vertices in their desired order. Defaults to None.
            after (bool, optional): If True and an anchor is provided, append the ordered neighbours to it,
                                    else prepend them. Defaults to True.
            anchor (int, optional): The vertex ID around which we should arrange our neighbours. Ignored if order is not provided. Defaults to None.

        Returns:
            list of ints: A list of vertices that are connected to the specified `vx` via incoming edges in the requested order (if any).

        Raises:
            RuntimeError: If the vertex ID `vx` does not exist, or if the ordered neighbours provided in the 'order' argument do not form a subset of those connected to `vx`.
                        Also raised if an invalid anchor is specified (not an integer).

        Example:
            >>> g = HGraph()
            >>> vs = g.add_vx(4)  # adds 4 vertices and returns their IDs in a list [0, 1, 2, 3]
            >>> e = g.add_edge([1, 2, 3], 0)  # connects vertices [1, 2, 3] to 0
            >>> g.in_vx(0)  # gets the in-neighbours of vertex 0
            [1, 2, 3]
            >>> g.in_vx(0, order=[3,2], after=False, anchor=1)
            [3, 2, 1]
            >>> g.in_vx(0, order=[2], after=False)
            [2, 3, 1]
        """

        if order is not None and self.read_only:
           raise RuntimeError("cannot modify read-only graph!")
        return self.__neighbours(_in=True, vx=vx, order=order, after=after, anchor=anchor)

    @modifies_graph
    def add_vx(self, n=1):
        """
        Add a new vertex to the graph.

        Args:
            n (int): The number of vertices to add. Default is 1.

        Returns:
            int or list:
            * if `n` == 1: returns the ID (int) of newly added vertex
            * if `n` > 1`: returns a list of IDs (list of int) of the newly added vertices.

        Example:
            >>> g = HGraph()
            >>> g.add_vx()  # adds one new vertex
            0
            >>> g.add_vx(3)  # adds three new vertices
            [1, 2, 3]
            >>> g.num_vx
            4
        """

        if n < 1:
            raise ValueError("[x] 'n' must be >= 1!")


        ivs = self.__g.add_vertex(n)

        if n == 1:
            _ivs = [ivs]
        else:
            _ivs = ivs

        ret = []
        for _ivx in _ivs:
            ivx = int(_ivx)
            vx = self.__gen_vx_id()

            self.__ivx[vx] = ivx
            self.__vx[ivx] = vx

            ret.append(vx)

            if self.__vinit:
                self.__vinit(self, vx)

        return ret if n > 1 else ret[0]

    @modifies_graph
    def rm_vx(self, vs, verify=True):
        """
        Remove one or more vertices from the graph and disconnect all edges connected to them.

        This function removes a specified vertex (or multiple vertices) along with all the edges that are incident
        on it in both directions i.e., incoming and outgoing edges. It also updates the internal dictionaries tracking
        neighbours of each vertex, so these changes will reflect in the `in_vx` and `out_vx` methods when called for
        this same vertices.

        Args:
            vs (int or list): The ID(s) of the vertex to be removed. If it's a single integer, then it represents one
                            vertex. If it's a list, then it contains multiple vertices.
            verify (bool, optional): If True, raises an exception if any specified
                vertex does not exist in the graph. Otherwise, any vertex not found is
                ignored. Default is True.

        Raises:
            RuntimeError: If any of the provided vertex IDs `vs` do not exist in the graph.

        Example:
            >>> g = HGraph()
            >>> g.add_vx(3)  # adds three vertices
            [0, 1, 2]
            >>> g.rm_vx(1)
            >>> g.vertices
            [0, 2]
            >>> g.rm_vx([0, 2])
            >>> g.vertices
            []
        """

        if type(vs) == int:
            vs = [vs]

        if len(vs) == 0:
            raise RuntimeError("no vertex ID specified!")


        if not verify:
            # filter if not exist to avoid raising an exception in the next statement
            vs = [ v for v in vs if self.check_vx(v, verify=False)]

        ivs = self.__to_ivs(vs) # {ivx: vx}

        # reverse order
        for ivx in reversed(sorted(ivs)):
            self.__g.remove_vertex(ivx)
            vx = ivs[ivx]
            del self.__ivx[vx]

        # defragment
        n = self.num_vx
        m = n
        for i in reversed(range(0, self.__vx_counter)):
            if i in self.__ivx:
                n = n - 1
                self.__ivx[i] = n
                self.__vx[n] = i
            if i >= m:
                self.__vx.pop(i, None)

        # bookkeeping
        for vx in vs:
            _in = self.__in.get(vx, None)
            if _in:
                for v in _in:
                    self.__out[v].remove(vx)

            _out = self.__out.get(vx, None)
            if _out:
                for v in _out:
                    self.__in[v].remove(vx)
            self.__in.pop(vx, None)
            self.__out.pop(vx, None)

            self.__properties.rm_elem(vx)


    def check_vx(self, vs, verify=False):
        """
        Checks if a vertex (or set of vertices) exist in the graph.

        This function checks whether one or more vertices specified by their IDs exist in the graph or not. It returns True if all vertices are present and False otherwise. If `verify` is set to True, it raises an exception with an error message specifying which vertex does not exist (if any).

        Args:
            vs  (int or list of ints): The ID(s) of the vertex/vertices to be checked. Can be a single integer or a list of integers.
            verify (bool, optional): If True, raises an exception if any specified vertex does not exist in the graph. Default is False.

        Returns:
            bool: True if all vertices are present and False otherwise.

        Raises:
            RuntimeError: If `verify` is set to True and any of the provided vertices do not exist in the graph. The error message contains the ID of that vertex that does not exist.

        Example:
            >>> g = HGraph()
            >>> vs = g.add_vx(3) # adds vertices [0, 1, 2]
            >>> g.check_vx([0, 2])
            True
            >>> g.check_vx(4)
            False
        """
        if type(vs) == int:
            vs = [vs]

        for _id in vs:
            if _id not in self.__ivx:
                if verify:
                    raise RuntimeError("vertex '%d' is invalid!" % _id)
                else:
                    return False
        return True

    ################################# edges
    @property
    def num_edges(self):
        """Returns the total number of edges present in the graph."""

        return self.__g.num_edges()

    @property
    def edges(self):
        """Returns a list of all edges as tuples (v1, v2) where each tuple represents an edge
        connecting vertex v1 and v2 in the graph instance. The vertices are identified by their integer IDs.
         """
        return [ (self.__vx[int(e[0])], self.__vx[int(e[1])]) for e in self.__g.get_edges() ]

    @modifies_graph
    def add_edge(self, s, t):
        """
        Adds a new edge to the graph connecting two vertices `s` and `t`.

        Adds one or more edges between vertices. Notes:
           * adding a self-loop where vertex `s` == vertex `t` is ignored. Use vertex property maps.
           * adding multiple edges between any two vertices is ignored. Use edge property maps.

        Args:
            s (int or list of ints): The source vertex ID(s). If 's' is an integer, it represents one
                                    source vertex. If 's' is a list, it contains multiple source vertices.
            t (int or list of ints): The target vertex ID(s). Similar to 's', if 't' is an integer it
                                    represents one target vertex and if 't' is a list, it contains multiple
                                    target vertices.

        Returns:
            list of tuples: A list of edges added as tuples in the format (source_vertex, target_vertex).
                        Each tuple represents an edge connecting source_vertex to target_vertex in the graph instance.

        Raises:
            RuntimeError: If 's' and/or 't' do not exist in the graph.
                        Also, raised if any of the provided vertex IDs are invalid.

        Example:
            >>> g = HGraph()
            >>> vs = g.add_vx(4)  # [0, 1, 2, 3]
            >>> g.add_edge(0, [1, 2])  # connects vertex 0 to vertices [1,2]
            [(0, 1), (0, 2)]
            >>> g.add_edge([1, 2], 0) # connects vertices [1,2] to vertex 0
            [(1, 0), (2, 0)]
            >>> g.add_edge(2, 3)
            [(2, 3)]
            >>> g.edges
            [(0, 1), (0, 2), (1, 0), (2, 0), (2, 3)]
        """
        if type(s) == int:
            s = [s]
        if type(t) == int:
            t = [t]

        edges = []
        for _s in s:
            for _t in t:
                # make sure s and t exist
                ivx_edge = list(self.__to_ivs([_s, _t]).keys())

                # ignore self-loop
                if _s == _t:
                    continue
                # ignore existing edges
                if self.__g.edge(ivx_edge[0], ivx_edge[1], add_missing=False) is not None:
                    continue
                self.__g.add_edge(ivx_edge[0], ivx_edge[1], add_missing=False)

                vx_edge = (_s, _t)
                edges.append(vx_edge)

                if self.__einit:
                    self.__einit(self, vx_edge)

                # bookkeeping
                if _t not in self.__in:
                    self.__in[_t] = [_s]
                else:
                    self.__in[_t].append(_s)

                if _s not in self.__out:
                    self.__out[_s] = [_t]
                else:
                    self.__out[_s].append(_t)

        return edges

    def check_edge(self, edge, verify=False):
        """
        Check if one or more edges exist in the graph.

        Args:
            edge (tuple or list of tuples): The ID(s) of the edge/edges to be checked.
                If `edge` is a tuple, it represents one edge. If `edge` is a list,
                it contains multiple edges.
            verify (bool, optional): If True, raises an exception if any specified
                edge does not exist in the graph. Default is False.

        Returns:
            bool: Whether all edges are present and valid or not.

        Raises:
            RuntimeError: If `verify` is True, and one or more edges are not found in the graph.

        Example:
            >>> g = HGraph()
            >>> g.add_vx(3)
            [0, 1, 2]
            >>> g.add_edge(0, [1, 2])
            [(0, 1), (0, 2)]
            >>> g.check_edge((0, 1))
            True
            >>> g.check_edge([(0, 1), (0, 2)])
            True
            >>> g.check_edge([(0, 1), (0, 4)])
            False
        """
        if type(edge) == tuple:
            edges = [edge]
        else:
            edges = edge

        for e in edges:

            found = True

            try:
                [ev0, ev1] = self.__to_ivs([e[0], e[1]])
            except RuntimeError:
                found = False

            if not found:
                if verify:
                    raise RuntimeError("edge %s is invalid!" % str(e))
                else:
                    return False

            if self.__g.edge(ev0, ev1, add_missing=False) is None:
                if verify:
                    raise RuntimeError("edge %s not found!" % str(e))
                else:
                    return False

        return True

    @modifies_graph
    def rm_edge(self, edge, verify=True):
        """
        Removes one or more edges from the graph.

        Args:
            edge (tuple or list of tuples): The ID(s) of the edge/edges to be removed.
                If `edge` is a tuple, it represents one edge. If `edge` is a list,
                it contains multiple edges.
            verify (bool, optional): If True, raises an exception if any specified
                edge does not exist in the graph. Otherwise, any edge not found is
                ignored. Default is True.

        Returns:
            None

        Example:
            >>> g = HGraph()
            >>> vs = g.add_vx(3) # adds 3 vertices
            >>> g.add_edge(0, [1, 2])
            [(0, 1), (0, 2)]
            >>> g.rm_edge((0,1)) # removes edge between vertex 0 and 1
            >>> g.edges
            [(0, 2)]

        Raises:
            RuntimeError: If `verify` is True and one or more edges are not found in the graph.
        """
        if type(edge) == tuple:
            if len(edge) != 2:
                raise RuntimeError("invalid edge: %s!" % str(edge))
            edges = [edge]
        else:
            edges = edge # list of edges

        if not verify:
            edges = [ e for e in edges if self.check_edge(e) ]

        g = self.__g
        for e in edges:
            try:
                [ev0, ev1] = self.__to_ivs([e[0], e[1]])
            except RuntimeError as ex:
                raise RuntimeError("edge descriptor not found: %s" % str(e)) from ex

            edge = g.edge(ev0, ev1, add_missing=False)
            if edge:
               g.remove_edge(edge)
               # bookkeeping
               self.__in[e[1]].remove(e[0])
               self.__out[e[0]].remove(e[1])

               self.__properties.rm_elem(e)

            else:
                raise RuntimeError("internal error (%d, %d) does not exist, and thus cannot be removed!" % (e[0],e[1]))



    @modifies_graph
    def erase(self):
        """
        Resets the graph to its initial state, clearing all vertices and edges.

        The properties of the graph will be reset as well, returning them to their default values.
        Read-only status is also set back to False.

        This function does not accept any arguments and does not return anything.

        Example:
            >>> g = HGraph()
            >>> vs = g.add_vx(3)   # adds three vertices
            >>> e = g.add_edge(0, 1)  # connects vertex 0 to vertex 1
            >>> g.num_vx
            3
            >>> g.num_edges
            1
            >>> g.erase()
            >>> g.num_vx
            0
            >>> g.num_edges
            0
        """
        self.__reset()

    def copy(self, *, vs=None, g=None, induced=True, ret_map=False):
        """
        Creates a copy of the current graph.

        This function creates an independent clone of the current graph instance. The cloned graph is optionally restricted to a subset of vertices (`vs`) or can be copied as an induced subgraph. An induced subgraph means that edges from any two nodes included in the copy are also copied automatically. Properties are automatically copied.

        Args:
            vs  (list of ints): A list of vertex IDs specifying which vertices should be included in the copy. If not provided, all vertices will be copied. Default is None.
            g   (HGraph instance, optional): The HGraph instance to store the clone. If provided, the clone is added. If not provided, a new HGraph instance is created. Default is None.
            induced  (bool, optional): A flag indicating whether an induced subgraph should be copied or all edges should be copied. Default is True.
            ret_map   (bool, optional): A flag indicating whether the vertex mapping from old to new graph should be returned. Default is False.

        Returns:
            HGraph instance:
               * If `ret_map` is False, returns a copy of the cloned graph.
               * If `ret_map` is True, returns a tuple containing both a copy of the current graph and a mapping from old to new vertices in the form of {old vertex: new vertex}.

        Example:
            >>> g = HGraph()
            >>> vs = g.add_vx(3)   # adds three vertices, returns their IDs [0, 1, 2]
            >>> e = g.add_edge(0, [1, 2])   # connects vertex 0 to vertices [1, 2]
            >>> (h, map_cp) = g.copy(vs=[0, 2], induced=True, ret_map=True)   # creates a copy of the graph
            >>> map_cp # 0 => 0, 2 => 1
            {0: 0, 2: 1}
            >>> h.vertices
            [0, 1]
            >>> h.edges
            [(0, 1)]
        """

        if g is None:
            g = HGraph(ginit=self.__ginit, vinit=self.__vinit, einit=self.__einit)
            # we need to set it to None, othrwise it will append to the existing style
            g.style = None; g.style = self.style
            g.vstyle = None; g.vstyle = self.vstyle
            g.estyle = None; g.estyle = self.estyle

        g.read_only = False

        # copy graph properties
        g.pmap = dict(self.__properties)


        if vs is None:
            vs = self.vertices

        _map = { } # vx(self) => vx (g)
        for vx in vs:
            _vx = g.add_vx(1)
            _map[vx] = _vx
            self.__properties.copy_prop_elem(g, _vx, vx)

        if induced:
            for e in self.edges:
                _e0 = _map.get(e[0], None)
                _e1 = _map.get(e[1], None)
                if (_e0 is not None) and (_e1 is not None):
                    g.add_edge(_e0, _e1)
                    self.__properties.copy_prop_elem(g, (_e0, _e1), e)

        g.read_only = self.read_only

        if ret_map:
            return (g, _map)
        else:
            return g

    @modifies_graph
    def remove_subgraph(self, vx):
        """
        Remove a subgraph rooted at a specified vertex.

        This method removes all vertices and edges connected to the provided vertex and its descendants in the graph.

        Args:
            vx (int): The ID of the vertex from where the subgraph starts being removed.

        Returns:
            None: The function doesn't return any value, it directly modifies the graph by removing vertices and edges.

        Example:
            >>> g = HGraph()
            >>> vs = g.add_vx(5)  # adds five vertices with IDs [0, 1, 2, 3, 4]
            >>> e = g.add_edge(0, [1, 2])  # connects vertex 0 to vertices 1 and 2
            >>> e = g.add_edge(1, 3)  # connects vertex 1 to vertex 3
            >>> e = g.add_edge(2, 4)  # connects vertex 2 to vertex 4
            >>> g.remove_subgraph(0)  # removes the subgraph rooted at vertex 0
            >>> g.vertices
            []
            >>> g.edges
            []
        """

        def visit(g, vx, synth):
           # flatten list
           synth = list(itertools.chain(*synth))
           synth.append(vx)
           return synth
        # vx is the root of the subgraph we wish to remove
        vs = dfs_traversal(g=self, vx=vx, post=visit)
        self.rm_vx(vs)

    def render(self, *, filename='graph.svg', format='svg', pipe=False, vs=None, induced=True, gstyle=None, vstyle=None, estyle=None, **kwargs):
        """
        Renders the graph (or part of the graph). The rendering style can be specified without changing the internal graph style.

        Args:
            filename (str, optional): The output filename. Defaults to 'graph.svg'.
            format (str, optional): The format of the generated images ('png', 'pdf', etc). Defaults to 'svg'.
            pipe (bool, optional): If True, return a string representation of the graph in specified format instead of saving an image file. Defaults to False.
            vs (list of ints, optional): A list of vertex IDs specifying which vertices should be included in the rendering. If not provided, all vertices will be included. Defaults to None.
            induced (bool, optional): Whether or not only the edges within the subgraph specified by `vs` should be rendered. Defaults to True.
            gstyle (dict, optional): The graph style as a dictionary where keys are property names and values are their new values. Defaults to None.
            vstyle (dict, optional): The vertex style as a dictionary where keys are property names and values are their new values. Defaults to None.
            estyle (dict, optional): The edge style as a dictionary where keys are property names and values are their new values. Defaults to None.
            **kwargs: Additional keyword arguments to pass to the rendering engine.

        Returns:
            str or None:
                * If `pipe` is True, returns a string representation of the graph in specified format.
                * Otherwise (if `pipe` is False), no return value. The rendered image file will be saved to disk with the filename provided.
        """

        # ==== cluster support ===
        # g.style['nclusters'] = 4
        # g.style['cluster'] = lambda g, c: {'label': 'abc'}
        # g.vstyle['cluster'] = lambda g, v: return c

        def init_styles(int_style, arg_style):
            style_n = { }; style_w = { }; style_c = { }
            _style = { }
            _style.update(int_style)
            if arg_style is not None:
               _style.update(arg_style)

            for s in _style:
                if s[0] == '#':
                    style_w[s[1:]] = _style[s]
                elif s in ['nclusters', 'cluster']:
                    style_c[s] = _style[s]
                elif s[0] != '!':
                    style_n[s] = _style[s]
            # style_n
            return (style_n, style_w, style_c)

        (_gstyle_n, _gstyle_w, _gstyle_c) = init_styles(self.__gstyle, gstyle)
        (_vstyle_n, _vstyle_w, _vstyle_c) = init_styles(self.__vstyle, vstyle)
        (_estyle_n, _estyle_w, _) = init_styles(self.__estyle, estyle)

        if vs is None:
            vs = set(self.vertices) # faster access

        vg = Digraph()

        # graph attributes
        sargs = { }
        for s in _gstyle_n:
           val = _gstyle_n[s](self) if callable(_gstyle_n[s]) else _gstyle_n[s]
           if val is not None:
               if s in _gstyle_w:
                   val = _gstyle_w[s](self, val)
               if val is not None:
                   sargs[s] = val
        vg.attr('graph', **sargs)

        ##### cluster support (graph)
        nclusters = int(_gstyle_c.get('nclusters', 0))
        ## set cluster attribute
        if nclusters > 0 and 'cluster' in _gstyle_c:
            cattr_fn = _gstyle_c['cluster']
            if cattr_fn is not None:
                for c in range(0, nclusters):
                    ret = cattr_fn(self, int(c))
                    if type(ret) != dict:
                        raise RuntimeError("expecting cluster attributes inside a dictionary!")
                    with vg.subgraph(name="cluster_%d" % c) as c:
                        c.attr(**ret)

        # vertex attributes
        for v in vs:
            sargs = { }
            for s in _vstyle_n:
                val = _vstyle_n[s](self, v) if callable(_vstyle_n[s]) else _vstyle_n[s]
                if val is not None:
                    if s in _vstyle_w:
                        val = _vstyle_w[s](self, v, val)
                    if val is not None:
                        sargs[s] = val
            vg.node(str(v), **sargs)

            # cluster support
            if nclusters > 0 and 'cluster' in _vstyle_c:
                c = _vstyle_c['cluster'](self, v)
                if c is not None:
                   with vg.subgraph(name='cluster_%d' % int(c)) as c:
                       c.node(str(v))

        # edge attributes
        if induced:
            for e in self.edges:
                if e[0] in vs and e[1] in vs:
                    sargs = { }
                    for s in _estyle_n:
                        val = _estyle_n[s](self, e) if callable(_estyle_n[s]) else _estyle_n[s]
                        if val is not None:
                            if s in _estyle_w:
                                val = _estyle_w[s](self, e, val)
                            if val is not None:
                                sargs[s] = val

                    vg.edge(str(e[0]), str(e[1]), **sargs)

        if pipe:
            return (vg.pipe(format=format, **kwargs))
        else:
            return vg.render(filename=filename, cleanup=True, format=format, **kwargs)


    def view(self, host='0.0.0.0', port='8888', viewer=None, **kwargs):
        """
        Open an interactive web interface to visualize this graph.

        This method opens a local server and displays the graph in a user-friendly way. It allows users to interact with the graph, such as zooming and panning.

        Args:
            host (str, optional): The address where the web interface should be hosted. Default is '0.0.0.0'.
            port (int, optional): The port on which to run the server. Default is 8888.
            viewer (HGraphViewer instance, optional): An existing HGraphViewer instance to use for visualization. If not provided, a new instance will be created. Default is None.
            **kwargs: Additional arguments passed directly to the viewer's run method.

        Returns:
            None

        """
        if viewer is None:
            from .webview import WebView
            _viewer = WebView()
        else:
            _viewer = viewer

        _viewer.add_graph(self, **kwargs)

        if viewer is None:
            _viewer.run(host=host, port=port)

    def __reset(self):
        """Private method. Resets the graph to its initial state.
        Used by :meth:`__init__` and :meth:`erase` methods."""

        self.__g.clear()
        self.__g.set_fast_edge_removal(fast=True)

        self.__vx_counter = 0 # vx counter

        # vx: used to identify vertex
        self.__ivx = { } # vx => ivx

        # ivx: internal vx - graph_tool
        self.__vx = { } # ivx => vx

        # vx => [vx_in0, vx_in1] : inputs of vx
        self.__in = { }

        # vx => [vx_out0, vx_out1] : outputs of vx
        self.__out = { }

        # graph map properties
        self.__properties = HGraphProps(self)

        '''
        # hovering support
        self.on_hover = None
        # def hover(g, elem):
        #    if type(elem) == int:
        #       return "<HTML CODE>"
        '''

        # read-only support
        self.read_only = False

        # default style
        self.__gstyle = { 'layout': 'dot', 'rankdir': 'TD' }
        self.__vstyle = { 'shape': 'Mrecord', 'style': 'filled', 'fillcolor': '#99CCFF', 'label': lambda g, id: str(id) }
        self.__estyle = { 'color': '#777777', 'arrowhead': 'open' }

        # graph initialisation, including setting style
        if self.__ginit:
            self.__ginit(self)

    def __gen_vx_id(self):
        """Private method. Generates a unique integer ID for a new vertex in the graph."""

        _id = self.__vx_counter
        self.__vx_counter = self.__vx_counter + 1
        return _id

    def __to_ivs(self, vs):
        """Private method which maps persistent vertex IDs to graph-tool vertex IDs (ivx). """
        ret = {}
        for vx in vs:
            ivx = self.__ivx.get(vx, None)
            if ivx is None:
                raise RuntimeError("cannot find internal vertex for id: %s" % vx)
            ret[ivx] = vx
        return ret

    def __neighbours(self, _in, vx, order=None, after=True, anchor=None):
        """Private method which outputs and orders input/output neighbours. Used by :meth:`in_vx` and :meth:`out_vx` methods. """
        # check if vx exists
        self.check_vx(vx, verify=True)

        if _in:
            nb=self.__in.get(vx, [])
        else:
            nb=self.__out.get(vx, [])

        if order is None and anchor is not None:
            raise RuntimeError("anchor specified without specifying order!")

        if (order is not None) and (len(order) > 0):
            if type(order) == int:
                order = [order]

            if not set(order).issubset(set(nb)):
                raise RuntimeError("specified order %s is not a subset of neighbours of vertex %d: %s!" % (order, vx, nb))

            # remove elements from list
            for x in order:
                nb.remove(x)

            if anchor is None:
                if after:
                    nb.extend(order)
                else:
                    nb = order + nb
            elif type(anchor) == int:
                try:
                   pos = nb.index(anchor)
                except ValueError:
                    raise RuntimeError("anchor '%d' not found!" % anchor)

                if after:
                    nb = nb[0:pos+1] + order + nb[pos+1:]
                else:
                    nb = nb[0:pos] + order + nb[pos:]
            else:
                raise RuntimeError("invalid anchor '%s': must be an int!" % anchor)

            if _in:
                self.__in[vx] = nb
            else:
                self.__out[vx] = nb

        return nb
