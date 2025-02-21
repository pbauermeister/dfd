STORE = """
"{name}" [shape=none label=<
  <TABLE BORDER="0">
    <TR><TD BGCOLOR="black" WIDTH="6"></TD></TR>
    <TR><TD>{text}</TD></TR>
    <TR><TD BGCOLOR="black" WIDTH="6"></TD></TR>
  </TABLE>>]
""".strip()


CHANNEL = """
"{name}" [shape=none label=<
  <TABLE BORDER="0">
    <TR>
      <TD WIDTH="48"></TD>
      <TD BGCOLOR="black" WIDTH="0" PORT="x"><BR/><BR/></TD>
      <TD WIDTH="48"></TD>
    </TR>
    <TR>
      <TD COLSPAN="3">{text}</TD>
    </TR>
  </TABLE>>]
""".strip()


CHANNEL_HORIZONTAL = """
"{name}" [shape=none label=<
  <TABLE BORDER="0">
    <TR><TD BGCOLOR="black" PORT="x"></TD></TR>
    <TR><TD>{text}</TD></TR>
  </TABLE>>]
""".strip()


DOT_FONT_EDGE = 'fontname="times-italic" fontsize=10'
DOT_FONT_NODE = 'fontname="helvetica" fontsize=10'
DOT_FONT_GRAPH = 'fontname="helvetica" fontsize=9 fontcolor="#000060"'

DOT_GRAPH_TITLE = """graph[label="\n- {title} -" """ + DOT_FONT_GRAPH + """]"""

DOT = (
    """
digraph D {{
  {graph_params}
  edge[color=gray """
    + DOT_FONT_EDGE
    + """]
  node["""
    + DOT_FONT_NODE
    + """]
  {block}
}}
""".strip()
)


GRAPH_PARAMS_CONTEXT_DIAGRAM = 'edge [len=2.25]'


ITEM_EXTERNAL_ATTRS = 'fillcolor=white color=grey fontcolor=grey'
