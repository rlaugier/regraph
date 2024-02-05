# Regraph

Regraph is a tool to help visualize complex requirement matrices.

## Setup:

### Install the main package from the github repo:

It is best to download/clone the repo, so you have access to gui.

```bash
git clone https://github.com/rlaugier/regraph/
cd regraph
python setup.py install
```

### Install the system dependency Graphviz

In order to use the full graph output, you will need a local installation of graphviz (in addition to the python package) that can be installed from (their website)[https://graphviz.org/download/].

## Getting started

Start the gui:

```
cd regraph/gui/
streamlit run regraph_gui.py
```

## To go further

The meaning of each column in the requirement table can be changed using a simple `.toml` configuration file. An example of such file is given in `egraph/regraph/config.toml`. It also controls most of the default display settings.

Future developments expected include:

* Possibility to link directly the application to an online spreadsheet
* Export to graphml document 
* Produce visualisation directly to pyvis 
