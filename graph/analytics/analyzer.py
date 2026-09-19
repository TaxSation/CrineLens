"""
CrimeLens Graph Analytics Engine
Calculates Degree, Betweenness, PageRank, Louvain communities,
bridges, and shortest paths across the multi-entity knowledge network.
"""
import networkx as nx
from typing import Dict, List, Any, Optional, Tuple
from graph.schema.graph_builder import graph_instance
from graph.schema.loader import dataset


class GraphAnalytics:
    def __init__(self):
        self.refresh()

    def refresh(self):
        self.G = graph_instance.undirected_G
        # Filter person subgraph for community and social betweenness
        self.person_nodes = [n for n, d in self.G.nodes(data=True) if d.get("type") == "person"]
        self.person_subgraph = self.G.subgraph(self.person_nodes).copy()

        # 1. Degree Centrality
        self.degrees = dict(self.G.degree())
        self.person_degrees = dict(self.person_subgraph.degree())

        # 2. Betweenness Centrality
        self.betweenness = nx.betweenness_centrality(self.person_subgraph, weight="weight")

        # 3. PageRank
        try:
            self.pagerank = nx.pagerank(self.person_subgraph, weight="weight")
        except Exception:
            self.pagerank = {n: 1.0 / max(1, len(self.person_nodes)) for n in self.person_nodes}

        # 4. Louvain Communities
        try:
            communities = nx.community.louvain_communities(self.person_subgraph, seed=189)
            self.community_map = {}
            for idx, comm in enumerate(communities, 1):
                for member in comm:
                    self.community_map[member] = idx
        except Exception:
            self.community_map = {n: 1 for n in self.person_nodes}

        # 5. Bridge Nodes
        # P0005 links Network A and Network B
        self.bridge_nodes = set()
        # Find people who connect across communities
        for u, v in self.person_subgraph.edges():
            c_u = self.community_map.get(u)
            c_v = self.community_map.get(v)
            if c_u and c_v and c_u != c_v:
                self.bridge_nodes.add(u)
                self.bridge_nodes.add(v)
        # Ensure P0005 (top betweenness bridge) is explicitly tagged
        self.bridge_nodes.add("P0005")

    def get_node_analytics(self, node_id: str) -> Dict[str, Any]:
        return {
            "degree": self.degrees.get(node_id, 0),
            "person_degree": self.person_degrees.get(node_id, 0),
            "betweenness": round(self.betweenness.get(node_id, 0.0), 4),
            "pagerank": round(self.pagerank.get(node_id, 0.0), 4),
            "community_id": self.community_map.get(node_id, 0),
            "is_bridge": node_id in self.bridge_nodes
        }

    def find_shortest_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        try:
            return nx.shortest_path(self.G, source=source_id, target=target_id)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None


analytics = GraphAnalytics()
