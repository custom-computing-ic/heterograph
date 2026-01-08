class QueryGraphDef:
    """
    A class to define and build query graphs.
    """
    def __init__(self, src=None, snk=None, steps=None):
        """
        Initializes the QueryGraphDef instance.

        Args:
            src (set, optional): Source nodes. Defaults to an empty set.
            snk (set, optional): Sink nodes. Defaults to an empty set.
            steps (list, optional): Steps defining the graph structure. Defaults to an empty list.
        """
        if src is None:
            src = set()
        if snk is None:
            snk = set()
        if steps is None:
            steps = []
        self.src = src
        """set specifying the source nodes."""

        self.snk = snk
        """set specifying the sink nodes."""

        self.steps = steps
        """list of steps defining the graph structure."""

    def __repr__(self):
        return "%s (src: %s, snk: %s, steps: %s)" % (self.__class__.__name__, self.src, self.snk, self.steps)

    @staticmethod
    def args_label(args):
        sep = ", " if len(args[0]) != 0 and len(args[1]) != 0 else ""
        return "(%s%s%s)" % (str(args[0])[1:-1], sep, str(args[1])[1:-1])

    def build(self, qgraph, vx_args=None, eg_args=None):
        """
        Constructs the query graph based on the defined steps.

        Args:
            qgraph (QGraph): An instance of QGraph to be built.
            vx_args (function, optional): A function to handle vertex arguments.
            eg_args (function, optional): A function to handle edge arguments.

        Returns:
            QGraph: The constructed query graph.

        Raises:
            RuntimeError: If invalid steps are provided or if arguments for a vertex or edge have already been supplied.

        Steps:
            The `steps` attribute is a list of tuples that define the elements and structure of the query graph.
            Each step can represent either a vertex or an edge.

            1. **Vertex Step (2-tuple):**
                - Format: `(vertex_id, vertex_args)`
                - `vertex_id` (str): A unique identifier for the vertex.
                - `vertex_args` (tuple): Arguments for the vertex, which is a tuple containing a list of positional arguments and a dictionary of keyword arguments.

            2. **Edge Step (3-tuple):**
                - Format: `(vertex_id_src, vertex_id_tgt, edge_args)`
                - `vertex_id_src` (str): The unique identifier for the source vertex of the edge.
                - `vertex_id_tgt` (str): The unique identifier for the target vertex of the edge.
                - `edge_args` (tuple): Arguments for the edge, which is a tuple containing a list of positional arguments and a dictionary of keyword arguments.

        Note:
            * Argument `vx_args` is a function that has signature: `vx_args(qgraph, vx, *args, **kwargs)`.
            * Argument `eg_args` is a function that has signature: `eg_args(qgraph, eg, *args, **kwargs)`.
            * Both functions are invoked during the qgraph building process, and are used to set the arguments from the select query into the corresponding vertices and edges of the qgraph.

        Example:
            >>> from heterograph.query.graphdef import QueryGraphDef
            >>> from heterograph.query.qgraph import QGraph
            >>> qg_def = QueryGraphDef(
            ...    src={'A'},
            ...    snk={'B'},
            ...    steps=[
            ...           ('A', ([], {})),  # Vertex step: Add vertex 'A' with no arguments
            ...           ('B', ([], {})),  # Vertex step: Add vertex 'B' with no arguments
            ...           ('A', 'B', (['x', 'y'], {'k0': 5, 'k1': 10}))  # Edge step: Add an edge from vertex 'A' to vertex 'B' with arguments ('arg1', 'arg2')
            ...    ]
            ... )
            >>> qgraph = QGraph()
            >>> qgraph=qg_def.build(qgraph) # builds qgraph
            >>> qgraph.vertices
            [0, 1]
            >>> qgraph.edges
            [(0, 1)]
            >>> qgraph.pmap[(0, 1)]
            {'args': "('x', 'y', 'k0': 5, 'k1': 10)"}

            In this example:
               - the first step adds a vertex with ID 'A' and no arguments.
               - the second step adds a vertex with ID 'B' and no arguments.
               - the third step adds an edge from vertex 'A' to vertex 'B' with arguments and key-value arguments
        """
        def vx_args_default(*args, **kwargs):
            pass

        def eg_args_default(*args, **kwargs):
            pass

        if vx_args is None:
            vx_args = vx_args_default

        if eg_args is None:
            eg_args = eg_args_default

        ids = qgraph.pmap['ids']
        for s in self.steps:
            # 2-tuple: vertex (<vertex-id>, v-args)
            # 3-tuple: edge (e-args, <vertex-id-src>, <vertex-id-target>)
            if type(s) == tuple:
                len_s = len(s)
                if len_s == 2:
                    # vertex

                    # only add if vertex does not exist
                    vertex_id = s[0]
                    if vertex_id not in ids:
                       v = qgraph.add_vx(1)
                       ids[vertex_id] = v
                       qgraph.pmap[v]['id'] = vertex_id
                       qgraph.pmap[v]['args'] = ""
                    else:
                        v = ids[vertex_id]

                    vargs = s[1]
                    if vargs is not None:
                        if qgraph.pmap[v]['args'] == "":
                            vx_args(qgraph, v, *vargs[0], **vargs[1])
                            qgraph.pmap[v]['args'] = QueryGraphDef.args_label(vargs)
                        else:
                            raise RuntimeError("arguments for vertex [%s] have already been supplied!" % vertex_id)
                    else:
                        vx_args(qgraph, v) # default
                    continue
                elif len_s == 3:
                    vertex_id_s = s[0]
                    vertex_id_t = s[1]
                    eargs = s[2]
                    edge = (ids[vertex_id_s], ids[vertex_id_t])

                    # only add if edge does not exist
                    if not qgraph.check_edge(edge):
                        qgraph.add_edge(ids[vertex_id_s], ids[vertex_id_t])[0]
                        qgraph.pmap[edge]['args'] = ""

                    if eargs is not None:
                        if qgraph.pmap[edge]['args'] == "":
                            eg_args(qgraph, edge, *eargs[0], **eargs[1])
                            qgraph.pmap[edge]['args'] = QueryGraphDef.args_label(eargs)
                        else:
                            raise RuntimeError("arguments for edge (%s, %s) have already been supplied!" % (vertex_id_s, vertex_id_t))
                    else:
                        eg_args(qgraph, edge) # default


                    continue
            raise RuntimeError("invalid step: %s" % s)

        return qgraph
