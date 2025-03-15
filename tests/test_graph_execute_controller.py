import unittest
from src.controllers.graph_execute_controller import GraphExecuteController
from src.utils import graph_util

class TestGraphExecuteController(unittest.TestCase):

    def setUp(self):
        graph = {
            "A": ["B", "C", "E"],
            "B": [],
            "C": ["D"],
            "D": ["E"],
            "E": []
        }
        nodes = {
            "A": "print('Hello A')",
            "B": "print('Hello B')",
            "C": "print('Hello C')",
            "D": "print('Hello D')",
            "E": "print('Hello E')"
        }
        self.controller = GraphExecuteController(graph, nodes)
    def test_execute_all(self):

        self.controller.execute_all()

    def test_execute_single_node_and_its_parents(self):
        self.controller.execute_single_node_and_its_parents("E")

    def tearDown(self):
        self.controller.shutdown_kernel()
