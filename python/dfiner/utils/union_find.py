class UnionFind:
    """Weighted quick-union with path compression.
    The original Java implementation is introduced at
    https://www.cs.princeton.edu/~rs/AlgsDS07/01UnionFind.pdf
    >>> uf = UnionFind(10)
    >>> for (p, q) in [(3, 4), (4, 9), (8, 0), (2, 3), (5, 6), (5, 9),
    ...                (7, 3), (4, 8), (6, 1)]:
    ...     uf.union(p, q)
    >>> uf._id
    [8, 3, 3, 3, 3, 3, 3, 3, 3, 3]
    >>> uf.find(0, 1)
    True
    >>> uf._id
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
    """

    def __init__(self, n):
        self._id = list(range(n))
        self._sz = [1] * n

    def _root(self, i):
        j = i
        while (j != self._id[j]):
            self._id[j] = self._id[self._id[j]]
            j = self._id[j]
        return j

    def find(self, p, q):
        return self._root(p) == self._root(q)

    def union(self, p, q):
        i = self._root(p)
        j = self._root(q)
        if i == j:
            return
        if (self._sz[i] < self._sz[j]):
            self._id[i] = j
            self._sz[j] += self._sz[i]
        else:
            self._id[j] = i
            self._sz[i] += self._sz[j]


class UnionComponents(object):
    @staticmethod
    def get_membership(i, clusters):
        for c_id in xrange(len(clusters)):
            if i in clusters[c_id]:
                return c_id
        return None

    @staticmethod
    def union(i, j, clusters):
        m_i = UnionComponents.get_membership(i, clusters)
        m_j = UnionComponents.get_membership(j, clusters)
        if m_i is None and m_j is None:
            s = set()
            s.add(i)
            s.add(j)
            clusters.append(s)
        elif m_i is None:
            clusters[m_j].add(i)
        elif m_j is None:
            clusters[m_i].add(j)
        else:
            # m_i will not be m_j but still
            assert m_i != m_j
            # we need to merge clusters at m_i and m_j
            # first sort
            m_i, m_j = (m_i, m_j) if m_i < m_j else (m_j, m_i)
            s = clusters.pop(m_j).union(clusters.pop(m_i))
            clusters.append(s)

    @staticmethod
    def get_component(i, clusters):
        for cluster in clusters:
            if i in cluster:
                return cluster
        return {i}