import time
import polars as pl
from decimal import Decimal, getcontext

getcontext().prec = 50


class TreeNode:
    def __init__(self, content):
        self.parent = None
        self.left = None
        self.right = None
        self.height = 1
        self.count = 1
        self.content = content


class ReuseDistanceTree:
    def __init__(self):
        self.root = None
        self.node_map = {}  # content -> node
        self.reuse_distances = {}  # content -> list of reuse distances

    def update_count_and_height(self, node):
        if node:
            node.count = 1 + (node.left.count if node.left else 0) + (node.right.count if node.right else 0)
            node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))

    def get_height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        return self.get_height(node.left) - self.get_height(node.right) if node else 0

    def left_rotate(self, z):
        y = z.right
        z.right = y.left
        if y.left:
            y.left.parent = z
        y.parent = z.parent
        if not y.parent:
            self.root = y
        elif y.parent.left == z:
            y.parent.left = y
        else:
            y.parent.right = y
        y.left = z
        z.parent = y
        self.update_count_and_height(z)
        self.update_count_and_height(y)
        return y

    def right_rotate(self, z):
        y = z.left
        z.left = y.right
        if y.right:
            y.right.parent = z
        y.parent = z.parent
        if not y.parent:
            self.root = y
        elif y.parent.right == z:
            y.parent.right = y
        else:
            y.parent.left = y
        y.right = z
        z.parent = y
        self.update_count_and_height(z)
        self.update_count_and_height(y)
        return y

    def insert_left_most(self, content):
        new_node = TreeNode(content)
        if not self.root:
            self.root = new_node
            return new_node

        current = self.root
        while current.left:
            current = current.left
        current.left = new_node
        new_node.parent = current
        self.update_tree(new_node)
        return new_node

    def update_tree(self, node):
        while node:
            self.update_count_and_height(node)
            balance = self.get_balance(node)
            if balance > 1:
                if self.get_balance(node.left) < 0:
                    node.left = self.left_rotate(node.left)
                node = self.right_rotate(node)
            elif balance < -1:
                if self.get_balance(node.right) > 0:
                    node.right = self.right_rotate(node.right)
                node = self.left_rotate(node)
            node = node.parent

    def rank_of_node(self, node):
        rank = 0
        if node.left:
            rank += node.left.count
        current = node
        while current.parent:
            if current == current.parent.right:
                if current.parent.left:
                    rank += current.parent.left.count + 1
                else:
                    rank += 1
            current = current.parent
        return rank

    def delete_node(self, node):
        if not node:
            return

        if not node.left and not node.right:
            if node == self.root:
                self.root = None
            elif node == node.parent.left:
                node.parent.left = None
            else:
                node.parent.right = None
            self.update_tree(node.parent)
        elif node.left and node.right:
            successor = node.right
            while successor.left:
                successor = successor.left
            node.content = successor.content
            self.node_map[node.content] = node
            self.delete_node(successor)
        else:
            child = node.left if node.left else node.right
            if node == self.root:
                self.root = child
                child.parent = None
            elif node == node.parent.left:
                node.parent.left = child
                child.parent = node.parent
            else:
                node.parent.right = child
                child.parent = node.parent
            self.update_tree(node.parent)


def calculate_reuse_distance_logn(tree, access):
    if access not in tree.node_map:
        node = tree.insert_left_most(access)
        tree.node_map[access] = node
        tree.reuse_distances[access] = []
    else:
        node = tree.node_map[access]
        reuse_distance = tree.rank_of_node(node)
        tree.reuse_distances[access].append(reuse_distance)
        tree.delete_node(node)
        node = tree.insert_left_most(access)
        tree.node_map[access] = node


def calculate_reuse_distances_nlogn(tree, accesses):
    for access in accesses:
        calculate_reuse_distance_logn(tree, access)
    return tree.reuse_distances


def calculate_reuse_distance_n(reuse_distances, last_indices, access, index):
    if access not in reuse_distances:
        reuse_distances[access] = []
        last_indices[access] = index
    else:
        set_of_accesses = set()
        for i in range(last_indices[access] + 1, index):
            set_of_accesses.add(accesses[i])
        reuse_distances[access].append(len(set_of_accesses))
        last_indices[access] = index


def calculate_reuse_distances_n2(accesses):
    reuse_distances = {}
    last_indices = {}
    for index, access in enumerate(accesses):
        calculate_reuse_distance_n(reuse_distances, last_indices, access, index)
    return reuse_distances


def compare_dict(dict1, dict2):
    for key in dict1:
        if dict1[key] != dict2[key]:
            return False
    return True


def calculate_average_reuse_distance(reuse_distances):
    sum_reuse_distances = Decimal(0)
    count = 0
    for key in reuse_distances:
        for reuse_distance in reuse_distances[key]:
            sum_reuse_distances += Decimal(reuse_distance)
            count += 1
    if count == 0:
        return None
    return sum_reuse_distances / Decimal(count)


