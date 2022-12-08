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

import xmltodict as x2d
import steppable_gen_functions as sgf


def get_morpheus_as_dict(infile):
    with open(infile, 'r') as f:
        xml_raw = f.read()
    mdict = x2d.parse(xml_raw)
    return mdict["MorpheusModel"]


def get_globals(mdict):
    ccglobs = {}
    globs = mdict["Global"]
    if type(globs["Variable"]) == list:
        for v in globs["Variable"]:
            ccglobs[v["@symbol"]] = v["@value"]
    else:
        ccglobs[globs["Variable"]["@symbol"]] = globs["Variable"]["@value"]

    if type(globs["Constant"]) == list:
        for v in globs["Constant"]:
            ccglobs[v["@symbol"]] = v["@value"]
    else:
        ccglobs[globs["Constant"]["@symbol"]] = globs["Constant"]["@value"]

    return ccglobs


def make_globals_str(ccglo):
    st = ''
    for var, value in ccglo.items():
        p = f"\nglobal {var}\n"
        p += f"{var} = {value}\n"
        st += p
    return st


def get_neighbors_loops(mdict):
    mctype = mdict["CellTypes"]['CellType']
    ccloops = {}
    for typedict in mctype:
        if 'NeighborhoodReporter' in typedict:
            ccloops[typedict['@name']] = typedict['NeighborhoodReporter']
            # if len(typedict['NeighborhoodReporter']):
            #     for report in typedict['NeighborhoodReporter']:

    return ccloops


def make_cc3d_neighbors_loops(ccloops, ccglo=None):
    mega_str = ""
    for ctype, loops in ccloops.items():
        ctype_loop = f"\n\t\tfor cell in self.cell_list_by_type(self.{ctype.upper()}):\n"

        if type(loops) == list:
            ifs = []
            for loop in loops:
                ctype_2 = loop['Input']['@value'].split(".")[-2]
                # todo: morpheus has a zeroing tag, check it to decide when the 0ing should happen
                if loop['Output']['@symbol-ref'] == "boundary":
                    ctype_loop = f"\t\t{loop['Output']['@symbol-ref']} = 0\n" + ctype_loop
                else:
                    ctype_loop += f"\t\t\t{loop['Output']['@symbol-ref']} = 0\n"

                if_neigh = f"\t\t\t\tif neighbor and neighbor.type == self.{ctype_2.upper()}:\n"
                if loop['Input']['@scaling'] == "length":
                    if_neigh += f"\t\t\t\t\t{loop['Output']['@symbol-ref']} += common_surface_area\n"
                else:
                    if_neigh += f"\t\t\t\t\t{loop['Output']['@symbol-ref']} += 1\n"
                if loop['Output']['@symbol-ref'] == "b" or "b2":
                    # todo: refine
                    if_neigh += f"\t\t\t\tcell.dict['{loop['Output']['@symbol-ref']}']=" \
                                f"{loop['Output']['@symbol-ref']}\n"

                ifs.append(if_neigh)
        else:
            ifs = []
            ctype_2 = loops['Input']['@value'].split(".")[-2]
            ctype_loop += f"\t\t\t{loops['Output']['@symbol-ref']} = 0\n"
            if_neigh = f"\t\t\t\tif neighbor and neighbor.type == self.{ctype_2.upper()}:\n"
            if loops['Input']['@scaling'] == "length":
                if_neigh += f"\t\t\t\t\t{loops['Output']['@symbol-ref']} += common_surface_area\n"
            else:
                if_neigh += f"\t\t\t\t\t{loops['Output']['@symbol-ref']} += 1\n"

            ifs.append(if_neigh)

        ctype_loop += f"\t\t\tfor neighbor, common_surface_area in self.get_cell_neighbor_data_list(cell):\n"
        for iif in ifs:
            ctype_loop += iif
        mega_str += ctype_loop

    return mega_str


def main(file_to_translate):
    mdict = get_morpheus_as_dict(file_to_translate)
    cc3d_globals = get_globals(mdict)
    globals_string = make_globals_str(cc3d_globals)
    neigh_loop = get_neighbors_loops(mdict)
    cc3d_neigh_loops = make_cc3d_neighbors_loops(neigh_loop)
    steppable_string = sgf.generate_steppable("example", 1, False, additional_imports=globals_string,
                                              additional_step=cc3d_neigh_loops)
    steppable_string.replace("\t", "    ")


if __name__ == "__main__":
    example = r"./morpheus_examples/CellSorting_2D.xml"
    mdict = get_morpheus_as_dict(example)
    cc3d_globals = get_globals(mdict)
    copy = """
'''
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
'''
"""
    globals_string = make_globals_str(cc3d_globals)
    neigh_loop = get_neighbors_loops(mdict)
    cc3d_neigh_loops = make_cc3d_neighbors_loops(neigh_loop)
    _extra_init = "\t\tself.track_cell_level_scalar_attribute(field_name='Inter_type_neighbors', attribute_name='b')\n" \
                  "\t\tself.track_cell_level_scalar_attribute(field_name='Inter_type_contact', attribute_name='b2')"
    _extra_start = "\t\tself.plot_win = self.add_new_plot_window(title='Inter-type common contact area', x_axis_title=" \
                   "'MonteCarlo Step (MCS)',  y_axis_title='Area', x_scale_type='linear', y_scale_type='linear'," \
                   " grid=True)\n" \
                   "\t\tself.plot_win.add_plot('Area', style='Lines', color='red', size=5)"

    _extra_step = "\n\t\tself.plot_win.add_data_point('Area', mcs, boundary)"
    _extra_step = cc3d_neigh_loops + _extra_step
    steppable_string = sgf.generate_steppable("example", 1, False, additional_imports=copy+globals_string,
                                              additional_step=_extra_step, additional_init=_extra_init,
                                              additional_start=_extra_start)

    steppable_string.replace("\t", "    ")
    with open(r"C:\github\morpheus-cc3d-translator\translated_compucell3d_example\exa"
              r"mple\Simulation\exampleSteppables.py", "w") as f:
        f.write(steppable_string)
    print("end")
