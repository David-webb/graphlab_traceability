import datetime
STARTIME = datetime.datetime.now()
TIMERATE = 3600
EDGES_FILENAME = 'tmp_edges.csv'
VERTICES_FILENAME = 'tmp_vertices.csv'

GRAPHMODEL = (
    ['p','p0',20, 1, 8, {}],
    ['p','p1',20, 1, 4, {}],
    ['p','p2',20, 1, 4, {'p0': 2, 'p1': 1}],
    ['p','p3',20, 1, 16, {}],
    ['p','p4',20, 0.5, 4, {'p2': 1, 'p3': 4}],
    ['p','p5',20, 1, 12, {}],
    ['p','p6',20, 1, 4, {}],
    ['p','p7',20, 0.5, 4, {'p5': 3, 'p6': 1}],
    ['p','p8',20, 1, 2, {'p4': 2, 'p7': 2}],
    ['t','t0',0, 2],
    ['t','t1',1, 2],
    ['t','t2',2, 4],
    ['t','t3',3, 4],
    ['t','t4',4, 8],
    ['t','t5',5, 7],
    ['t','t6',6, 7],
    ['t','t7',7, 8],
)