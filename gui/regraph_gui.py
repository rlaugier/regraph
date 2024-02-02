
from astropy import table
from textwrap import wrap
from graphviz import Digraph
from io import BytesIO
from io import StringIO

import streamlit as st

verbose = st.checkbox("Verbose")

def string2list(astr):
    if not isinstance(astr, str):
        mystr = str(astr)
    else:
        mystr = astr
    alist = mystr.split(sep=",")
    alist = [anitem.strip() for anitem in alist]
    return alist
def rewrap(astring, nchar):
    newstring = "\n".join(wrap(astring, width=nchar))
    return newstring

# Rading the list of requirements
class RequirementSet(object):
    def __init__(self, mytable, colordict=None, verbose=False,
                attributes=None):
        if colordict is not None:
            self.colordict = colordict
        else :
            self.colordict = default_colordict
        if attributes is not None:
            self.attributes = attributes
        else:
            self.attributes = default_settings
        self.table = mytable
        reflist = []
        refdict = {}
        desclist = []
        linklist = []
        if verbose:
            print("Starting to read")
            print("=====================")
            print(self.table.colnames)
        for arow in self.table:
            if verbose:
                print(arow)
                st.write(arow)
            # print(arow["#"])
            if isinstance(arow["#"], str):
                reflist.append(arow["#"])
                refdict[arow["#"]] = {
                    "#":arow["#"],
                    "Type":arow["Type"],
                    "Description": rewrap(arow["Description"], self.attributes["wrap_width"]),
                }
                desclist.append( rewrap(arow["Description"], self.attributes["wrap_width"]))
                if isinstance(arow["Linked req"], str):
                    reflist = string2list(arow["Linked req"])
                    refdict[arow["#"]]["parents"] = reflist
                    for alinked in reflist:
                        linklist.append((alinked, arow["#"]))
        self.reflist = reflist
        self.refdict = refdict
        self.desclist = desclist
        self.linklist = linklist

    def draw_legend(self,):
        with self.mygraph.subgraph(name="cluster_legend") as legend:
            for akey, acolor in self.colordict.items():
                legend.attr(style="flled", rank="source",)
                legend.node(akey, color=acolor,
                                    penwidth=self.attributes["penwidth_labelarrow"],
                            shape="rect", margin="0.02,0.02")

    def refresh_graph_graphviz(self, verbose):
        self.mygraph = Digraph()
        self.mygraph.attr(rankdir="LR")
        self.mygraph.attr("node", )
        # print(self.colordict)
        for akey, anitem in self.refdict.items():
            if verbose:
                print(anitem["Type"])
            self.mygraph.node(akey, shape="ellipse",
                            color=self.colordict[anitem["Type"]],
                            penwidth=self.attributes["penwidth_node"])
            with self.mygraph.subgraph() as s:
                if self.attributes["align_labels"]:
                    s.attr(rank="sink")
                s.node(anitem["Description"], shape="rect",
                             color=self.colordict[anitem["Type"]],
                            penwidth=self.attributes["penwidth_node"],
                            margin=self.attributes["margin"],
                            fontsize=self.attributes["font_size"])
            self.mygraph.edge(akey, anitem["Description"],
                            color=self.colordict[anitem["Type"]],
                            penwidth=self.attributes["penwidth_labelarrow"])
        for alink in self.linklist:
            self.mygraph.edge(alink[0], alink[1])

    def display_graph(self):
        st.graphviz_chart(self.mygraph)

default_colordict = {
    "Technical req": "#d08770",
    "Science": "#88c0d0",
    "Functional": "#a3be8c",
}


st.header("Requirement Graph Processor")
with st.expander("Help"):
    st.write("Allows to convert a requirement list into a human readable graph")
    st.write("This renderer has formatting options")
    st.write("Attributes can be found in [the graphviz documentation](https://graphviz.org/doc/info/attrs.html).")
with st.expander("Options"):
    encoding = st.text_input("Encoding", value="utf-8")
myfile = st.file_uploader("Upload a csv spreadsheet:", type=["csv"], )
if myfile is None:
    st.write("Please load a file")
    quit()
mydata = StringIO(myfile.getvalue().decode(encoding))
mylines = mydata.readlines()

from astropy.io import ascii

mytable = ascii.read(mylines, format="csv", delimiter=",", data_start=1)


with st.sidebar:
    include_legen = st.checkbox("Include legend", value=True)
    default_settings = {
        "align_labels": st.checkbox("Align labels", value=True),
        "penwidth_node": str(st.number_input("Border width", value=3., min_value=0.1, max_value=8., step=0.1)),
        "penwidth_labelarrow": str(st.number_input("Label arrow width", value=3., min_value=0.1, max_value=8.,  step=0.1)),
        "wrap_width": st.number_input("Wrap width", value=50, min_value=5, max_value=100,  step=1),
        "font_size": str(st.number_input("Font size", value=9, min_value=3, max_value=30, step=1)),
        # "margin": str(st.number_input("Margin",min_value=0.01, max_value=1.0, value=0.05, step=0.01)),
        "margin": "0.05,0.05"
        
    }
    
##################################################################
myobj = RequirementSet(mytable, verbose=verbose, colordict=default_colordict)


myobj.refresh_graph_graphviz(verbose=verbose)
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

