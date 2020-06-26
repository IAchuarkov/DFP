# pylint: disable=missing-docstring
# pylint: disable=invalid-name

#!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from collections import defaultdict
from itertools import product


class POC_Node:
    def __init__(self, item_name):
        self.item_name = item_name
        self.count = 1
        self.children_list = []
        self.pre_order = []


class Pattern:
    def __init__(self, itemset, support):
        self.itemset = itemset
        self.support = support
        self.nodeset = set()

    def __str__(self):
        return str(self.itemset)

    def calc_params(self, freqs):
        self.calc_nodeset(freqs)
        self.calc_support()

    def calc_support(self):
        self.support = 0
        for _, count in self.nodeset:
            self.support += count

    def calc_nodeset(self, freqs):
        self.nodeset = rec_nodeset_calc(self.itemset, freqs)


class Reverse_str_wrapper:
    def __init__(self, obj):
        self.string = str(obj)

    def __eq__(self, other):
        return other.string == self.string

    def __lt__(self, other):
        return other.string < self.string


def rec_nodeset_calc(itemset, freqs):
    if tuple(itemset) in freqs:
        return freqs[tuple(itemset)].nodeset

    return rec_nodeset_calc(itemset[1:], freqs) &\
        rec_nodeset_calc([itemset[0]] + itemset[2:], freqs)


def find_frequent_items(DB, min_support):
    items_dict = defaultdict(int)

    for trans in DB:
        for element in trans:
            items_dict[element] += 1

    return {key: val for key, val in items_dict.items() if val >= min_support}


def insert_tree(Node, itemset):
    rec_node = None

    for node in Node.children_list:
        if node.item_name == itemset[0]:
            node.count += 1
            rec_node = node

    if rec_node is None:
        rec_node = POC_Node(itemset[0])
        Node.children_list.append(rec_node)

    if len(itemset) > 1:
        insert_tree(rec_node, itemset[1:])


def set_pre_orders(Node, node_id):
    Node.pre_order = node_id
    node_id += 1
    for child in Node.children_list:
        node_id = set_pre_orders(child, node_id)

    return node_id


def create_order_dict(F_1_dict):
    L_1_list = sorted(F_1_dict.keys(), key=lambda item:
                      (F_1_dict[item], Reverse_str_wrapper(item)))

    #print(f'L_1_list: {L_1_list}')
    return {key: index for index, key in enumerate(L_1_list)}


def build_POC_tree(DB, min_support):
    F_1_dict = find_frequent_items(DB, min_support)
    L_1_dict = create_order_dict(F_1_dict)
    #print(f'minimal support: {min_support}')
    # print(L_1_dict)

    root = POC_Node('root')

    for trans in DB:
        freq_items = sorted(
            (item for item in trans if item in L_1_dict),
            key=lambda item: L_1_dict[item], reverse=True)

        if freq_items:
            #print(f'transaction: {trans}\tordered: {freq_items}')
            insert_tree(root, freq_items)

    set_pre_orders(root, 0)

    return root, L_1_dict


# def gen_2patterns_1patterns(Node, ancestors, F_2):
#     for ancestor in ancestors:
#         new_pat_label = (ancestor.item_name, Node.item_name)
#         if new_pat_label in F_2:
#             F_2[new_pat_label].support += Node.count
#         else:
#             F_2[new_pat_label] = Pattern(list(new_pat_label), Node.count)

#     for child in Node.children_list:
#         gen_2patterns_1patterns(child, ancestors + [Node], F_2)


def traverse_with_ancestors(Node, ancestors, F_2, func, freq_pat=None):
    if freq_pat and Node.item_name != 'root':
        freq_pat[(Node.item_name,)].nodeset.add((Node.pre_order, Node.count))
        freq_pat[(Node.item_name,)].support += Node.count

    for ancestor in ancestors:
        func(Node, ancestor, F_2)

    for child in Node.children_list:
        traverse_with_ancestors(
            child, ancestors +
            [Node] if Node.item_name != 'root' else ancestors,
            F_2,
            func,
            freq_pat=freq_pat)


