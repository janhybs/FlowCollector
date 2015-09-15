# encoding: utf-8
# author:   Jan Hybs

import clang.cindex
p = '/home/jan-hybs/Dokumenty/Smartgit-flow/flow123d/src/main.cpp'
l = '/usr/lib/x86_64-linux-gnu/libclang-3.6.so.1'


clang.cindex.Config.set_library_file(l)
index = clang.cindex.Index.create()
tu = index.parse(p)
node = tu.cursor

def find (node, level=0):
    print "{line} {level} {kind} ".format(level=level * '-', kind=node.kind, line=node.location)
    if str(node.kind.name) == 'CLASS_DECL':
        ref_node = node.get_definition()
        print ref_node.spelling

    for child in node.get_children():
        find(child, level+1)


# find(node)

