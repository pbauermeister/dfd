# TODO

P1:
- percent_zoom, default 75?

- dst/dst: (#source|source.ext]:src/dst
  	 - remove prefix
	 - create CheckedStatement(statement) + checked_src, checked_dst
	 - remember checked_statement into to_be_checked[]

	 - before render:
	   - for each checked_statement of to_be_checked()
	     - for checked_src, checked_dst:
	       - if not in source_dict{}: read and parse source
	       - in source, locate item NAME
	       - if not found: error
	       - if statement misses label, take it from source


P2:
- #option ARGS: like cmdline args
- #dot inline-code
