from heterograph.hgraph import HGraph
from heterograph.query.aql import QueryAQL
from heterograph.query.transformer import QueryTransformer


class QGraph(HGraph):
    """
    A class used to represent a query graph.

    This class extends the HGraph class and adds functionality for processing queries and transforming them into graph definitions.

    Note:
        * Argument `vx_args` is a function that has signature: `vx_args(qgraph, vx, *args, **kwargs)`.
        * Argument `eg_args` is a function that has signature: `eg_args(qgraph, eg, *args, **kwargs)`.
        * Both functions are invoked during the qgraph building process, and are used to set the arguments from the pattern into the corresponding vertices and edges of the qgraph.

    Example:
        >>> from heterograph.query.qgraph import QGraph
        >>> qgraph = QGraph(pattern="A{1} ={ weight: 3.14 }> B{2}")
        >>> print(qgraph.pattern)
        A{1} ={ weight: 3.14 }> B{2}
        >>> print(qgraph.graph_def)
        QueryGraphDef (src: {'A'}, snk: {'B'}, steps: [('A', ([1], {})), ('B', ([2], {})), ('A', 'B', ([], {'weight': 3.14}))])
    """
    def __init__(self, pattern=None, vx_args=None, eg_args=None):
        """
        Constructs all the necessary attributes for the QGraph object.

        Parameters:
            pattern (str): The query to be processed. Defaults to "0".
            vx_args (dict): The vertex arguments. Defaults to None.
            eg_args (dict): The edge arguments. Defaults to None.
        """

        def ginit(graph):
            graph.pmap['ids'] = { }
            graph.vstyle['label'] = lambda g, vx: r'''<<TABLE CELLBORDER="0" CELLSPACING="0" border="0"><TR align="right"><TD><B>%s:</B>%d %s</TD></TR></TABLE>>''' % (g.pmap[vx]['id'], vx,  g.pmap[vx]['args'] )
            graph.estyle['label'] = lambda g, eg: "%s" % (g.pmap[eg]['args'])
            graph.vstyle['shape'] = "component"
            graph.vstyle['fillcolor'] = "burlywood1"

        super().__init__(ginit=ginit)
        if pattern is None:
            pattern = "0"

        self.pattern = pattern
        """(str): pattern to be processed and translated to a graph."""

        self.engine = QueryAQL()
        """(QueryAQL): engine used to translate the pattern"""

        self.graph_def = None
        """ graph object resulting from processing the query."""

        try:
            self.graph_def = self._process(vx_args=vx_args, eg_args=eg_args)
        except Exception as e:
            raise SyntaxError(f"[x] error processing AQL pattern: '{self.pattern}'") from None

    def _process(self, vx_args, eg_args):
        """
        Processes the query and transforms it into a graph definition.

        Parameters:
            vx_args: A function to handle vertex arguments.
            eg_args: A function to handle edge arguments.

        Returns:
            QueryGraphDef: The graph definition resulting from processing the query.
        """
        query = self.pattern.replace('\n', '')
        queries = []
        for q in query.split(";"):
            _q = q.strip()
            if _q != '':
                queries.append(_q)

        graph_defs = []
        for q in queries:
           pre = self.engine.grammar.parse(q)
           graph_def = self.engine.transformer.transform(pre)
           graph_defs.append(graph_def)

        if len(graph_defs) == 1:
            graph_def = graph_defs[0]
        else:
            graph_def = QueryTransformer.merge_graphs(graph_defs)

        graph_def.build(self, vx_args, eg_args)
        return graph_def

