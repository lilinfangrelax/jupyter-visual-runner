from src.controllers.jupyter_client_executor import JupyterClientExecutor
from src.utils import graph_util


class GraphExecuteController:
    def __init__(self, graph: dict, nodes: dict):
        self.graph = graph
        self.nodes = nodes
        self.jupyter_executor = JupyterClientExecutor("python3")

    def execute_all(self):
        # 1. Execute all nodes in topological order
        topo_order = graph_util.topological_sort(self.graph)
        # 2. Execute
        for node_id in topo_order:
            self.execute(self.nodes[node_id])

    def execute_single_node_and_its_parents(self, node_id):
        topo_order_node_parent = graph_util.topological_sort_node_parent(self.graph, node_id)
        for order_id in topo_order_node_parent:
            if order_id is not None:
                self.execute(self.nodes[order_id])


    def execute(self, node):
        self.jupyter_executor.execute(node)
        pass

    def shutdown_kernel(self):
        self.jupyter_executor.shutdown()