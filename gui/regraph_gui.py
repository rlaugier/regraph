import regraph
from astropy.io import ascii
from io import BytesIO
from io import StringIO

import streamlit as st

from regraph import default_colordict
from regraph import default_settings


verbose = st.checkbox("Verbose")


st.header("Requirement Graph Processor")
with st.expander("Help"):
    st.write("Allows to convert a requirement list into a human readable graph")
    st.write("This renderer has formatting options")
    st.write("Attributes can be found in [the graphviz documentation](https://graphviz.org/doc/info/attrs.html).")
with st.expander("Options"):
    encoding = st.text_input("Encoding", value="utf-8")
    config_file = st.file_uploader("Load a config", type=["toml"])
    if config_file is not None:
        cfg_string = StringIO(config_file.getvalue().decode("utf-8")).read()
        st.write(cfg_string)
        aconfig, aninput, adefault_settings, adefault_colordict = regraph.load_config(string=cfg_string, verbose=verbose)
        
        del cfg_string
    else:
        if verbose:
            print("using defaults")
        st.write("regraph.default")
        aconfig, aninput, adefault_settings, adefault_colordict = (regraph.dconfig,
                                                            regraph.dinput,
                                                            regraph.default_settings,
                                                            regraph.default_colordict)
myfile = st.file_uploader("Upload a csv spreadsheet:", type=["csv"], )
if myfile is None:
    st.write("Please load a file")
    quit()
mydata = StringIO(myfile.getvalue().decode(encoding))
mylines = mydata.readlines()


mytable = ascii.read(mylines, format="csv", delimiter=",", data_start=1)


with st.sidebar:
    st.write("## Adjust preferences")
    include_legen = st.checkbox("Include legend", value=True)
    user_settings = {
        "align_labels": st.checkbox("Align labels", value=True),
        "penwidth_node": str(st.number_input("Border width", value=3., min_value=0.1, max_value=8., step=0.1)),
        "penwidth_labelarrow": str(st.number_input("Label arrow width", value=3., min_value=0.1, max_value=8.,  step=0.1)),
        "wrap_width": st.number_input("Wrap width", value=50, min_value=5, max_value=100,  step=1),
        "font_size": str(st.number_input("Font size", value=9, min_value=3, max_value=30, step=1)),
        # "margin": str(st.number_input("Margin",min_value=0.01, max_value=1.0, value=0.05, step=0.01)),
        "margin": "0.05,0.05"
        
    }
    
##################################################################
myobj = regraph.RequirementSet(mytable, verbose=verbose,
                            colordict=adefault_colordict, 
                            attributes=user_settings,
                            config=aconfig,
                            input=aninput,
                            )


myobj.refresh_graph_graphviz_labels(verbose=verbose)
if include_legen:
    myobj.draw_legend()

with st.expander("Informations"):
    if st.checkbox("Display source", value=False):
        st.write(mylines)

    st.write(f"File length: {len(mytable)} lines")

    st.write(f"Parsed reqs: {len(myobj.reflist)}")
    st.write(f"Links: {len(myobj.linklist)}")
    if st.checkbox("Show table"):
        mytable
#####################################################################
# proj_name = st.text_input("Project name", value="tac_graph")
if st.checkbox("Show (ok on small graphs)"):
    st.graphviz_chart(myobj.mygraph)

if st.checkbox("Open (preferable for large graphs)"):
    myobj.mygraph.render(view=True)
if st.checkbox("Save"):
    with BytesIO() as buffer:
        myobj.mygraph.render(buffer)
        st.write(buffer.name)

        default_settings = {
            "lwidth": 2
        }
        st.download_button(label="Download graph",
                                data=buffer)

if verbose:
    for akey, anitem in myobj.redict:
        st.write(anitem["Description"])

