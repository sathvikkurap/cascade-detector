"""Graph utilities for dependency and fork networks."""

import networkx as nx
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Node:
    """Represents a node in the cascade graph."""
    
    id: str
    name: str
    node_type: str  # "repo", "dependency", "fork", "secret"
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Edge:
    """Represents an edge in the cascade graph."""
    
    source: str
    target: str
    edge_type: str  # "depends_on", "forked_from", "propagated_to", "found_in"
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class CascadeGraph:
    """Builds and traverses secret cascade graphs using NetworkX."""

    def __init__(self):
        """Initialize the cascade graph."""
        self.graph = nx.DiGraph()
        self.nodes_by_type: Dict[str, List[str]] = {}
        self.secrets: Set[str] = set()

    def add_node(self, node: Node) -> None:
        """Add a node to the graph.
        
        Args:
            node: Node to add
        """
        self.graph.add_node(
            node.id,
            name=node.name,
            type=node.node_type,
            metadata=node.metadata,
        )
        if node.node_type not in self.nodes_by_type:
            self.nodes_by_type[node.node_type] = []
        self.nodes_by_type[node.node_type].append(node.id)

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph.
        
        Args:
            edge: Edge to add
        """
        # Ensure nodes exist
        if edge.source not in self.graph:
            self.add_node(Node(edge.source, edge.source, "unknown"))
        if edge.target not in self.graph:
            self.add_node(Node(edge.target, edge.target, "unknown"))

        self.graph.add_edge(
            edge.source,
            edge.target,
            type=edge.edge_type,
            metadata=edge.metadata,
        )

    def get_cascade_paths(
        self, secret_id: str, max_depth: int = 5
    ) -> List[List[str]]:
        """Get all propagation paths from a secret.
        
        Args:
            secret_id: ID of the secret node
            max_depth: Maximum traversal depth
            
        Returns:
            List of paths from secret to affected nodes
        """
        if secret_id not in self.graph:
            return []

        paths = []
        visited = set()

        def dfs(current: str, path: List[str], depth: int):
            if depth > max_depth or current in visited:
                return
            
            visited.add(current)
            path.append(current)

            # Get successors
            successors = list(self.graph.successors(current))
            if not successors:
                paths.append(path.copy())
            else:
                for successor in successors:
                    if successor not in visited:
                        dfs(successor, path.copy(), depth + 1)

        dfs(secret_id, [], 0)
        return paths

    def get_affected_repos(self, secret_id: str, max_depth: int = 5) -> Set[str]:
        """Get all repositories affected by a secret.
        
        Args:
            secret_id: ID of the secret
            max_depth: Maximum traversal depth
            
        Returns:
            Set of affected repo IDs
        """
        affected = set()
        paths = self.get_cascade_paths(secret_id, max_depth)
        
        for path in paths:
            for node_id in path:
                node_type = self.graph.nodes[node_id].get("type")
                if node_type == "repo":
                    affected.add(node_id)
        
        return affected

    def get_blast_radius(self, secret_id: str, max_depth: int = 5) -> Dict:
        """Calculate blast radius of a secret.
        
        Args:
            secret_id: ID of the secret
            max_depth: Maximum traversal depth
            
        Returns:
            Dict with blast radius metrics
        """
        paths = self.get_cascade_paths(secret_id, max_depth)
        affected_repos = self.get_affected_repos(secret_id, max_depth)

        return {
            "secret_id": secret_id,
            "num_propagation_paths": len(paths),
            "affected_repos": len(affected_repos),
            "affected_repo_ids": list(affected_repos),
            "max_depth_reached": max(len(p) for p in paths) if paths else 0,
            "paths": paths,
        }

    def get_dependency_tree(self, repo_id: str, max_depth: int = 5) -> Dict:
        """Get dependency tree for a repository.
        
        Args:
            repo_id: Repository ID
            max_depth: Maximum traversal depth
            
        Returns:
            Dependency tree structure
        """
        tree = {
            "repo": repo_id,
            "dependencies": [],
            "transitive_deps": [],
        }

        visited = set()

        def traverse(node_id: str, depth: int, is_transitive: bool = False):
            if depth > max_depth or node_id in visited:
                return
            
            visited.add(node_id)
            
            # Get direct dependencies
            for successor in self.graph.successors(node_id):
                edge_data = self.graph.edges[node_id, successor]
                if edge_data.get("type") == "depends_on":
                    dep_info = {
                        "id": successor,
                        "name": self.graph.nodes[successor].get("name", successor),
                        "transitive": is_transitive,
                    }
                    
                    if is_transitive:
                        tree["transitive_deps"].append(dep_info)
                    else:
                        tree["dependencies"].append(dep_info)
                    
                    # Traverse transitive deps
                    traverse(successor, depth + 1, is_transitive=True)

        traverse(repo_id, 0, False)
        return tree

    def get_subgraph(self, nodes: Set[str]) -> 'CascadeGraph':
        """Extract a subgraph for given nodes.
        
        Args:
            nodes: Set of node IDs to include
            
        Returns:
            New CascadeGraph containing subgraph
        """
        subgraph = CascadeGraph()
        sub_nx = self.graph.subgraph(nodes)
        
        for node_id in nodes:
            if node_id in self.graph:
                node_data = self.graph.nodes[node_id]
                node = Node(
                    node_id,
                    node_data.get("name", node_id),
                    node_data.get("type", "unknown"),
                    node_data.get("metadata", {}),
                )
                subgraph.add_node(node)
        
        for source, target in sub_nx.edges():
            edge_data = self.graph.edges[source, target]
            edge = Edge(
                source,
                target,
                edge_data.get("type", "unknown"),
                edge_data.get("metadata", {}),
            )
            subgraph.add_edge(edge)
        
        return subgraph

    def to_mermaid(self) -> str:
        """Export graph as Mermaid diagram.
        
        Returns:
            Mermaid diagram syntax
        """
        lines = ["graph TD"]
        
        # Add nodes with labels
        for node_id, node_data in self.graph.nodes(data=True):
            node_type = node_data.get("type", "unknown")
            name = node_data.get("name", node_id)
            
            # Color by type
            color_map = {
                "secret": "#FF6B6B",
                "repo": "#4ECDC4",
                "dependency": "#95E1D3",
                "fork": "#FFD93D",
                "unknown": "#CCCCCC",
            }
            color = color_map.get(node_type, "#CCCCCC")
            
            lines.append(f'    {node_id}["{name}<br/>{node_type}"]')
            lines.append(f'    style {node_id} fill:{color}')
        
        # Add edges
        for source, target, edge_data in self.graph.edges(data=True):
            edge_type = edge_data.get("type", "unknown")
            lines.append(f'    {source} -->|{edge_type}| {target}')
        
        return "\n".join(lines)

    def to_dict(self) -> Dict:
        """Export graph as dictionary.
        
        Returns:
            Dictionary representation of graph
        """
        return {
            "nodes": [
                {
                    "id": node_id,
                    "name": node_data.get("name"),
                    "type": node_data.get("type"),
                    "metadata": node_data.get("metadata", {}),
                }
                for node_id, node_data in self.graph.nodes(data=True)
            ],
            "edges": [
                {
                    "source": source,
                    "target": target,
                    "type": edge_data.get("type"),
                    "metadata": edge_data.get("metadata", {}),
                }
                for source, target, edge_data in self.graph.edges(data=True)
            ],
        }
