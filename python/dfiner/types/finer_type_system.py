class FinerTypeSystem(object):
    def __init__(self, tree):
        self.tree = tree

    def is_coarse_type(self, node_name):
        return self.tree[node_name]["parent"] is None

    def parent_of(self, node_name):
        return self.tree[node_name]["parent"]

    def types(self):
        return self.tree

    def is_figer_type(self, node_name):
        return self.tree[node_name]["is_figer_type"]

    def a_belongs_to_b(self, fine, coarse):
        it = fine
        while self.tree[it]["parent"]:
            if self.tree[it]["parent"] == coarse:
                return True
            it = self.tree[it]["parent"]
        return False

    def has_type(self, t):
        return t in self.tree

    def get_path(self, node):
        path = []
        it = node
        while self.tree[it]["parent"]:
            path.append(self.tree[it]["parent"])
            it = self.tree[it]["parent"]
        return path


if __name__ == '__main__':
    import yaml
    with open("/home/haowu4/codes/dataless_finer/resources/figer_hier.yaml") as input:
        types = yaml.load(input.read())
    finer_types = FinerTypeSystem(types)
