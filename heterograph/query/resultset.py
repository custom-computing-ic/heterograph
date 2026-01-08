from tabulate import tabulate
from colorama import Fore, Style
import copy

class QueryResultSet:
    """
    Represents a result set of a query execution.

    Args:
        g (Graph): The graph on which the query was executed.
        qgraph (QueryGraph): The query graph used for the execution.
        results (list): The list of matches in the result set.
    """

    def __init__(self, g, qgraph, results:list):
        """
        Initializes the instance with a graph, a query graph, and a list of results.

        The results can be in two formats:
           - A list of matches, where each match is a dictionary mapping identifiers to vertices: {'id0': vx0, 'id1': vx1... }
           - A list of matches, where each match is a list of vertices: [vx0, vx1, ...]

        Args:
            g: The graph object.
            qgraph: The query graph.
            results (list): The list of results. Each result can be a dictionary mapping identifiers to vertices, or a list of vertices.

        Raises:
            RuntimeError: If an identifier from the query graph is not found in a match from the results.
        """

        self.ids = list(qgraph.pmap['ids'].keys())
        """the list of IDs in the query graph."""

        self.matches = None
        """the list of matches in the result set."""

        if len(results) > 0 and type(results[0]) == dict:
                # convert format 1 to format 2
                self.matches = []
                for  m in results:
                    match = []
                    for _id in self.ids:
                        if _id not in m:
                            #raise RuntimeError(f"cannot find id '{_id }' in result-set!")
                            match.append(None)
                        # we store the result as 'vx' instead of cnode, since the
                        # cnode could be removed, and we lose the ability to track
                        # it
                        else:
                            match.append(m[_id])
                    self.matches.append(match)
        else:
            self.matches = copy.copy(results)

        self.qgraph = qgraph
        """The query graph used for the execution."""

        self.g = g
        """the graph on which the query was executed."""

        self.vs = set(g.vertices)
        """set of vertices in the graph."""

        self.__iter = None
        """iterator object for the result set."""

    def apply(self, action, **kwargs):
        """
        Applies the given action to the result set.

        Args:
           action: The action to apply to the result set.
           kwargs: Additional keyword arguments to pass to the action.

        Returns:
           The result of applying the action to the result set.
        """
        return action(self, **kwargs)

    def _create_match_obj(self, ids, match):
        """
        Creates a match object that represents a query result.

        Args:
            ids (list): A list of IDs corresponding to the query result.
            match (list): A list of matches for the query result.

        Returns:
            Result: An instance of the Result class representing the query result.

        Raises:
            RuntimeError: If a vertex in the query result has been removed.

        """
        class Result:
            def __init__(self, qrs:QueryResultSet, ids, match):

                for _id in match:
                    if _id is not None:
                        if not qrs.g.check_vx(_id):
                            raise RuntimeError("Query result corruption: vertex [%d] has been removed!" % _id)

                self.result = dict(zip(ids, match))

                for r in self.result:
                    vx = self.result[r]
                    if vx is None:
                        self.__setattr__(r, None)
                    else:
                        self.__setattr__(r, qrs.g[self.result[r]])

            @property
            def match(self):
                return self.result

            def __getitem__(self, item):
                return getattr(self, item)

            def __repr__(self):
                return str(self.result)

        return Result(self, ids, match)

    def __repr__(self):

        g_vs = set(self.g.vertices)

        def fmt(match):
            fmatch = []

            for vx in match:
                if vx not in g_vs:
                    fm = f"{Fore.LIGHTRED_EX}({vx}){Style.RESET_ALL}"
                else:
                    fm = f"{Fore.LIGHTBLACK_EX}{vx}{Style.RESET_ALL}"
                fmatch.append(fm)
            return fmatch

        data = [ fmt(match) for match in self.matches ]
        out = tabulate(data, headers=self.ids)
        return out

    @property
    def removed(self):
            """
            Returns the set of vertices that have been removed from the result set.

            Returns:
                set: The set of vertices that have been removed.
            """
            current_vs = set(self.g.vertices)
            return self.vs - current_vs


    @property
    def inserted(self):
        """
        Returns the set of vertices that were inserted into the graph since the creation of this result set.

        Returns:
            set: The set of inserted vertices.
        """
        current_vs = set(self.g.vertices)
        return current_vs - self.vs

    def __iter__(self):
        """Returns an iterator object for the result set."""
        self.__iter = iter(self.matches)

        return self

    def __next__(self):
        """
        Retrieves the next match from the result set.

        Returns:
            A match object created using the ids and match data.

        Raises:
            StopIteration: If there are no more matches in the result set.
        """
        match = next(self.__iter)
        return self._create_match_obj(self.ids, match)

    def __len__(self):
        """
        Returns the number of matches in the result set.

        Returns:
            int: The number of matches in the result set.
        """
        return len(self.matches)

    def __getitem__(self, item):
        """
        Get the item at the specified index.

        Parameters:
            item (int): The index of the item to retrieve.

        Returns:
            object: The item at the specified index.
        """
        return self._create_match_obj(self.ids, self.matches[item])















