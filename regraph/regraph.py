
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


Empty_Cell = "--"

from pdb import set_trace

def string2list(astr):
    if not isinstance(astr, str):
        mystr = str(astr)
    else:
        mystr = astr
    alist = mystr.split(sep=",")
    alist = [anitem.strip() for anitem in alist]
    return alist

def escape_string(string):
    print("Escaping :")
    print(string)
    escaped_string = string.replace('\\', '\\\\')\
                           .replace("http://", "")\
                           .replace("https://", "")\
                           .replace('"', '\\"')\
                           .replace('\n', '\\n')\
                           .replace('\r', '\\r')\
                           .replace('\t', '\\t')\
                           .replace('\b', '\\b')\
                           .replace('\f', '\\f')
    print("To:" )
    print(escaped_string)
    return escaped_string

def rewrap(astring, nchar):
    escaped_string = escape_string(astring)
    newstring = "\n".join(wrap(escaped_string, width=nchar))
    return newstring



# Rading the list of requirements
class RequirementSet(object):
    def __init__(self, mytable, colordict=None, verbose=False,
                attributes=None, config=None, input=None):
        if colordict is not None:
            self.colordict = colordict
        else :
            self.colordict = default_colordict
        if attributes is not None:
            self.attributes = attributes
        else:
            self.attributes = default_settings
        if config is None:
            self.config = dconfig
        else:
            self.config = config
        if input is None:
            self.input = dinput
        else:
            self.input = input
            
        self.table = mytable
        self.verbose = verbose
        # set_trace()
        self.read_table(mytable)

    def read_table(self, mytable):
        reflist = []
        refdict = {}
        desclist = []
        linklist = []
        if self.verbose:
            print("Starting to read")
            print("=====================")
            print(self.table.colnames)
        for arow in self.table:
            if self.verbose:
                print(arow)
                # st.write(arow)
            if self.verbose:
                st.write("input in read_table")
                st.write(self.input)
                print("dict?", isinstance(self.input, dict))
                print("Getting column:", self.input["req_id"])
                print(isinstance(arow[self.input["req_id"]], str))
            if isinstance(arow[self.input["req_id"]], str):
                reflist.append(arow[self.input["req_id"]])
                refdict[arow[self.input["req_id"]]] = {
                    "Req_id":arow[self.input["req_id"]],
                    "Type":arow[self.input["req_family"]],
                    "Comments":rewrap(str(arow[self.input["req_comments"]]), self.attributes["wrap_width"]),
                    "Description": rewrap(str(arow[self.input["req_description"]]), self.attributes["wrap_width"]),
                }
                if "link" in self.input:
                    if arow[self.input["link"]] != "--":
                        refdict[arow[self.input["req_id"]]]["Link"] = arow[self.input["link"]]
                    else:
                        refdict[arow[self.input["req_id"]]]["Link"] = None
                myitem = refdict[arow[self.input["req_id"]]]
                myitem["Common"] = f"{myitem['Req_id']}  --  {myitem['Description']}"
                desclist.append( rewrap(arow[self.input["req_description"]], self.attributes["wrap_width"]))
                if isinstance(arow[self.input["req_parents"]], str):
                    reflist = string2list(arow[self.input["req_parents"]])
                    refdict[arow[self.input["req_id"]]]["parents"] = reflist
                    for alinked in reflist:
                        linklist.append((alinked, arow[self.input["req_id"]]))
        # Quick fix: when types are int, then it poses proble to match with colors.
        for akey, anitem in refdict.items():
            if not isinstance(anitem["Type"], str):
                anitem["Type"] = str(anitem["Type"])
        # End fix
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

    def refresh_graph_graphviz_labels(self, verbose):
        self.mygraph = Digraph()
        self.mygraph.attr(rankdir="LR")
        self.mygraph.attr("node", )
        # print(self.colordict)
        for akey, anitem in self.refdict.items():
            if verbose:
                print(anitem["Type"])
                print("Type is string", isinstance(anitem["Type"], str))
                print("self.colordict", self.colordict)
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

    def refresh_graph_graphviz(self, verbose):
            self.mygraph = Digraph()
            self.mygraph.attr(rankdir="LR")
            self.mygraph.attr("node", )
            # print(self.colordict)
            for akey, anitem in self.refdict.items():
                if verbose:
                    print(anitem["Type"])
                self.mygraph.node(anitem["Common"], shape="rect",
                                color=self.colordict[anitem["Type"]],
                                penwidth=self.attributes["penwidth_node"],
                                href=anitem["Link"])
                with self.mygraph.subgraph() as s:
                    if self.attributes["align_labels"]:
                        s.attr(rank="sink")
                    if anitem["Comments"] != "--":
                        s.node(anitem["Comments"], shape="rect",
                                 color=self.colordict[anitem["Type"]],
                                penwidth=self.attributes["penwidth_node"],
                                margin=self.attributes["margin"],
                                fontsize=self.attributes["font_size"])
                if anitem["Comments"] != "--":
                    self.mygraph.edge(anitem["Common"], anitem["Comments"],
                                color=self.colordict[anitem["Type"]],
                                penwidth=self.attributes["penwidth_labelarrow"])
            for alink in self.linklist:
                linkstart = self.refdict[alink[0]]["Common"]
                linkend = self.refdict[alink[1]]["Common"]
                self.mygraph.edge(linkstart, linkend)
            
    def display_graph(self):
        st.graphviz_chart(self.mygraph)

def load_config(file=None, string=None, verbose=False):
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
    if verbose:
        print("Loading config:")
        print("config:")
        print(config)
        print("input:")
        print(input)
        print("input['req_id']")
        print(input["req_id"])
    return config, input, default_settings, default_colordict

dconfig, dinput, default_settings, default_colordict = load_config(file=parent/"config.toml")

    
