import nbformat



def load_notebook(path):
    with open(path, 'r', encoding='utf-8') as f:
        return nbformat.read(f, as_version=4)

def save_notebook(notebook, path):
    with open(path, 'w', encoding='utf-8') as f:
        nbformat.write(notebook, f)

