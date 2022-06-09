import inspect
from subprocess import check_output
from IPython.core.display import HTML

def view_source_code(f):
    output = check_output(["pygmentize","-f","html","-O","full,style=emacs","-l","python"],
        input=inspect.getsource(f), encoding='ascii')
    display(HTML(output))