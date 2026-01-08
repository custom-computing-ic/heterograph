from typing import ChainMap
import itertools
from heterograph.query.qgraph import QGraph
from heterograph.algorithm.dfs import dfs_traversal, get_paths


class QueryProcessorDFS:
    """
    This class employs Depth-First Search (DFS) to traverse a graph and identify matches corresponding to a specified query graph. Only works for graphs that are trees (i.e., no cycles).
    """

    @staticmethod
    def check_depth(root_depth, vx_depth, depth_constr):
        """
        Checks if the vertex depth is within the given depth constraints.

        Args:
            root_depth (int): The depth of the root vertex.
            vx_depth (int): The depth of the current vertex.
            depth_constr (tuple): A tuple containing the minimum and maximum depth constraints.

        Returns:
            bool: True if the vertex depth is within the constraints, False otherwise.
        """

        dist = vx_depth-root_depth

        check_min = depth_constr[0] is None or dist >= depth_constr[0]
        check_max = depth_constr[1] is None or dist <= depth_constr[1]

        return check_min and check_max

    @staticmethod
    def __find_match(g, qgraph, chain, qchain, path_check, root_depth, vx_depths, fd, gd):
        """
        Finds matches in the graph for the given query graph.

        Args:
            g (HGraph): The graph to be searched.
            qgraph (QGraph): The query graph.
            chain (tuple): A tuple representing the current chain in the graph.
            qchain (tuple): A tuple representing the current chain in the query graph.
            path_check (function): A function to check the path validity.
            root_depth (int): The depth of the root vertex.
            fd (optional, can be an integer or a tuple of two integers): This parameter specifies the distance between the root and the first node of the match. If not provided, the distance is unrestricted.
            gd (optional, can be an integer or a tuple of two integers): This parameter specifies the distance between the root and any node of the match. If not provided, the distance is unrestricted.


        Returns:
            list: A list of matches found in the graph.
        """
        def post(g, vx, synth):
            nonlocal qgraph, prefix_vx, prefix_qvx, qvx, rest_path

            synth = list(itertools.chain(*synth))

            vx_depth = vx_depths[vx]

            # fd
            if (fd is None) or (prefix_vx is not None) or QueryProcessorDFS.check_depth(root_depth, vx_depth, fd):
                # gd
                if (gd is None) or  QueryProcessorDFS.check_depth(root_depth, vx_depth, gd):
                    if path_check(g, qgraph, (prefix_vx, vx), (prefix_qvx, qvx)):
                        if len(rest_path) != 0:
                            child_vs = g.out_vx(vx)
                            for c_vx in child_vs:
                                partial_match = QueryProcessorDFS.__find_match(g=g,
                                                                               qgraph=qgraph,
                                                                               chain=(vx, c_vx),
                                                                               qchain=(qvx, rest_path),
                                                                               path_check=path_check,
                                                                               root_depth=root_depth,
                                                                               vx_depths=vx_depths,
                                                                               fd=fd,
                                                                               gd=gd)

                                for pm in partial_match:
                                    pmatch={**pm}
                                    pmatch[qgraph.pmap[qvx]['id']]=vx
                                    synth.append(pmatch)
                        else:
                            synth.append({qgraph.pmap[qvx]['id']:vx})
            return synth

        (prefix_qvx, path) = qchain

        if len(path) == 0:
            return []

        qvx,*rest_path = path
        (prefix_vx, root_vx) = chain

        return dfs_traversal(g=g, vx=root_vx, post=post)

    def run(self, g, qgraph, *, vs=None, path_check=None, match_filter=None, fd=None, gd=None):
        """
        Executes the query on the graph.

        Args:
            g (HGraph): The graph to be queried.
            qgraph (QGraph): the query graph.
            vs (list, optional): The vertices to start the query from. If not specified, then the source vertices of the graph will be used.
            path_check (function, optional): A function to check the path validity between two elements of the match.
            match_filter (function, optional): A function to filter the matches.
            fd (optional, can be an integer or a tuple of two integers): This parameter specifies the distance between the root and the first node of the match. If not provided, the distance is unrestricted.
            gd (optional, can be an integer or a tuple of two integers): This parameter specifies the distance between the root and any node of the match. If not provided, the distance is unrestricted.

        Returns:
            list: A list of results matching the query.
        """

        if path_check is None:
            path_check = lambda g, qgraph, chain, qchain: True

        if match_filter is None:
            match_filter = lambda g, qgraph, match: True

        if fd is not None:
            if type(fd) == int:
                fd=(fd, fd)
            elif type(fd) != tuple or len(fd) != 2:
                raise RuntimeError("invalid fd: expecting an int or an (int, int)!")

        if gd is not None:
            if type(gd) == int:
                gd=(gd, gd)
            elif type(gd) != tuple or len(gd) != 2:
                raise RuntimeError("invalid gd: expecting an int or an (int, int)!")

         # create paths from qgraph
        paths = get_paths(g=qgraph)

        if vs is None:
            vs = g.source

        matches=[]

        vx_depths = { }
        def pre_depth(g, vx, inh):
            if vx in vx_depths:
                raise RuntimeError("[x] This algorithm can only be used with tree graphs!")
            vx_depths[vx] = inh
            return inh + 1

        for vx in vs:
            dfs_traversal(g=g, vx=vx, pre=pre_depth, inh=0)

        for vx in vs:
            for path in paths:
                match=[ m for m in QueryProcessorDFS.__find_match(g=g,
                                                                  qgraph=qgraph,
                                                                  chain=(None, vx),
                                                                  qchain=(None, path),
                                                                  path_check=path_check,
                                                                  root_depth=vx_depths[vx],
                                                                  vx_depths=vx_depths,
                                                                  fd=fd,
                                                                  gd=gd)
                        if match_filter(g, qgraph, m)
                      ]
                matches.extend(match)
        return matches