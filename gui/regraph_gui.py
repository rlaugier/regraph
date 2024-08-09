import regraph
from astropy.io import ascii
from io import BytesIO
from io import StringIO

import streamlit as st

from regraph import default_colordict
from regraph import default_settings

LIFE_DEFAULT_CONFIG = """
[Input]
req_id = "ID"
req_family = "Level"
req_description = "Requirement"
req_parents = "Parent ID"
# req_comments = "Rationale and comments"
req_comments = "Assumed parameter's value"
# req_comments = "Verification Method"
link = "Redmine Issue"

[Display]
align_labels = true
penwidth_node = 3.0
penwidth_labelarrow = 3.0
wrap_width = 50
font_size = 9

[Families]
Family_colors = {0 = "#d08770", 1 = "#88c0d0", 2 = "#a3be8c", 3 = "#b197fc"}

"""
ESA_DEFAULT_CONFIG = """
[Input]
req_id = "#"
req_family = "Type"
req_description = "Description"
req_parents = "Linked req"
req_comments = "Comment"
link = "None"

[Display]
align_labels = true
penwidth_node = 3.0
penwidth_labelarrow = 3.0
wrap_width = 50
font_size = 9

[Families]
Family_colors = {Technical req = "#d08770", Science = "#88c0d0", Functional = "#a3be8c"}

"""



verbose = st.checkbox("Verbose")


st.header("Requirement Graph Processor")
with st.expander("Help"):
    st.write("Allows to convert a requirement list into a human readable graph")
    st.write("This renderer has formatting options")
    st.write("Attributes can be found in [the graphviz documentation](https://graphviz.org/doc/info/attrs.html).")
with st.expander("Options"):
    used_defaults = False
    encoding = st.text_input("Encoding", value="utf-8")
    which_config = st.selectbox(label="Starting config", options=["LIFE default", "ESA default", "Upload"])
    if which_config == "LIFE default":
        cfg_string = LIFE_DEFAULT_CONFIG
    elif which_config == "ESA default":
        cfg_string = ESA_DEFAULT_CONFIG
    elif which_config == "Upload":
        config_file = st.file_uploader("Load a config", type=["toml"])
        if config_file is not None:
            cfg_string = StringIO(config_file.getvalue().decode("utf-8")).read()
    else:
        if verbose:
            print("using defaults")
        used_defaults = True
    if not used_defaults:
        modified_cfg_string = st.text_area(label="The configuration text", value=cfg_string,
                                            height=600)
        aconfig, aninput, adefault_settings, adefault_colordict = regraph.load_config(string=modified_cfg_string, verbose=verbose)
        del cfg_string
    else:
        st.write("regraph.default")
        aconfig, aninput, adefault_settings, adefault_colordict = (regraph.dconfig,
                                                            regraph.dinput,
                                                            regraph.default_settings,
                                                            regraph.default_colordict)
with st.expander("More options"):
    st.write("Interactive options")
myfile = st.file_uploader("Upload a csv spreadsheet:", type=["csv"], )
if myfile is None:
    st.write("Please load a file")
    quit()
mydata = StringIO(myfile.getvalue().decode(encoding))
mylines = mydata.readlines()


mytable = ascii.read(mylines, format="csv", delimiter=",", data_start=1)


with st.sidebar:
    st.write("## Adjust preferences")
    box_mode = st.selectbox("What type of display", ["all-in-one", "id-and-label"])
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


if "all-in-one" in box_mode:
    myobj.refresh_graph = myobj.refresh_graph_graphviz
elif "id-and-label" in box_mode:
    myobj.refresh_graph = myobj.refresh_graph_graphviz_labels

myobj.refresh_graph(verbose=verbose)

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
    items_to_show = {"none":None, "reflist":myobj.reflist,
                    "refdict":myobj.refdict, "desclist":myobj.desclist,
                    "linklist":myobj.linklist}
    itemshown = st.selectbox("Item to show", items_to_show.keys())
    st.write(items_to_show[itemshown])    
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
    st.write(myobj.config)
    for akey, anitem in myobj.refdict:
        st.write(anitem["Description"])



