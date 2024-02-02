
from astropy import table
from textwrap import wrap
from graphviz import Digraph
from io import BytesIO
from io import StringIO

from astropy.io import ascii

import streamlit as st

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

default_settings = {
    "align_labels": True,
    "penwidth_node": str(3.),
    "penwidth_labelarrow": str(3.),
    "wrap_width": 50,
    "font_size": str(9),
    # "margin": str(st.number_input("Margin",min_value=0.01, max_value=1.0, value=0.05, step=0.01)),
    "margin": "0.05,0.05"
    
}
