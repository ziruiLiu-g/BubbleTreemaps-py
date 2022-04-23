import circlify as circ


class Hierarchy:
    def __init__(self):
        self.parent = None
        self.name = None
        self.level = 0
        self.r = 0
        self.uncertainty = 0
        self.children = []
        self.height = 0
        self.color = ''
        self.contourPadding = 0
        self.planckPadding = 0
        self.value = 0
        self.x = 0
        self.y = 0
        self.r = 0

    def build(self, data):
        self.create(data, None, 0)
        self.sum_value()
        self.get_cord()
        return self

    def create(self, data, parent, level):
        self.parent = parent
        if 'size' in data.keys():
            self.value = data['size']
        if 'uncertainty' in data.keys():
            self.uncertainty = data['uncertainty']
        self.name = data['name']
        self.level = level

        if 'children' not in data.keys():
            self.height = 0
            return self.level

        childs = data['children']
        max_level = 0
        for c in childs:
            h = Hierarchy()
            lv = h.create(c, self, level + 1)
            self.children.append(h)
            self.height = max(self.height, lv - level)
            max_level = max(max_level, lv)
        return max_level

    def all_nodes(self):
        list = []
        list.append(self)
        for n in self.children:
            list += (n.all_nodes())

        return list

    def print_all_nodes(self):
        print(self.name)
        for n in self.children:
            n.print_all_nodes()

    def descendants(self):
        return self.all_nodes()

    def search_level(self, lv):
        desc = []
        for node in self.descendants():
            if node.level == lv:
                desc.append(node)

        return desc

    def ancestors(self):
        node = self
        res = []
        while node is not None:
            res.append(node)
            node = node.parent
        return res

    def leaves(self):
        leaves = []
        if len(self.children) == 0:
            leaves.append(self)
        else:
            for n in self.children:
                leaves += (n.leaves())

        return leaves

    def path(self, target):
        res = []
        node = self
        while node is not None and node != target:
            res.append(node)
            node = node.parent
        return res

    def sum_value(self):
        for c in self.children:
            c.sum_value()
            self.value += c.value
        return self

    def get_cord(self):
        dic = [self.to_dict()]
        circles = circ.circlify(dic, show_enclosure=False)
        all_nodes = self.all_nodes()
        for n in all_nodes:
            for c in circles:
                if n.name == c.ex['id']:
                    n.r = c.r * 1000
                    n.x = (c.x + 1) * 1000
                    n.y = (c.y + 1) * 1000

    def to_dict(self):
        dic = {}
        dic['id'] = self.name
        dic['datum'] = self.value
        if len(self.children) > 0:
            dic['children'] = []
            for i in self.children:
                dic['children'].append(i.to_dict())
        return dic

    def __str__(self):
        return "parent: {0}, name: {1}, level: {2}, value: {3}, uncer: {4}, height: {5}, color: {6}, x: {7}, y: {8}, r: {9}" \
            .format(self.parent.name if self.parent is not None else None,
                    self.name,
                    self.level,
                    self.value,
                    self.uncertainty,
                    self.height,
                    self.color,
                    self.x,
                    self.y,
                    self.r)


# import json
#
# data = json.loads(open('data.json').read())
# h = Hierarchy()
# h.build(data).sum_value().get_cord()
#
# for n in h.all_nodes():
#     print(str(n))
