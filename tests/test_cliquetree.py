from __future__ import division

from cliquetree import CliqueTree


def test_insertable1():
    c = CliqueTree()
    edges = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (3, 5), (6, 4),
             (1, 3), (1, 5), (1, 4), (5, 7), (2, 5), (1, 6), (2, 4), (1, 7),
             (4, 7), (2, 7), (3, 7), (2, 6), (3, 6)]
    solutions = [frozenset([]), frozenset([(1, 3)]), frozenset([(1, 3), (2, 4)]),
                 frozenset([(1, 3), (2, 4), (3, 5)]),
                 frozenset([(4, 6), (1, 3), (2, 4), (3, 5)]),
                 frozenset([(4, 6), (5, 7), (1, 3), (2, 4), (3, 5)]),
                 frozenset([(1, 3), (4, 6), (5, 7), (3, 6), (2, 5), (2, 4)]),
                 frozenset([(4, 7), (1, 3), (5, 7), (3, 6), (2, 5), (2, 4)]),
                 frozenset([(4, 7), (5, 7), (1, 4), (1, 5), (3, 6), (2, 5), (2, 4)]),
                 frozenset([(2, 5), (5, 7), (3, 6), (1, 4), (4, 7)]),
                 frozenset([(4, 7), (5, 7), (1, 6), (3, 6), (2, 5), (2, 4)]),
                 frozenset([(2, 5), (1, 6), (2, 4), (3, 6), (4, 7)]),
                 frozenset([(4, 7), (1, 6), (2, 4), (3, 6)]),
                 frozenset([(4, 7), (2, 4), (3, 6), (1, 7)]),
                 frozenset([(4, 7), (2, 6), (3, 6), (1, 7)]),
                 frozenset([(4, 7), (2, 6), (3, 6)]),
                 frozenset([(2, 7), (3, 7), (2, 6), (3, 6)]),
                 frozenset([(3, 7), (2, 6)]),
                 frozenset([(2, 6), (3, 6)]),
                 frozenset([(3, 6)]),
                 frozenset([])]

    for edge, insertable in zip(edges, solutions):
        c.add_edge(*edge)
        assert c.insertable == insertable


def test_update():
    c = CliqueTree()
    edges = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (3, 5), (6, 4),
             (1, 3), (1, 5), (1, 4), (5, 7), (2, 5), (1, 6), (2, 4), (1, 7),
             (4, 7), (2, 7), (3, 7), (2, 6), (3, 6)]
    solutions = [frozenset([]), frozenset([(1, 3)]), frozenset([(1, 3), (2, 4)]),
                 frozenset([(1, 3), (2, 4), (3, 5)]),
                 frozenset([(4, 6), (1, 3), (2, 4), (3, 5)]),
                 frozenset([(4, 6), (5, 7), (1, 3), (2, 4), (3, 5)]),
                 frozenset([(1, 3), (4, 6), (5, 7), (3, 6), (2, 5), (2, 4)]),
                 frozenset([(4, 7), (1, 3), (5, 7), (3, 6), (2, 5), (2, 4)]),
                 frozenset([(4, 7), (5, 7), (1, 4), (1, 5), (3, 6), (2, 5), (2, 4)]),
                 frozenset([(2, 5), (5, 7), (3, 6), (1, 4), (4, 7)]),
                 frozenset([(4, 7), (5, 7), (1, 6), (3, 6), (2, 5), (2, 4)]),
                 frozenset([(2, 5), (1, 6), (2, 4), (3, 6), (4, 7)]),
                 frozenset([(4, 7), (1, 6), (2, 4), (3, 6)]),
                 frozenset([(4, 7), (2, 4), (3, 6), (1, 7)]),
                 frozenset([(4, 7), (2, 6), (3, 6), (1, 7)]),
                 frozenset([(4, 7), (2, 6), (3, 6)]),
                 frozenset([(2, 7), (3, 7), (2, 6), (3, 6)]),
                 frozenset([(3, 7), (2, 6)]),
                 frozenset([(2, 6), (3, 6)]),
                 frozenset([(3, 6)]),
                 frozenset([])]

    for edge, insertable in zip(edges[:10], solutions[:10]):
        c.add_edge(*edge)
    c.add_edge(*edges[10], update_insertable=False)
    assert len(c.insertable) == 0
    c.update_insertable(7, stop_at=1)
    assert len(c.insertable) == 1
    assert len(c.insertable.intersection(solutions[10])) == 1