def calculate_median_reuse_distance(reuse_distances):
    reuse_distances_list = []
    for key in reuse_distances:
        for reuse_distance in reuse_distances[key]:
            reuse_distances_list.append(reuse_distance)
    if len(reuse_distances_list) == 0:
        return None
    reuse_distances_list.sort()
    n = len(reuse_distances_list)
    if n % 2 == 0:
        return (reuse_distances_list[n // 2 - 1] + reuse_distances_list[n // 2]) / 2
    return reuse_distances_list[n // 2]


def calculate_min_max_reuse_distance(reuse_distances):
    min_reuse_distance = float('inf')
    max_reuse_distance = 0
    for key in reuse_distances:
        for reuse_distance in reuse_distances[key]:
            min_reuse_distance = min(min_reuse_distance, reuse_distance)
            max_reuse_distance = max(max_reuse_distance, reuse_distance)
    if min_reuse_distance == float('inf'):
        return None, None
    return min_reuse_distance, max_reuse_distance


def calculate_std_reuse_distance(reuse_distances):
    average = calculate_average_reuse_distance(reuse_distances)
    sum_squared_diff = Decimal(0)
    count = 0
    for key in reuse_distances:
        for reuse_distance in reuse_distances[key]:
            sum_squared_diff += (Decimal(reuse_distance) - average) ** 2
            count += 1
    if count == 0:
        return None
    return (sum_squared_diff / Decimal(count)).sqrt()


def calculate_max_access_count(reuse_distances):
    max_access_count = 0
    for key in reuse_distances:
        max_access_count = max(max_access_count, len(reuse_distances[key]) + 1)
    return max_access_count


def calculate_average_access_count(reuse_distances):
    sum_access_count = 0
    count = 0
    for key in reuse_distances:
        sum_access_count += len(reuse_distances[key]) + 1
        count += 1
    if count == 0:
        return None
    return sum_access_count / count


def calculate_median_access_count(reuse_distances):
    access_counts = []
    for key in reuse_distances:
        access_counts.append(len(reuse_distances[key]) + 1)
    if len(access_counts) == 0:
        return None
    access_counts.sort()
    n = len(access_counts)
    if n % 2 == 0:
        return (access_counts[n // 2 - 1] + access_counts[n // 2]) / 2
    return access_counts[n // 2]


def calculate_std_access_count(reuse_distances):
    average = calculate_average_access_count(reuse_distances)
    sum_squared_diff = Decimal(0)
    count = 0
    for key in reuse_distances:
        sum_squared_diff += Decimal((len(reuse_distances[key]) + 1 - average)) ** 2
        count += 1
    if count == 0:
        return None
    return (sum_squared_diff / Decimal(count)).sqrt()


def calculate_distinct_accesses(accesses):
    return len(set(accesses))


def calculate_access_count(accesses):
    return len(accesses)


def calculate_count_one_access_offsets(reuse_distances):
    count = 0
    for key in reuse_distances:
        if len(reuse_distances[key]) == 0:
            count += 1
    return count


for path in ['Alibaba_Traces_P1/A42.csv', 'Alibaba_Traces_P1/A108.csv', 'Alibaba_Traces_P2/A129.csv',
             'Alibaba_Traces_P3/A669.csv']:
    start_time = time.time()
    accesses = pl.read_csv(path, columns=['Offset(Byte)'])['Offset(Byte)'].to_list()
    tree = ReuseDistanceTree()
    reuse_distances = calculate_reuse_distances_nlogn(tree, accesses)
    with open(path.split('/')[0] + '/' + path.split('/')[1] + ' reuse distances.txt', 'w') as f:
        f.write('access count: %s\n' % calculate_access_count(accesses))
        f.write('distinct accesses: %s\n' % calculate_distinct_accesses(accesses))
        f.write('average access count per offset: %s\n' % calculate_average_access_count(reuse_distances))
        f.write('median access count per offset: %s\n' % calculate_median_access_count(reuse_distances))
        f.write('std access count per offset: %s\n' % calculate_std_access_count(reuse_distances))
        f.write('max access count per offset: %s\n' % calculate_max_access_count(reuse_distances))
        f.write('count of offsets with no reuse: %s\n' % calculate_count_one_access_offsets(reuse_distances))
        f.write('average reuse distances: %s\n' % calculate_average_reuse_distance(reuse_distances))
        f.write('median reuse distances: %s\n' % calculate_median_reuse_distance(reuse_distances))
        f.write('std reuse distances: %s\n' % calculate_std_reuse_distance(reuse_distances))
        min_reuse_distance, max_reuse_distance = calculate_min_max_reuse_distance(reuse_distances)
        f.write('min reuse distances: %s\n' % min_reuse_distance)
        f.write('max reuse distances: %s\n' % max_reuse_distance)
        f.write('time: %s\n' % (time.time() - start_time))
        f.write('reuse distances per offset:\n')
        for key in reuse_distances.keys():
            f.write("%s:%s\n" % (key, reuse_distances[key]))
