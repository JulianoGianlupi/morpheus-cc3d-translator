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


def main(file_to_translate):
    mdict = get_morpheus_as_dict(file_to_translate)
    cc3d_globals = get_globals(mdict)
    globals_string = make_globals_str(cc3d_globals)


if __name__ == "__main__":
    example = r"./morpheus_examples/CellSorting_2D.xml"
    mdict = get_morpheus_as_dict(example)
    cc3d_globals = get_globals(mdict)
    globals_string = make_globals_str(cc3d_globals)
    print("end")