def gen_2patterns_and_1patterns(Node, ancestor, F_2):

    new_pat_label = (ancestor.item_name, Node.item_name)
    if new_pat_label in F_2:
        F_2[new_pat_label].support += Node.count
    else:
        F_2[new_pat_label] = Pattern(list(new_pat_label), Node.count)


def gen_2nodesets(Node, ancestor, F_2):
    new_pat_label = (ancestor.item_name, Node.item_name)
    if new_pat_label in F_2:
        F_2[new_pat_label].nodeset.add((Node.pre_order, Node.count))


class SE_Node:
    def __init__(self, label, itemset):
        self.label = label
        self.itemset = itemset
        self.equiavlent_items = []
        self.childnodes = []


def all_ordered_subsets(prev, items):
    for pos, item in enumerate(items):
        yield prev + [item]
        yield from all_ordered_subsets(prev + [item], items[pos + 1:])


def constructing_pattern_tree(Node, Cad_set, FIS_parent, F, L_1_dict, minimal_support):
    Next_Cad_set = []

    for item in Cad_set:
        Y = [item] + Node.itemset[1:]
        P = Pattern([item] + Node.itemset, 0)
        if tuple(Y) not in F:
            continue

        #P.nodeset = F[tuple(Node.label)].nodeset & F[tuple(Y)].nodeset

        P.nodeset = rec_nodeset_calc(Node.itemset, F) & rec_nodeset_calc(Y, F)
        P.calc_support()

        if P.support >= minimal_support:
            F[tuple(P.itemset)] = P

        if P.support == F[tuple(Node.label)].support:
            Node.equiavlent_items.append(item)
        elif P.support >= minimal_support:
            Node.childnodes.append(SE_Node([item], P.itemset))
            Next_Cad_set.append(item)

    if Node.equiavlent_items:
        sorted_equivalent_items = sorted(
            Node.equiavlent_items, key=lambda item: L_1_dict[item], reverse=True)
        SS = all_ordered_subsets([], sorted_equivalent_items)
        PSet = [A + Node.label for A in SS]

        if not FIS_parent:
            FIT_Node = PSet
        else:
            FIT_Node = []
            for i, j in product(range(len(PSet)), range(len(FIS_parent))):
                FIT_Node.append(PSet[i] + FIS_parent[j])

        for itemset in FIT_Node:
            new_pattern = Pattern(itemset, 0)
            new_pattern.calc_params(F)

            F[tuple(itemset)] = new_pattern

    for child in Node.childnodes:
        constructing_pattern_tree(
            child,
            [item for item in Next_Cad_set if L_1_dict[item]
             > L_1_dict[child.lable[0]]],
            FIT_Node,
            F,
            L_1_dict,
            minimal_support
        )


def _fin(DB, min_support_threshold):
    min_support = min_support_threshold * len(DB)

    poc_tree, L_1_dict = build_POC_tree(DB, min_support)
    # for key, value in F_1_dict.items():
    #     F[key] = Pattern([key], value)

    F = {(key,): Pattern([key], 0) for key in L_1_dict.keys()}

    F_2 = {}
    traverse_with_ancestors(
        poc_tree, [], F_2, gen_2patterns_and_1patterns, freq_pat=F)

    F_2 = {key: value for key, value in F_2.items() if value.support >=
           min_support}

    traverse_with_ancestors(poc_tree, [], F_2, gen_2nodesets)

    F.update(F_2)

    # for key, value in F.items():
    #     print(key, value, value.support, value.nodeset)

    for pattern in F_2.values():
        constructing_pattern_tree(
            SE_Node(pattern.itemset, pattern.itemset),
            [item for item in L_1_dict.keys() if L_1_dict[item] >
             L_1_dict[pattern.itemset[0]]],
            [],
            F,
            L_1_dict,
            min_support
        )

    return F


def FIN(DB, min_support_threshold):
    mined_patterns = _fin(DB, min_support_threshold)

    return list(mined_patterns.values())
