class RSet:
    """
    Represents a set of query results.
    """

    @staticmethod
    def distinct(rs, target=None):
        """
        Returns a new query result set with distinct matches based on the specified target.

        Args:
            rs (QueryResultSet): The original query result set.
            target (str or list): The target identifier(s) to consider for distinctness. None means all identifiers.

        Returns:
            QueryResultSet: A new query result set with distinct matches.

        Raises:
            ValueError: If the target identifier does not exist in the query results.
        """
        if target is None:
            target = rs.ids
        else:
            if type(target) == str:
                target = [target]

        pos = []
        for i in target:
            try:
                pos.append(rs.ids.index(i))
            except ValueError:
                raise ValueError(f"Identifier '{i}' does not exist in query results!") from None

        fmatches = []
        stored_matches = set() # keep all vx from column idt
        for match in rs.matches:
            vx_match = tuple([match[p] for p in pos])
            if vx_match not in stored_matches:
                fmatches.append(match)
                stored_matches.add(vx_match)

        qrs = rs.__class__(g=rs.g, qgraph=rs.qgraph, results=fmatches)

        return qrs

    @staticmethod
    def disjoint(rs, target):
        """
        Returns a new query result set with matches that are disjoint with the specified target.

        Args:
            rs (QueryResultSet): The original query result set.
            target (str): The target identifier to check for disjointness.

        Returns:
            QueryResultSet: A new query result set with disjoint matches.

        Raises:
            ValueError: If the target identifier does not exist in the query results.
        """
        nodes = []
        fmatches = []

        try:
            pos = rs.ids.index(target)
        except ValueError:
            raise ValueError(f"Identifier '{target}' does not exist in query results!") from None

        for match in rs.matches:
            include_match = True
            tnode = rs.g[match[pos]]
            for node in nodes:
                if tnode.overlaps(node):
                    include_match = False
                    break
            if include_match:
                fmatches.append(match)
                nodes.append(tnode)

        qrs = rs.__class__(g=rs.g, qgraph=rs.qgraph, results=fmatches)

        return qrs



