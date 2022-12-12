import sys
from os import makedirs, path

from extract_pak import HeapsPak


def explore_node(node: HeapsPak.Header.Entry, parent_path: path = ""):
    node_name = path.join(parent_path, node.name)
    print(f"Exploring node: {node_name}")
    if isinstance(node.body, HeapsPak.Header.Dir):
        if not path.exists(node_name):
            makedirs(node_name)
        # TODO: Iterate over directory, call explore_node recursively
        for n in node.body.entries:
            explore_node(n, parent_path=node_name)
    elif isinstance(node.body, HeapsPak.Header.File):
        # TODO: Save to file using parent path
        body: HeapsPak.Header.File = node.body
        with open(node_name, "wb") as f:
            f.write(body.data)
    else:
        print("Error, unrecognized node!")


if __name__ == "__main__":
    args = sys.argv

    if len(args) < 2:
        exit(1)

    filename = args[1]
    filename_raw = path.splitext(filename)[0]

    root = HeapsPak.from_file(filename)

    if not root:
        exit(1)

    print(f"Successfully loaded {filename}, processing...")

    explore_node(node=root.header.root_entry, parent_path=filename_raw)
