MD_OK = """
Some text
```data_flow_diagram diagram1.svg
body 1
```

Some more text
```data_flow_diagram diagram2.svg
body 2
```

Yet more text

```ruby
Baby
```
"""

MD_EXPECTED = [('body 1\n', 'diagram1.svg'), ('body 2\n', 'diagram2.svg')]

ALL_SYNTAX_OK = """
style	vertical
style	horizontal

process	P	Process
process	P2	Process 2
entity	T	Terminal
store	S	Store
channel	C	Channel
channel	C2	Channel 2b

flow	P	C  	data
bflow	P	S	config
signal	P	P2	event
flow 	P2	C2	more data
flow	*	P2	ext data
flow	P	T
"""

SYNTAX_ERROR = """
xyz
"""

DUPLICATE_ITEM_ERROR = """
process	P text
entity P text
"""

MISSING_REF_ERROR = """
process	P text
flow P Q text
"""

DOUBLE_STAR_ERROR = """
flow * * text
"""
