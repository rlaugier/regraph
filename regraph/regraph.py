
from astropy import table
from textwrap import wrap
from graphviz import Digraph
import toml
from io import BytesIO
from io import StringIO
from pathlib import Path

parent = Path(__file__).parent.absolute()

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
            # print(arow[input["req_id"]])
            if isinstance(arow[input["req_id"]], str):
                reflist.append(arow[input["req_id"]])
                refdict[arow[input["req_id"]]] = {
                    "Req_id":arow[input["req_id"]],
                    "Type":arow[input["req_family"]],
                    "Description": rewrap(arow[input["req_description"]], self.attributes["wrap_width"]),
                }
                desclist.append( rewrap(arow[input["req_description"]], self.attributes["wrap_width"]))
                if isinstance(arow[input["req_parents"]], str):
                    reflist = string2list(arow[input["req_parents"]])
                    refdict[arow[input["req_id"]]]["parents"] = reflist
                    for alinked in reflist:
                        linklist.append((alinked, arow[input["req_id"]]))
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

def load_config(file=None, string=None):
    if file is not None:
        print("Reading a file")
        with open(file, "r") as myfile:
            config = toml.load(myfile)
    elif string is not None:
        print("Reading a string")
        print(string)
        config = toml.loads(string)
    else:
        raise ValueError("Pleas provide either file or string")
    default_colordict = config["Families"]["Family_colors"]
    default_settings = {
        "align_labels": config["Display"]["align_labels"],
        "penwidth_node": str(config["Display"]["penwidth_node"]),
        "penwidth_labelarrow": str(config["Display"]["penwidth_labelarrow"]),
        "wrap_width": config["Display"]["wrap_width"],
        "font_size": str(config["Display"]["font_size"]),
        # "margin": str(st.number_input("Margin",min_value=0.01, max_value=1.0, value=0.05, step=0.01)),
        "margin": "0.05,0.05"
    }
    input = config["Input"]
    return config, input, default_settings, default_colordict

config, input, default_settings, default_colordict = load_config(file=parent/"config.toml")

    
