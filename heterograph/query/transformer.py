from lark import Transformer
from heterograph.query.graphdef import QueryGraphDef

class QueryTransformer(Transformer):
    """
    A class used to transform parsed queries using the LARK grammar defined in :class:`QueryAQL<heterograph.query.aql.QueryAQL>`  into a more usable format.

    This class extends the lark.Transformer class and overrides its methods to provide custom transformations for different types of parsed query components. It basically transforms a string query into a QueryGraphDef object. The format of a QueryGraphDef object is as follows:
        * src (set): The set of source vertices.
        * snk (set): The set of sink vertices.
        * steps (list): The list of steps in the query graph.

    Each step helps construct the QGraph, and is represented by:
       * A vertex (2-tuple): `(vertex_id, vertex_args)`
       * An edge (3-tuple): `(vertex_id_src, vertex_id_tgt, edge_args)`

    Vertex and edge arguments are represented as a tuple containing a list of positional arguments and a dictionary of keyword arguments.
    """
    true_val = lambda self, _: True
    false_val = lambda self, _: False

    def string(self, str):
        """
        Converts a string representation to a Python string.

        Args:
            str (list): A list containing a single string.

        Returns:
            str: The converted Python string.

        """
        s = str[0]
        if s[0] == '"':
            return str[0][1:-1]
        else:
            return s

    def number_int(self, n):
        """
        Converts the first element of the input list `n` to an integer.

        Args:
            n (list): A list containing a single element.

        Returns:
            int: The first element of the input list `n`, converted to an integer.
        """
        return int(n[0])

    def number_float(self, n):
        """
        Converts the first element of the input list `n` to a float.

        Args:
            n (list): A list containing a single element.

        Returns:
            float: The first element of the input list `n` converted to a float.
        """
        return float(n[0])

    def args(self, items):
        """
        Returns the arguments passed to the method.

        Args:
            items (list): A list of items.

        Returns:
            object: If the list contains only one item, that item is returned.
                    Otherwise, the entire list is returned.
        """
        if len(items) == 1:
            return items[0]
        else:
            return items

    def pair(self, items):
        """
        Create a dictionary with the first item as the key and the second item as the value.

        Args:
            items (list): A list of two items.

        Returns:
            dict: A dictionary with the first item as the key and the second item as the value.
        """
        return {items[0]: items[1]}

    def map(self, items):
            """
            Maps the given items and returns the first item.

            Args:
                items (list): A list of items to be mapped.

            Returns:
                The first item in the list.
            """
            return items[0]


    def id(self, items):
            """
            Converts the first item in the given list to a string representation.

            Args:
                items (list): A list of items.

            Returns:
                str: The string representation of the first item in the list.
            """
            return str(items[0])

    def process_args(self, items):
        """
        Process the arguments passed to the method.

        Args:
            items (list or any): The arguments to be processed. It can be a single item or a list of items.

        Returns:
            tuple: A tuple containing two elements - a list of positional arguments and a dictionary of keyword arguments.
        """
        if type(items) != list:
            items = [items]
        args = []
        kwargs = {}
        for arg in items:
            if type(arg) == dict:
                kwargs.update(arg)
            else:
                args.append(arg)
        return (args, kwargs)

    def node(self, items):
        """
        Create a node tuple with arguments.

        Args:
            items (list): A list of items.

        Returns:
            tuple: A tuple containing the first item as the node and the second item as a tuple of arguments.

        """
        if len(items) == 1:
            return (items[0], None)
        else:
            # process args
            (args, kwargs) = self.process_args(items[1])

            return (items[0], (args, kwargs))

    def edge(self, items):
        """
        Process a list of items and return a tuple containing the processed arguments and keyword arguments.

        Args:
            items (list): A list of items to be processed.

        Returns:
            tuple: A tuple containing the processed arguments and keyword arguments. If the list is empty, the tuple will contain `None` for both elements.

        """
        if len(items) == 0:
            return (None, None)
        else:
            # process args
            (args, kwargs) = self.process_args(items[0])
            return (None, (args, kwargs))

    def empty_graph(self, items):
        """
        Creates and returns an empty QueryGraphDef object.

        Parameters:
        - items: A list of items to initialize the graph with.

        Returns:
        - An empty QueryGraphDef object.

        """
        return QueryGraphDef()

    def node_graph(self, items):
        """
        Create a query graph definition based on the given items.

        Args:
            items (list): A list of items representing the graph.

        Returns:
            QueryGraphDef: The query graph definition.

        """
        _id = set([items[0][0]])
        return QueryGraphDef(_id, _id, steps=[items[0]])

    def edge_graph(self, items):
        """
        Constructs a new query graph by connecting the sink nodes of the first graph (`g1`) with the source nodes of the second graph (`g2`) using the specified edge argument.

        Args:
            items (list): A list of items containing the two graphs (`g1` and `g2`) and the edge argument.

        Returns:
            QueryGraphDef: The new query graph with the connected nodes and the updated steps.

        """
        g1 = items[0]
        g2 = items[2]

        new_steps = []
        edge_arg = items[1][1]
        for s in g1.snk:
            for t in g2.src:
                new_steps.append((s, t, edge_arg))

        return QueryGraphDef(src=g1.src, snk=g2.snk, steps=g1.steps + g2.steps + new_steps)

    @staticmethod
    def merge_graphs(items):
        """
        Merge multiple graphs into a single graph.

        Args:
            items (list): A list of graphs to be merged.

        Returns:
            QueryGraphDef: The merged graph.

        """
        gdef = QueryGraphDef()
        for g in items:
            gdef.src.update(g.src)
            gdef.snk.update(g.snk)
            gdef.steps = gdef.steps + g.steps
        return gdef

    def group_graph(self, items):
        """
        Groups the given list of items into a single graph.

        Args:
            items (list): A list of graphs to be merged.

        Returns:
            Graph: The merged graph containing all the items.
        """
        return QueryTransformer.merge_graphs(items)
