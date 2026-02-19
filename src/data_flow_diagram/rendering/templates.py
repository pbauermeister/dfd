"""This module holds templates for DOT code generation."""

# ── Item shapes and fills ──────────────────────────────────────────────

SHAPE_PROCESS_CONTEXT = "circle"
SHAPE_PROCESS = "ellipse"
SHAPE_ENTITY = "rectangle"
SHAPE_NONE = "none"

FILL_PROCESS_CONTEXT = "white"
FILL_PROCESS = '"#eeeeee"'

STYLE_PROCESS = "filled"
STYLE_CONTROL = '"filled,dashed"'

# ── Connection attributes ──────────────────────────────────────────────
# Leading space preserved — matches the existing `attrs +=` pattern.

ATTR_CONSTRAINT_LABELED = " style=solid color=invis"
ATTR_CONSTRAINT_HIDDEN = " style=invis dir=none"
ATTR_DIR_BACK = " dir=back"
ATTR_DIR_BOTH = " dir=both"
ATTR_DIR_NONE = " dir=none"
ATTR_CFLOW_TAIL = " arrowtail=normalnormal"
ATTR_CFLOW_HEAD = " arrowhead=normalnormal"
ATTR_STYLE_DASHED = " style=dashed"
ATTR_RELAXED = " constraint=false"

# ── Layout parameters ─────────────────────────────────────────────────

LAYOUT_VERTICAL = "rankdir=TB"
LAYOUT_HORIZONTAL = "rankdir=LR"
ROTATION_DEGREES = 90

# ── Channel, star, frame, engine ──────────────────────────────────────

CHANNEL_PORT = ":x:c"
STAR_NODE_FMT = "__star_{nr}__"
HTML_ITEM_DEFAULTS: dict[str, str] = {"fontcolor": "black", "color": "black"}
ENGINE_CONTEXT = "neato"
ENGINE_DEFAULT = "dot"

# ── DOT templates ─────────────────────────────────────────────────────

STORE = """
"{name}" [shape=none label=<
  <TABLE BORDER="0">
    <TR><TD BGCOLOR="{color}" WIDTH="6"></TD></TR>
    <TR><TD><FONT COLOR="{fontcolor}">{text}</FONT></TD></TR>
    <TR><TD BGCOLOR="{color}" WIDTH="6"></TD></TR>
  </TABLE>>]
""".strip()


CHANNEL = """
"{name}" [shape=none label=<
  <TABLE BORDER="0">
    <TR>
      <TD WIDTH="48"></TD>
      <TD BGCOLOR="{color}" WIDTH="0" PORT="x"><BR/><BR/></TD>
      <TD WIDTH="48"></TD>
    </TR>
    <TR>
      <TD COLSPAN="3"><FONT COLOR="{fontcolor}">{text}</FONT></TD>
    </TR>
  </TABLE>>]
""".strip()


CHANNEL_HORIZONTAL = """
"{name}" [shape=none label=<
  <TABLE BORDER="0">
    <TR><TD BGCOLOR="{color}" PORT="x"></TD></TR>
    <TR><TD><FONT COLOR="{fontcolor}">{text}</FONT></TD></TR>
  </TABLE>>]
""".strip()


# Graphviz font defaults for edges, items, and graph label
DOT_FONT_EDGE = 'fontname="times-italic" fontsize=10'
DOT_FONT_NODE = 'fontname="helvetica" fontsize=10'
DOT_FONT_GRAPH = 'fontname="helvetica" fontsize=9 fontcolor="#000060"'

DOT_GRAPH_TITLE = """graph[label="\n- {title} -" """ + DOT_FONT_GRAPH + """]"""
DOT_GRAPH_NOTITLE = f"graph[{DOT_FONT_GRAPH}]"

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


GRAPH_PARAMS_CONTEXT_DIAGRAM = "edge [len=2.25]"
