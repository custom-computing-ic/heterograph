from flask import Flask, render_template, request
import threading
import sys, os.path as osp
import inspect
from heterograph.hgraph import HGraph
from heterograph.utils.notebook import is_notebook

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class WebView:
    """
    A Flask-based web app that provides a graphical interface to visualize and interact with heterographs.

    This class creates a web view of heterographs  using Flask, allowing users to navigate through different
    graphs, hover over elements in the graph, and shut down the server when they are done. It also handles user
    interaction with the graphs by executing corresponding handler functions if one exists for the current active
    graph.
    """

    obj = None
    """
    Class-level variable that stores an instance of this WebView class. This is used to access its properties and methods from within static methods.

    Type: WebView

    Note:
         The value of this attribute should be an instance of the WebView class. If it's not set or is not a WebView instance, accessing its properties or methods may result in errors.
    """

    def __init__(self, root_path=None):

        """
        Initializes a WebView instance.

        This method sets up a new WebView instance with Flask and adds URL rules for different routes such as index, first graph, next graph, previous graph, hovering over elements, and shutting down the server.

        The class-level variable `obj` is set to this instance, which can be used to access its properties and methods from within static methods. It also initializes several lists for SVG representations of graphs, their titles, and associated hover functions.

        Finally, if the application is not running in an IPython session (e.g., a Jupyter notebook), it will start the Flask web server on the specified host and port, or defaults to '0.0.0.0' and '8888' respectively. If it's running within an IPython session, it will display the SVG representations of all graphs without starting a server.

        Args:
            root_path (str, optional): The path to the root directory for web application assets. Defaults to None.
                If not provided, it will default to the 'assets' folder in the same directory as this file.
        """

        if root_path is None:
           root_path = osp.join(osp.abspath(osp.dirname(__file__)), 'assets')

        self.svg_graphs = []
        self.titles = []
        self.graphs = []
        self.on_hovers = [] # each graph has its hover
        self.hover_elem = None
        self.web_app = Flask('WebView', root_path=root_path)
        self.web_app.add_url_rule('/', 'index', self.__class__.req_index)
        self.web_app.add_url_rule('/first/', 'first', self.__class__.req_first)
        self.web_app.add_url_rule('/first', 'first', self.__class__.req_first)
        self.web_app.add_url_rule('/next/', 'next', self.__class__.req_next)
        self.web_app.add_url_rule('/next', 'next', self.__class__.req_next)
        self.web_app.add_url_rule('/prev', 'prev', self.__class__.req_prev)
        self.web_app.add_url_rule('/prev/', 'prev', self.__class__.req_prev)
        self.web_app.add_url_rule('/shutdown', 'shutdown', self.__class__.req_shutdown, methods=['POST'])
        self.web_app.add_url_rule('/shutdown/', 'shutdown', self.__class__.req_shutdown, methods=['POST'])
        self.web_app.add_url_rule('/hover/<elem>', 'hover', self.__class__.req_hover, methods=['GET'])

        WebView.obj = self

        self.index = -1

    @property
    def graph(self):
        """Returns the currently active graph in the WebView instance.

        This is a read-only property that returns the currently active graph in the WebView instance. If no graph is selected or an invalid index is being accessed, it will raise a RuntimeError.

        Returns:
            hgraph: The current active graph.

        Raises:
            RuntimeError: If there's no currently active graph (i.e., `self.index` is -1) or if the index is out of bounds.
        """
        if self.index == -1:
            raise RuntimeError("invalid graph access!")
        return self.graphs[self.index]


    def add_graph(self, graph, title='', **kwargs):
        """
        Adds a new graph to the WebView instance.

        This function adds a new graph to the WebView instance, along with its associated title and additional style information in kwargs.
        It updates the SVG representations of all graphs, their titles, and their corresponding hover functions. If an 'on_hover' key exists in the style dictionary of the graph, it is saved as a handler function for that specific graph.

        Args:
            graph (hgraph): The graph to be added to the WebView instance. This should be an instance of HGraph or its subclass.
            title (str, optional): Title of the graph. If not provided, it defaults to an empty string.
                It can be used to identify this graph in the user interface later on.
            **kwargs: Additional style information for the graph, such as colors, sizes, or any other custom attributes.
                These will be passed directly to the HGraph rendering method when rendering the SVG representation of the graph.

        Returns:
            None: This function does not return anything. It only modifies the WebView instance's state.

        Note:
            The `graph` argument should be an instance of HGraph or its subclass.
            If it is not, calling this method may raise errors because certain assumptions about the graph structure are made in the rendering process.
        """

        #g=graph.copy()
        self.graphs.append(graph)
        self.titles.append(title)
        if '!on_hover' in graph.style:
            self.on_hovers.append(graph.style['!on_hover'])
        else:
            self.on_hovers.append(None)

        svg = graph.render(format="svg", pipe=True, **kwargs)
        self.svg_graphs.append(svg.decode('utf8'))


    def run(self, host='0.0.0.0', port='8888'):
        """Starts the Flask web server or displays SVG representations if running in a Jupyter notebook.

        Args:
            host (str, optional): The host address to which the server will be bound. Defaults to '0.0.0.0'.
            port (str, optional): The port on which the server will listen for connections. Defaults to '8888'.

        Returns:
            None

        Note:
            The `run` method checks if it's running in a Jupyter notebook (IPython session). If so, it displays SVG representations without starting a server.
            If not, it starts the Flask web server on the specified host and port, or defaults to '0.0.0.0' and '8888'.
        """

        try:
            __IPYTHON__
            _in_ipython_session = True
        except NameError:
            _in_ipython_session = False
        if _in_ipython_session:
            import IPython.display
            for svg, title in zip(self.svg_graphs, self.titles):
                if title != '':
                  IPython.display.display(IPython.display.HTML(f"<h3 style='color:orange;padding: 10px; border: 1px solid orange; border-radius: 5px; text-align: center;'>{title}</h3>"))
                IPython.display.display(IPython.display.SVG(svg), raw=False)
            return

        host = '0.0.0.0' if host == None else host
        port = '8888' if port == None else port
        self._next_graph()
        print(f"URL: =====[http://{host}:{port}]=====")
        x = threading.Thread(target=self.web_app.run, kwargs=dict(host=host, port=port))
        x.start()
        x.join()
        #self.web_app.run(host=self.host, port=self.port, use_reloader=True)

    @staticmethod
    def req_index():
        """
        Renders and returns the HTML template for the view page.

        This function is used to render and return the HTML template that represents the view page.
        The view page usually provides a graphical interface for users to visualize and interact with heterographs.

        Returns:
           str: A string representation of an HTML template which is rendered for the view page.
        """

        return render_template('view.html')


    @staticmethod
    def req_hover(elem):
        """
        Handles user hover interaction with an element in the current graph.

        This function handles a request to hover over an element in the current active graph,
        executing a handler function if one exists for that specific graph. The element is specified as
        a string `elem`, corresponding to a vertex id (int) or an edge id (int, int).

        Args:
            elem (str): A string representation of the element to hover over.
                It can be a simple number or a tuple in string format. For example, '1' or '(2,3)'.

        Returns:
            dict: An empty dictionary signifying that the event processing is complete.

        Note:
            This method requires a handler function (`on_hover`) to be defined for the current active graph.
            If the handler does not exist, the method will do nothing but still return an empty dictionary.

        """

        if ',' in elem:
            elem = eval('(' + elem + ')')
        else:
            elem = int(elem)

        g = WebView.obj.graphs[WebView.obj.index]

        on_hover = WebView.obj.on_hovers[WebView.obj.index]

        # prevent from invoking multiple times, if the item is different
        if on_hover is not None:
            if (WebView.obj.hover_elem is None) or (elem != WebView.obj.hover_elem):
                if on_hover(g, elem):
                    WebView.obj.hover_elem = elem

        return { }

    @staticmethod
    def req_first():
        """
        Resets and returns the next graph payload.

        This function resets the index of the active graph to -1, then calls `req_next()` to get the next graph's payload.
        The result is a dictionary containing the SVG representation of the current graph, its title, total number of graphs in the viewer, and whether or not there is an hover function for the current graph.

        Returns:
           dict: A dictionary containing the SVG representation of the current graph, its index, title, total number of graphs, and whether or not there is a hover function.
        """
        WebView.obj._reset()
        return WebView.obj.req_next()

    @staticmethod
    def req_next():
        """
        Requests the next graph and returns its payload.

        This function calls a private method `_next_graph()` to get the next graph in the viewer, then uses the `payload()`
        static method to generate a dictionary containing information about that graph.

        Returns:
            dict: A dictionary containing the SVG representation of the current graph, its index, title, total number of graphs,
            and whether or not there is a hover function for the current graph.
        """
        g = WebView.obj._next_graph()
        return WebView.payload(g)

    @staticmethod
    def req_prev():
        """
        Requests the previous graph and returns its payload.

        This function calls a private method `_next_graph()` to get the previous graph in the viewer,
        then uses the `payload()` static method to generate a dictionary containing information about that graph.

        Returns:
            dict: A dictionary containing the SVG representation of the current graph, its index, title, total number of graphs,
                and whether or not there is a hover function for the current graph.
        """

        g = WebView.obj._prev_graph()
        return WebView.payload(g)

    @staticmethod
    def req_shutdown():
        """
        Shuts down the server when user interaction is done.

        This function handles a request to shut down the server, usually initiated by the user once they're done with their interactions.
        The method will retrieve the shutdown function from the Flask app environment and execute it if available. If not, an error will be raised.

        Raises:
           RuntimeError: If there is no Werkzeug Server running to shut down.

        Returns:
           str: A string indicating that the server is about to shutdown.
               Example output: "Server shutting down..."
        """
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return "Server shutting down..."

    @staticmethod
    def payload(g):
        """
        Generates a dictionary containing the SVG representation of a graph, its index, title,
        total number of graphs in the viewer, and whether or not there is an hover
        function for the current graph.

        Args:
            g (hgraph): The graph to be included in the payload.

        Returns:
            dict: A dictionary containing the following keys:
                - 'svg': The SVG representation of the graph.
                - 'index': The index of the current graph.
                - 'title': The title of the current graph.
                - 'ngraphs': The total number of graphs in the viewer.
                - 'hover': A boolean indicating whether or not there is an hover function for the current graph.

        Note:
            This method requires a WebView instance to be defined and its properties should be accessible.

        """
        index = WebView.obj.index
        pl = {'svg': g,
              'index': index,
              'title': WebView.obj.titles[index],
              'ngraphs': len(WebView.obj.svg_graphs),
              'hover': WebView.obj.on_hovers[index] is not None
              }
        return pl


    def _reset(self):
        """Resets the active graph index back to -1."""
        self.index = -1


    def _prev_graph(self):
        """
        Get the previous graph from the list of graphs.

        This method returns the SVG representation of the previous graph in the viewer. If there are no graphs, it sets index to -1 and returns None.
        Otherwise, it decrements the current index by 1 (with wrap-around if necessary), retrieves the new current graph from `self.svg_graphs` using the updated index, and returns it.

        Returns:
            The SVG representation of the previous graph in the viewer or None if there are no graphs.
        """
        ngraphs = len(self.svg_graphs)
        if ngraphs == 0:
            self.index = -1
            return None

        self.index = (self.index - 1) % ngraphs
        return self.svg_graphs[self.index]

    def _next_graph(self):
        """
        Get the next graph from the list of graphs.

        This method returns the SVG representation of the next graph in the viewer. If there are no graphs, it sets index to -1 and returns None.
        Otherwise, it increments the current index by 1 (with wrap-around if necessary), retrieves the new current graph and returns it.

        Returns:
            The SVG representation of the next graph in the viewer or None if there are no graphs.
        """
        ngraphs = len(self.svg_graphs)
        if ngraphs == 0:
            self.index = -1
            return None

        self.index = (self.index + 1) % ngraphs
        return self.svg_graphs[self.index]







