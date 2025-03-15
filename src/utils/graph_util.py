from collections import deque

def has_cycle(graph):
    """
    Determine whether an undirected graph has a cycle
    :param graph: an undirected graph represented as a dictionary of lists
    :return: True if the graph has a cycle, False otherwise
    """
    def dfs(node, parent):
        visited[node] = True
        for neighbor in graph[node]:
            if not visited[neighbor]:
                if dfs(neighbor, node):
                    return True
            elif neighbor != parent:
                return True
        return False

    visited = [False] * len(graph)
    for i in range(len(graph)):
        if not visited[i]:
            if dfs(i, -1):
                return True
    return False

def build_reverse_graph(graph):
    """Build a reverse adjacency list to record the parent node of each node"""
    reverse_graph = {}
    for node in graph:
        for child in graph[node]:
            if child not in reverse_graph:
                reverse_graph[child] = []
            reverse_graph[child].append(node)
        # Ensure that all nodes have entries in the reverse graph (even if they have no parent)
        if node not in reverse_graph:
            reverse_graph[node] = []
    return reverse_graph


def find_ancestors(target, graph):
    """Find all ancestor nodes of the target node (excluding itself)"""
    reverse_graph = build_reverse_graph(graph)
    ancestors = set()
    direct_parents = reverse_graph.get(target, [])
    queue = deque(direct_parents)
    ancestors.update(direct_parents)

    while queue:
        node = queue.popleft()
        for parent in reverse_graph.get(node, []):
            if parent not in ancestors and parent != target:
                ancestors.add(parent)
                queue.append(parent)
    return ancestors

def topological_sort(graph):
    """Topological sort of a directed acyclic graph (DAG)"""
    in_degree = {u: 0 for u in graph}
    for u in graph:
        for v in graph[u]:
            in_degree[v] += 1

    queue = deque([u for u in graph if in_degree[u] == 0])

    topo_order = []

    while queue:
        u = queue.popleft()
        topo_order.append(u)
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    if len(topo_order) == len(graph):
        return topo_order
    else:
        raise ValueError("Graph has cycle, cannot topological sort")


def topological_sort_node_parent(graph, node_id):
    """ Topological sort of a directed acyclic graph (DAG) with node parents"""
    in_degree = {u: 0 for u in graph}
    for u in graph:
        for v in graph[u]:
            in_degree[v] += 1

    queue = deque([u for u in graph if in_degree[u] == 0])

    # Find all ancestors of the target node (excluding itself)
    parents = find_ancestors(node_id, graph)
    parents.add(node_id)

    topo_order = []

    while queue:
        u = queue.popleft()
        topo_order.append(u)
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    if len(topo_order) == len(graph):
        for i in range(len(topo_order)):
            # If the node is not an ancestor of the target node, set it to None
            if topo_order[i] not in parents:
                topo_order[i] = None
        return topo_order
    else:
        raise ValueError("Graph has cycle, cannot topological sort")
    return None