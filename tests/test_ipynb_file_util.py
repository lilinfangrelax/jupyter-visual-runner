from src.controllers.graph_execute_controller import GraphExecuteController
from src.models.JupyterNodeModel import JupyterNodeModel
from src.utils.ipynb_file_util import load_notebook, save_notebook
import unittest

class TestIpynbFileUtil(unittest.TestCase):
    def test_load_notebook(self):
        notebook = load_notebook('D:\\Dev\\GitHub\\ideas\\scripts\\获取邮箱账号注册过的所有网站\\获取邮箱账号注册过的所有网站.ipynb')
        for cell in notebook.cells:
            print(cell.source)
        self.assertIsNotNone(notebook)

    def test_create_jupyter_node_model(self):
        notebook = load_notebook('D:\\Dev\\GitHub\\ideas\\scripts\\获取邮箱账号注册过的所有网站\\获取邮箱账号注册过的所有网站.ipynb')
        graph_nodes_table = {}
        nodes = {}
        count = 0
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                count += 1
                node_model = JupyterNodeModel(cell.source.split('\n')[0], cell.source)
                graph_nodes_table[node_model.title] = []
                nodes[node_model.title] = node_model

        # assert nodes length
        self.assertEqual(len(nodes), count)
        self.assertIsNotNone(nodes.items())


    def test_run_nodebook(self):
        notebook = load_notebook('D:\\Dev\\GitHub\\ideas\\scripts\\获取邮箱账号注册过的所有网站\\获取邮箱账号注册过的所有网站.ipynb')
        graph_nodes_table = {}
        nodes = {}
        count = 0
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                count += 1


                node_model = JupyterNodeModel(cell.source.split('\n')[0], cell.source)
                graph_nodes_table[node_model.title] = []
                nodes[node_model.title] = node_model

        graph = graph_nodes_table

        the_nodes = {}
        for node in nodes.values():
            the_nodes[node.title] = node.code
        self.controller = GraphExecuteController(graph, the_nodes)
        self.controller.execute_all()

