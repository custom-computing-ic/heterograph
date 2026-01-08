import copy

class HGraphProps(dict):
    def __init__(self, g):
        self.g = g
        self.vx = { }
        self.eg = { }
        super().__init__()

    def copy_prop_elem(self, new_g, new_elem, elem):
        if type(elem) == int:
            self.g.check_vx(elem, verify=True)
            new_g.check_vx(new_elem, verify=True)
            # we only copy if it exists
            if elem in self.vx:
                new_g.pmap[new_elem] = copy.deepcopy(self.vx[elem])
        elif type(elem) == tuple and len(elem) == 2:
            self.g.check_edge(elem, verify=True)
            new_g.check_edge(new_elem, verify=True)
            if elem in self.eg:
                new_g.pmap[new_elem] = copy.deepcopy(self.eg[elem])
        else:
            raise RuntimeError("invalid element '%s' specified!" % str(key))


    def rm_elem(self, elem):
        if type(elem) == int:
            if elem in self.vx:
               del self.vx[elem]
        elif type(elem) == tuple and len(elem) == 2:
            if elem in self.eg:
               del self.eg[elem]
        else:
            raise RuntimeError("invalid element '%s' specified!" % str(key))

    def __getitem__(self, key):
        if type(key) == int:
            # vertex
            self.g.check_vx(key, verify=True)

            # dynamic generation of property map
            if key not in self.vx:
                self.vx[key] = { }
            return self.vx[key]

        if type(key) == tuple and len(key) == 2:
            self.g.check_edge(key, verify=True)
            if key not in self.eg:
                self.eg[key] = {}

            return self.eg[key]

        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if type(key) == int:
            # vertex
            if type(value) != dict:
               raise RuntimeError("property map value must be 'dict' type!")

            self.vx[key] = value
        elif type(key) == tuple and len(key) == 2:
            # vertex
            if type(value) != dict:
               raise RuntimeError("property map value must be 'dict' type!")

            self.eg[key] = value
        else:
           super().__setitem__(key, value)