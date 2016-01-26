import networkx as nx


class CliqueTree:
    """Defines the data structure that will be used to decide if edge addition
    respects graph chordality.
    """
    def __init__(self):
        self.G = nx.Graph()
        self.cliquetree = nx.Graph()
        self.node_in_cliques = {}  # cliques in which the node participates in
        self.nodes_in_clique = {}  # the set of nodes in each clique
        self.node_in_separators = {}
        self.nodes_in_separator = {}
        self.uid = 1
        self.insertable = set()

    def _clique_is_maximal(self, nodes):
        """Returns True if the list of given nodes form a maximal clique
        """
        nodeset = set(nodes)
        if not nodeset and len(self.G) > 0:
            # empty clique is not maximal, unless graph is empty
            return False
        checked_neighbors = set()
        for x in nodes:
            neighbors_x = set(self.G[x])
            # check if nodeset is clique for x
            if len(nodeset - neighbors_x) > 1:
                return False
            for neighbor in neighbors_x:
                if neighbor in checked_neighbors or neighbor in nodeset:
                    continue
                two_hop_neighbors = set(self.G[neighbor])
                if len(two_hop_neighbors.intersection(nodeset)) == len(nodeset):
                    return False
                else:
                    checked_neighbors.add(neighbor)
        return True

    def _add_clique_node(self, uid, nodes):
        """Adds a new node in the cliquetree that represents a given node set.
        """
        self.cliquetree.add_node(uid)
        if uid not in self.nodes_in_clique:
            self.nodes_in_clique[uid] = set()
        for node in nodes:
            self.nodes_in_clique[uid].add(node)
            if node not in self.node_in_cliques:
                self.node_in_cliques[node] = set()
            self.node_in_cliques[node].add(uid)

    def add_edge(self, x, y):
        """Adds an edge to the clique tree and updates the data structures.
        """
        # Start by checking if the edge can be inserted
        # if not self.query_edge(e):
        #   return False
        if self._edge(x, y) in self.G.edges():
            return
        if x in self.G:
            neighbors_x = set(self.G[x])
        else:
            neighbors_x = set()
            self.G.add_node(x)
        if y in self.G:
            neighbors_y = set(self.G[y])
        else:
            neighbors_y = set()
            self.G.add_node(y)

        K1 = None
        if x in self.node_in_cliques:
            for clq in self.node_in_cliques[x]:
                K1 = clq
                break
        K2 = None
        if y in self.node_in_cliques:
            for clq in self.node_in_cliques[y]:
                K2 = clq
                break

        changed_edges = []

        if (K1 and not K2) or (not K1 and K2):
            self._add_clique_node(self.uid, neighbors_x.intersection(neighbors_y).union(set([x, y])))
            if K1 and not K2:
                sep = self.nodes_in_clique[K1]\
                          .intersection(self.nodes_in_clique[self.uid])
                self.cliquetree.add_edge(K1, self.uid, nodes=sep)
                changed_edges.append((K1, self.uid))
            elif not K1 and K2:
                sep = self.nodes_in_clique[K2]\
                          .intersection(self.nodes_in_clique[self.uid])
                self.cliquetree.add_edge(K2, self.uid, nodes=sep)
                changed_edges.append((K2, self.uid))
        elif K1 and K2:
            Kx = None
            Ky = None
            # figure out Kx and Ky
            path = nx.shortest_path(self.cliquetree, source=K1, target=K2)
            min_edge_weight = 1e100
            min_edge = None
            first_node = True
            found_Kx = False
            for clq1, clq2 in zip(path[:-1], path[1:]):
                if first_node:
                    if x in self.nodes_in_clique[clq1]:
                        Kx = clq1
                    first_node = False
                if not Ky:
                    if y in self.nodes_in_clique[clq2]:
                        Ky = clq2
                    if x in self.nodes_in_clique[clq2]:
                        Kx = clq2
                    else:
                        # first time to not find x in clq2, Kx = clq1
                        found_Kx = True
                if found_Kx:
                    sep = self.cliquetree[clq1][clq2]['nodes']
                    if len(sep) < min_edge_weight:
                        min_edge_weight = len(sep)
                        min_edge = (clq1, clq2)
            Kx_nodes = self.nodes_in_clique[Kx]
            Ky_nodes = self.nodes_in_clique[Ky]
            I = Kx_nodes.intersection(Ky_nodes)
            if Ky not in self.cliquetree[Kx] and min_edge_weight > len(I):
                return False
            elif Ky not in self.cliquetree[Kx] and min_edge_weight == len(I):
                # replace min_edge with (Kx, Ky)
                self.cliquetree.remove_edge(*min_edge)
                c1, c2 = self._edge(Kx, Ky)
                self.cliquetree.add_edge(c1, c2, nodes=I)

            # Step 2
            # Add the cliquetree node now, because we might have aborted above
            self._add_clique_node(self.uid,
                                  I.union(set([x, y])))
            edge_to_remove = self._edge(Kx, Ky)
            self.cliquetree.remove_edge(*edge_to_remove)

            to_remove = []
            to_keep = []
            for clq in [Kx, Ky]:
                clq_nodes = self.nodes_in_clique[clq]
                if len(clq_nodes) > len(I) + 1:
                    to_keep.append(clq)
                else:
                    to_remove.append(clq)

            for clq in to_remove:
                # clq is not maximal in the new graph
                for v in self.cliquetree[clq]:
                    if v == self.uid or v in [Kx, Ky]:
                        continue
                    sep = self.nodes_in_clique[v]\
                              .intersection(self.nodes_in_clique[self.uid])
                    self.cliquetree.add_edge(v, self.uid, nodes=sep)
                    c1, c2 = self._edge(v, clq)
                self.cliquetree.remove_node(clq)
                del self.nodes_in_clique[clq]
                for v in self.node_in_cliques:
                    if clq in self.node_in_cliques[v]:
                        self.node_in_cliques[v].remove(clq)
            for clq in to_keep:
                sep = self.nodes_in_clique[clq]\
                          .intersection(self.nodes_in_clique[self.uid])
                self.cliquetree.add_edge(clq, self.uid, nodes=sep)
                changed_edges.append((clq, self.uid))
        else:
            # not K1 and not K2
            self._add_clique_node(self.uid,
                                  neighbors_x.intersection(neighbors_y)
                                      .union(set([x, y])))

        # Update the actual graph
        self.G.add_edge(x, y)
        # if (x, y) in self.insertable:
        #     self.insertable.remove((x, y))

        self.uid += 1
        self.insertable = set()
        for v in self.G:
            self.update_insertable(v)
        return True

    def update_insertable(self, v):
        K1 = 0
        Kx = None
        nodes_seen = []
        min_weights = []
        v_cliques = self.node_in_cliques[v]
        for clq in self.node_in_cliques[v]:
            K1 = clq
            break
        for clq1, clq2, data in \
                nx.dfs_labeled_edges(self.cliquetree, source=K1):
            if data['dir'] is 'nontree' or (clq1 == K1 and clq2 == K1):
                continue
            clq_min, clq_max = self._edge(clq1, clq2)
            sep = self.cliquetree[clq_min][clq_max]['nodes']
            if data['dir'] is 'forward':
                if clq1 in v_cliques and clq2 not in v_cliques:
                    Kx = clq1
                    Kx_nodes = self.nodes_in_clique[clq1]
                if Kx:
                    w_e = len(sep)
                    if not min_weights or w_e <= min_weights[-1]:
                        # w(e) = w(x, y)
                        min_weights.append(w_e)
                        # is it a possible Ky?
                        Ky_nodes = self.nodes_in_clique[clq2]
                        if min_weights[-1] == len(Kx_nodes.intersection(Ky_nodes)):
                            for u in self.nodes_in_clique[clq2]:
                                if (not nodes_seen or u not in nodes_seen[-1]) \
                                        and u not in self.G[v]:
                                    # Ky for u
                                    self.insertable.add(self._edge(u, v))
                    else:
                        min_weights.append(min_weights[-1])
                    if nodes_seen:
                        seen_previous = nodes_seen[-1]
                    else:
                        seen_previous = set()
                    nodes_seen.append(self.nodes_in_clique[clq2]
                                          .union(seen_previous))
            elif data['dir'] is 'reverse':
                first_Kx = False
                if clq1 in v_cliques and clq2 not in v_cliques:
                    Kx = None
                    Kx_nodes = None
                    first_Kx = True
                if Kx is not None or first_Kx:
                    min_weights.pop()
                    nodes_seen.pop()

    def query_edge(self, x, y):
        e = self._edge(x, y)
        if not self.insertable or e in self.insertable:
            return True
        return False

    def _edge(self, x, y):
        return (min(x, y), max(x, y))

    def clique_tostr(self, v):
        return ', '.join(map(str, list(self.nodes_in_clique[v])))
