#!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from copy import deepcopy
from collections import defaultdict

PLACEHOLDER = '_'


def find_frequent_items(pattern, S, min_support):
    placeholder_items = defaultdict(int)
    freq_items = defaultdict(int)

    if pattern.length > 0:
        last_set = pattern.sequence[-1]
    else:
        last_set = []

    
    for seq in S:

        is_prefix = all(item in seq[0] for item in last_set)
        if is_prefix and pattern.length > 0:
            pos = seq[0].index(last_set[-1])
            if pos < len(seq[0]) - 1:
                for item in seq[0][pos + 1:]:
                    placeholder_items[item] += 1 
            
        if seq[0][0] == PLACEHOLDER:
            for item in seq[0][1:]:
                placeholder_items[item] += 1
            seq = seq[1:]

        used = set()
        for itemset in seq:
            for item in itemset:
                if item not in used:
                    freq_items[item] += 1
                    used.add(item)

    result = []
    result += [SequentialPattern([[item]], freq) 
                    for item, freq in freq_items.items() if freq >= min_support]
    result += [SequentialPattern([[PLACEHOLDER, item]], freq) 
                    for item, freq in placeholder_items.items() if freq >= min_support]

    return result           
    #return sorted(result, key = lambda pat: pat.support)


def _prefixspan(pattern, S, min_support_threshold, maxLength=1500):
    min_support = min_support_threshold * len(S)
    patterns = []
    find_frequent_items_list = find_frequent_items(pattern, S, min_support)

    for item in find_frequent_items_list:
        new_pattern = deepcopy(pattern)
        new_pattern.append(item)

        if new_pattern.length <= maxLength and new_pattern.support >= min_support:
            patterns.append(new_pattern)

            if new_pattern.length < maxLength:
                #TODO: возможно когда осталось мало паттернов не всегда стоит вообще пытаться делать проекцию
                projected_DB = project_DB(new_pattern, S)
                new_patterns_list = _prefixspan(new_pattern, projected_DB, min_support, maxLength)
                patterns += new_patterns_list

    return patterns





def project_DB(pattern, S):
    result = []

    last_itemset = pattern.sequence[-1]
    last_item = last_itemset[-1]

    for seq in S:
        for itemset in seq:
            if itemset[0] == PLACEHOLDER:
                if len(last_itemset) > 1 and last_item in itemset:
                    suffix = make_suffix(last_itemset, seq, itemset)
                    if len(suffix) > 0:
                        result.append(suffix)
                    break

            elif all(item in itemset for item in last_itemset):
                suffix = make_suffix(last_itemset, seq, itemset)
                if len(suffix) > 0:
                    result.append(suffix)
                break
    
    return result

def make_suffix(last_itemset, seq, itemset):
    itemset_pos = seq.index(itemset)
    item_pos = itemset.index(last_itemset[-1])

    if item_pos == len(itemset) - 1:
        # mb a deepcopy?
        return seq[itemset_pos + 1:]
    else:
        result = seq[itemset_pos:]
        result[0] = [PLACEHOLDER] + itemset[item_pos + 1:]
        return result


class SequentialPattern:
    def __init__(self, sequence, support):
        self.sequence = deepcopy(sequence)
        self.support = support
        self.length = self._get_length()

    def _get_length(self):
        result = 0
        for s in self.sequence:
            result += len(s)
        return result

    def append(self, pat):
        if pat.sequence[0][0] == PLACEHOLDER:
            self.sequence[-1] += pat.sequence[0][1:]
        else:
            self.sequence += pat.sequence
            if self.support is None:
                self.support = pat.support
        self.support = min(self.support, pat.support)
        self.length += 1  


def PrefixSpan(DB, min_support_threshold):
    return _prefixspan(SequentialPattern([], None), DB, min_support_threshold)