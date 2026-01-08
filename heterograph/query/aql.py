from lark import Lark
from heterograph.query.transformer import QueryTransformer

query_grammar = r"""

id              : /[a-zA-Z][a-zA-Z0-9_]*/

pair: id ":" value

value: pair -> map
    | ESCAPED_STRING -> string
    | SIGNED_INT -> number_int
    | SIGNED_FLOAT -> number_float
    | "True" -> true_val
    | "False" -> false_val
    | id -> string

args            : value
                | args ("," value)*

node            :   id
                  | id "{" args "}"

edge            : "=>"
                | "={" args "}>"

graph           : "(" graph ("|" graph)* ")" -> group_graph
                | "0" -> empty_graph
                | node -> node_graph
                | graph edge graph -> edge_graph



%import common.ESCAPED_STRING
%import common.SIGNED_INT
%import common.SIGNED_FLOAT
%import common.WS
%ignore WS
"""
from lark import Lark

class QueryAQL:
    """
    A class for processing AQL queries and transforming them into graph definitions.

    This class takes in queries and transforms them into graph definitions. The attributes associated with nodes and edges can be either key-value pairs or arguments.

    The AQL grammar in BNF format:
        .. code-block:: text

            <id> ::= /[a-zA-Z][a-zA-Z0-9_]*/
            <pair> ::= <id> ":" <value>

            <value> ::= <pair>             -- map
                    | ESCAPED_STRING     -- string
                    | SIGNED_INT         -- number_int
                    | SIGNED_FLOAT       -- number_float
                    | "True"             -- true_val
                    | "False"            -- false_val
                    | <id>               -- string

            <args> ::= <value>
                    | <args> ("," <value>)*

            <node> ::= <id>
                    | <id> "{" <args> "}"

            <edge> ::= "=>"
                    | "={" <args> "}>"

            <graph> ::= "(" <graph> ("|" <graph>)* ")"   -- group_graph
                    | "0"                             -- empty_graph
                    | <node>                          -- node_graph
                    | <graph> <edge> <graph>          -- edge_graph

            <WS> ::= " "  -- whitespace

            <ESCAPED_STRING> ::= "\"" ( "\\" . | ~["\\])* "\""

            <SIGNED_INT> ::= ["-"] [0-9]+

            <SIGNED_FLOAT> ::= ["-"] [0-9]+ "." [0-9]+


    Note:
            Attributes associated to nodes (**id{attr}**) and edges (**id0 ={attr}> id1**) can be either:
             - key-values: a:2, b:"abc" OR
             - arguments: a,b,c

    Example:
            >>> from heterograph.query.aql import QueryAQL
            >>> aql = QueryAQL()
            >>> lst = [
            ...     "0",   # empty graph
            ...     "abc", # single node
            ...     'abc { a: 1, b: 2.4, c: "3"}', # node with key-value arguments
            ...     'abc { a, b, c}', # node with arguments
            ...     'abc ={ weight: 3.14 }> def', # edge with key-value arguments
            ...     'abc ={ weight: 3.14, color: "black" }> def{ a: 1, b: 2.4, c: "3"}',
            ...     'q => (a|b|c)=>d' # graph with nodes and edges
            ... ]
            >>> for i in lst:
            ...     r = aql.grammar.parse(i)

    """
    def __init__(self):
        """
        Initializes with the specified grammar and transformer.
        """
        global query_grammar
        self.grammar = Lark(query_grammar, start='graph', parser='lalr')
        """the grammar used to parse the queries."""

        self.transformer = QueryTransformer()
        """(QueryTransformer): the transformer used to transform the parsed queries."""

