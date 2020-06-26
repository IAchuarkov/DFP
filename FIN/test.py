#!/usr/bin/env python3
# # -*- coding: utf-8 -*-


from fin import build_POC_tree, FIN


def print_tree(node):
    print(f'{node.item_name} : ({node.pre_order}, {node.count})')

    for child in node.children_list:
        print_tree(child)


DB = [
    ['a', 'c', 'g', 'f'],
    ['e', 'a', 'c', 'b'],
    ['e', 'c', 'b', 'i'],
    ['b', 'f', 'h'],
    ['b', 'f', 'e', 'c', 'd']
]

# root = build_POC_tree(DB, 2)

# print_tree(root)

freqs = FIN(DB, 0.4)

# for key, value in freqs.items():
#     print(key, value, value.support, value.nodeset)

for pat in freqs:
    print(f'{pat.itemset}, {pat.support}')
