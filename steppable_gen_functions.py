"""
MIT License

Copyright (c) 2022 Juliano Ferrari Gianlupi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def _add_to_function(function, extra):
    return function + '\n' + extra + '\n'


def add_to_imports(imports, additional_imports):
    return _add_to_function(imports, additional_imports)


def add_to_init(init, additional_init):
    return _add_to_function(init, additional_init)


def add_to_start(start, additional_start):
    return _add_to_function(start, additional_start)


def add_to_step(step, additional_step):
    return _add_to_function(step, additional_step)


def add_to_finish(finish, additional_finish):
    return _add_to_function(finish, additional_finish)


def add_to_on_stop(on_stop, additional_on_stop):
    return _add_to_function(on_stop, additional_on_stop)


def generate_cell_type_loop(ctype, ntabs):
    tab = ''
    for i in range(ntabs):
        tab += '\t'

    return tab + f"for cell in self.cell_list_by_type(self.{ctype.upper()}):\n"


def steppable_imports():
    imports = '''from cc3d.cpp.PlayerPython import *\nfrom cc3d import CompuCellSetup
from cc3d.core.PySteppables import *\nimport numpy as np\n
'''
    return imports


def steppable_declaration(step_name, mitosis=False):
    if not mitosis:
        stype = "SteppableBasePy"
    else:
        stype = "MitosisSteppableBase"
    return f"class {step_name}Steppable({stype}):\n"


def mitosis_init(frequency):
    return f'''\n\tdef __init__(self,frequency={frequency}):
\t\tMitosisSteppableBase.__init__(self,frequency)\n'''


def steppable_init(frequency, mitosis=False):
    if mitosis:
        return mitosis_init(frequency)
    return f'''\n\tdef __init__(self, frequency={frequency}):
\t\tSteppableBasePy.__init__(self,frequency)\n'''


def steppable_start():
    return '''
\tdef start(self):
\t\t"""
\t\tCalled before MCS=0 while building the initial simulation
\t\t"""'''


def steppable_step():
    step = '''
\tdef step(self, mcs):
\t\t"""
\t\tCalled every frequency MCS while executing the simulation
\t\t:param mcs: current Monte Carlo step
\t\t"""\n
'''
    return step


def steppable_finish():
    finish = '''
\tdef finish(self):
\t\t"""
\t\tCalled after the last MCS to wrap up the simulation. Good place to close files and do post-processing
\t\t"""\n
'''
    return finish


def steppable_on_stop():
    stop = '''
\tdef on_stop(self):
\t\t"""
\t\tCalled if the simulation is stopped before the last MCS
\t\t"""
\t\tself.finish()\n
'''
    return stop


# todo: use frequency when generating the steppable.
def generate_steppable(step_name, frequency, mitosis, minimal=False, already_imports=False, additional_init=None,
                       additional_start=None, additional_step=None, additional_finish=None, additional_on_stop=None,
                       additional_imports=None):
    imports = steppable_imports()
    if additional_imports is not None:
        imports = add_to_imports(imports, additional_imports)
    declare = steppable_declaration(step_name, mitosis=mitosis)
    init = steppable_init(frequency, mitosis=mitosis)
    if additional_init is not None:
        init = add_to_init(init, additional_init)

    start = steppable_start()
    if additional_start is not None:
        start = add_to_start(start, additional_start)
    else:
        start += "\n\t\tpass\n"

    step = steppable_step()
    if additional_step is not None:
        step = add_to_step(step, additional_step)
    else:
        step += "\n\t\tpass\n"

    finish = steppable_finish()

    if additional_finish is not None:
        finish = add_to_finish(finish, additional_finish)

    finish += "\n\t\treturn\n"

    on_stop = steppable_on_stop()

    if additional_on_stop is not None:
        on_stop = add_to_on_stop(on_stop, additional_on_stop)

    if minimal and already_imports:
        return declare + init + start + "\n"
    elif minimal:
        return imports + declare + init + start + "\n"
    elif not already_imports:
        return imports + declare + init + start + step + finish + on_stop + "\n"
    return declare + init + start + step + finish + on_stop + "\n"


if __name__ == "__main__":
    test_step = generate_steppable("test", 1, False)
    test_mit = generate_steppable("mit", 1, True)
    pass