import os.path

def preprocess(src_name: str, dfd_src: str, debug: bool,
               snippet_by_name: dict[str, str] = None) -> str:

    src_lines = dfd_src.splitlines()
    new_lines: list[str] = []
    for ln, src_line in enumerate(src_lines):
        pair = src_line.split(maxsplit=1)
        if len(pair) == 2 and pair[0] == '#include':
            name = pair[1]
            if name.startswith('<'):
                if not snippet_by_name:
                    raise RuntimeError(
                        f'At line {ln}: source is not markdown, '
                        f'cannot include snippet "{name}".')
                name0 = name
                name = name[1:]
                snippet = snippet_by_name.get(name) or snippet_by_name.get(name0)
                if not snippet:
                    raise RuntimeError(
                        f'At line {ln}: included snippet "{name}" not found.')
                new_lines.append(snippet)
            else:
                if not os.path.exists(name):
                    raise RuntimeError(
                        f'At line {ln}: included file "{name}" not found.')
                with open(name, encoding='utf-8') as f:
                    snippet = f.read()
                new_lines.append(snippet)
        else:
            new_lines.append(src_line)

    src = '\n'.join(new_lines)
    if debug:
        print()
        print(f'--- {src_name} >>> ---')
        print(src)
        print(f'--- <<< {src_name} ---')

    return src