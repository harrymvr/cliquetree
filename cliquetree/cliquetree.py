from copy import deepcopy
import networkx as nx
from networkx import NetworkXNoPath


class CliqueTree:
    """Defines the data structure that will be used to decide if edge addition
    respects graph chordality.
    """
    def __init__(self):
        self.G = nx.Graph()
        self.cliquetree = nx.Graph()
        self.node_in_cliques = {}  # cliques in which the node participates in
        self.nodes_in_clique = {}  # the set of nodes in each clique
        self.uid = 1
        self.insertable = set()
        self.deletable = set()

    def __deepcopy__(self, memo):
        obj = CliqueTree()
        obj.G = deepcopy(self.G, memo)
        obj.cliquetree = deepcopy(self.cliquetree, memo)
        obj.node_in_cliques = deepcopy(self.node_in_cliques, memo)
        obj.nodes_in_clique = deepcopy(self.nodes_in_clique, memo)
        obj.uid = self.uid
        obj.insertable = deepcopy(self.insertable, memo)
        obj.deletable = deepcopy(self.deletable, memo)
        return obj

    def copy(self):
        return deepcopy(self)

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

    def add_edge(self, x, y, update_insertable=True):
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
            try:
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
                    if found_Kx and Ky:
                        break
            except NetworkXNoPath:
                # The two nodes belong to disconnected components, so it
                # is safe to add the edge.
                # sep = self.nodes_in_clique[K1]\
                          # .intersection(self.nodes_in_clique[K2])
                # self.cliquetree.add_edge(K1, K2, nodes=sep)
                # changed_edges.append((K1, K2))
                Kx = K1
                Ky = K2
                min_edge_weight = 0
            Kx_nodes = self.nodes_in_clique[Kx]
            Ky_nodes = self.nodes_in_clique[Ky]
            I = Kx_nodes.intersection(Ky_nodes)
            if Ky not in self.cliquetree[Kx]:
                if min_edge_weight > len(I):
                    return False

            if Ky in self.cliquetree[Kx] or (min_edge_weight == len(I) and
                    Ky not in self.cliquetree[Kx] and min_edge_weight > 0):
                # replace min_edge with (Kx, Ky)
                self.cliquetree.remove_edge(*min_edge)
                c1, c2 = self._edge(Kx, Ky)
                self.cliquetree.add_edge(c1, c2, nodes=I)

            # Step 2
            # Add the cliquetree node now, because we might have aborted above
            self._add_clique_node(self.uid,
                                  I.union(set([x, y])))
            edge_to_remove = self._edge(Kx, Ky)
            if Ky in self.cliquetree[Kx]:
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
        if update_insertable:
            self.insertable = set()
            for v in self.G:
                self.update_insertable(v)
        return True

    def update_insertable(self, v):
        K1 = 0
        Kx = None
        cliques_visited = set()
        nodes_seen = []
        min_weights = []
        v_cliques = self.node_in_cliques[v]
        for clq in self.node_in_cliques[v]:
            K1 = clq
            break
        cliques_visited.add(K1)
        for clq1, clq2, data in \
                nx.dfs_labeled_edges(self.cliquetree, source=K1):
            if data['dir'] is 'nontree' or (clq1 == K1 and clq2 == K1):
                continue
            clq_min, clq_max = self._edge(clq1, clq2)
            sep = self.cliquetree[clq_min][clq_max]['nodes']
            if data['dir'] is 'forward':
                cliques_visited.add(clq2)
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
                                        and u not in self.G[v] and u != v:
                                    # Ky for u
                                    self.insertable.add(self._edge(u, v))
                                    if u == v:
                                        raise ValueError('u is equal to v')
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
        for clq in self.cliquetree:
            # if clique is in another component, edge is insertable
            if clq not in cliques_visited:
                for u in self.nodes_in_clique[clq]:
                    self.insertable.add(self._edge(u, v))

    def update_deletable(self):
        self.deletable = set()
        for u_index, u in enumerate(self.G):
            for v_index, v in enumerate(self.G):
                if u_index >= v_index:
                    continue
                if self._edge(u, v) in self.deletable:
                    continue
                clq_u = self.node_in_cliques[u]
                clq_v = self.node_in_cliques[v]
                if len(clq_u.intersection(clq_v)) == 1:
                    self.deletable.add(self._edge(u, v))

    def from_graph(self, G):
        self.G = G.copy()
        cliques = nx.clique.find_cliques(G)
        cliquegraph = nx.clique.make_max_clique_graph(G)
        clique_dict = {}
        for v, clq in zip(cliquegraph.nodes(), cliques):
            clique_dict[v] = clq

        for u, v, data in cliquegraph.edges(data=True):
            cliquegraph.remove_edge(u, v)
            sep = set(clique_dict[u]).intersection(set(clique_dict[v]))
            w = len(sep)
            cliquegraph.add_edge(u, v, nodes=sep, weight=-w)
        self.cliquetree = nx.minimum_spanning_tree(cliquegraph)

        for v in self.G:
            self.node_in_cliques[v] = set()
        for v in clique_dict:
            self.nodes_in_clique[v] = set()
            for node in clique_dict[v]:
                self.nodes_in_clique[v].add(node)
                self.node_in_cliques[node].add(v)
        self.uid = len(G) + 1
        self.insertable = set()
        for v in self.G:
            self.update_insertable(v)

    def remove_edge(self, u, v):
        Kx = self.node_in_cliques[u].intersection(self.node_in_cliques[v])
        if len(Kx) == 0:
            raise ValueError('Edge (%s, %s) was not found in the graph.' %
                             (u, v))
        if len(Kx) > 1:
            raise ValueError('Edge (%s, %s) belongs to more than one cliques' %
                             (u, v))

        (Kx, ) = Kx  # get single element from the intersection
        Kux_nodes = set(self.nodes_in_clique[Kx])
        Kux_nodes.remove(v)
        Kvx_nodes = set(self.nodes_in_clique[Kx])
        Kvx_nodes.remove(u)
        Nu = []
        Nv = []
        Nuv = []
        Kux = None
        Kvx = None
        for clq in self.cliquetree[Kx]:
            found_u = False
            found_v = False
            clq_nodes = self.nodes_in_clique[clq]
            if u in clq_nodes:
                found_u = True
                Nu.append(clq)
                # if Kux is subset of clq, replace Kux with clq
                if Kux_nodes.issubset(clq_nodes):
                    Kux = clq
            elif v in clq_nodes:
                found_v = True
                Nv.append(clq)
                # if Kvx is subset of clq, replace Kux with clq
                if Kvx_nodes.issubset(clq_nodes):
                    Kvx = clq
            if not found_u and not found_v:
                Nuv.append(clq)
        # Add to Kux all the nodes in Nu and the Nuv
        Nu.extend(Nuv)
        if Kux is None:
            # there is at least one neighbor of Kux and
            # Kux has not been replaces by any of its neighbors
            self._add_clique_node(self.uid, Kux_nodes)
            Kux = self.uid
            self.uid += 1
        if Kvx is None:
            self._add_clique_node(self.uid, Kvx_nodes)
            Kvx = self.uid
            self.uid += 1
        for clq in Nu:
            if clq == Kux:
                continue
            clq_min, clq_max = self._edge(clq, Kx)
            sep = self.cliquetree[clq_min][clq_max]['nodes']
            self.cliquetree.add_edge(clq, Kux, nodes=sep)
        for clq in Nv:
            if clq == Kvx:
                continue
            clq_min, clq_max = self._edge(clq, Kx)
            sep = self.cliquetree[clq_min][clq_max]['nodes']
            self.cliquetree.add_edge(clq, Kvx, nodes=sep)

        # Add an edge between Kux and Kvx
        if Kux is not None and Kvx is not None:
            sep = self.nodes_in_clique[Kux]\
                      .intersection(self.nodes_in_clique[Kvx])
            if len(sep) > 0:
                # the edge deletion will not disconnect the tree
                clq_min, clq_max = self._edge(Kux, Kvx)
                self.cliquetree.add_edge(clq_min, clq_max, nodes=sep)

        # Delete Kx
        self.cliquetree.remove_node(Kx)
        del self.nodes_in_clique[Kx]
        for t in self.node_in_cliques:
            if Kx in self.node_in_cliques[t]:
                self.node_in_cliques[t].remove(Kx)
        self.G.remove_edge(u, v)
        self.insertable = set()
        for t in self.G:
            self.update_insertable(t)

    def query_edge(self, x, y):
        e = self._edge(x, y)
        if not self.insertable or e in self.insertable:
            return True
        return False

    def _edge(self, x, y):
        return (min(x, y), max(x, y))

    def clique_tostr(self, v):
        return ', '.join(map(str, list(self.nodes_in_clique[v])))
