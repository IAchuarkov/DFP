from prefixspan import prefixspan, SequentialPattern


if __name__ == "__main__":

    DB = [
        [['a'], ['a', 'b', 'c'], ['a', 'c'], ['d'], ['c', 'f']],
        [['a', 'd'], ['c'], ['b', 'c'], ['a', 'e']],
        [['e', 'f'], ['a', 'b'], ['d', 'f'], ['c'], ['b']],
        [['e'], ['g'], ['a', 'f'], ['c'], ['b'], ['c']]
    ]

    result = prefixspan(SequentialPattern([], None), DB, minSupport=2, maxLength=10)

    sorted_result = sorted(result, key=lambda record: str(record.sequence))
    print('patterns mined: {}\n'.format(len(sorted_result)))
    for pt in sorted_result:
        print('{}, {}'.format(pt.sequence, pt.support))