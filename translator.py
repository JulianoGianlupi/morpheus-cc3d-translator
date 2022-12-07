import xmltodict as x2d


def get_morpheus_as_dict(infile):
    with open(infile, 'r') as f:
        xml_raw = f.read()
    mdict = x2d.parse(xml_raw)
    return mdict["MorpheusModel"]


def get_globals(mdict):
    ccglobs = {}
    globs = mdict["Global"]
    if len(globs["Variable"]):
        for v in globs["Variable"]:
            ccglobs[v["@symbol"]] = v["@value"]
    else:
        ccglobs[globs["Variable"]["@symbol"]] = globs["Variable"]["@value"]

    if len(globs["Constant"]):
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
                # todo: morpheus has a zeroing tag, check it before adding the following string
                ctype_loop += f"\t\t\t{loop['Output']['@symbol-ref']} = 0\n"
                if_neigh = f"\t\t\t\tif neighbor and neighbor.type == self.{ctype_2.upper()}:\n"
                if loop['Input']['@scaling'] == "length":
                    if_neigh += f"\t\t\t\t\t{loop['Output']['@symbol-ref']} += common_surface_area\n"
                else:
                    if_neigh += f"\t\t\t\t\t{loop['Output']['@symbol-ref']} += 1\n"

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


if __name__ == "__main__":
    example = r"./morpheus_examples/CellSorting_2D.xml"
    mdict = get_morpheus_as_dict(example)
    cc3d_globals = get_globals(mdict)
    globals_string = make_globals_str(cc3d_globals)
    neigh_loop = get_neighbors_loops(mdict)
    cc3d_neigh_loops = make_cc3d_neighbors_loops(neigh_loop)
    print("end")
