"""Propagation agent for mapping secret cascades."""

from typing import List, Dict, Set, Optional
from datetime import datetime, UTC
from cascade_detector.core.graphs import CascadeGraph, Node, Edge


class PropagationAgent:
    """Agent responsible for mapping secret propagation through dependencies and forks."""

    def __init__(self, max_depth: int = 5):
        """Initialize Propagation agent.
        
        Args:
            max_depth: Maximum traversal depth for dependency/fork chains
        """
        self.max_depth = max_depth
        self.graph = CascadeGraph()

    def add_secret(self, secret_id: str, secret_info: Dict) -> None:
        """Add a secret to the propagation graph.
        
        Args:
            secret_id: Unique secret identifier
            secret_info: Dict with secret metadata (pattern, confidence, etc.)
        """
        node = Node(
            id=secret_id,
            name=secret_info.get("name", secret_id),
            node_type="secret",
            metadata=secret_info,
        )
        self.graph.add_node(node)

    def add_repository(self, repo_id: str, repo_info: Dict) -> None:
        """Add a repository node to the graph.
        
        Args:
            repo_id: Repository identifier
            repo_info: Dict with repo metadata (url, name, etc.)
        """
        node = Node(
            id=repo_id,
            name=repo_info.get("name", repo_id),
            node_type="repo",
            metadata=repo_info,
        )
        self.graph.add_node(node)

    def add_dependency(
        self,
        from_repo: str,
        to_dep: str,
        dep_info: Dict,
    ) -> None:
        """Add a dependency relationship.
        
        Args:
            from_repo: Repository that depends on the dependency
            to_dep: Dependency identifier
            dep_info: Dependency metadata (version, type, etc.)
        """
        # Ensure nodes exist
        if from_repo not in self.graph.graph:
            self.add_repository(from_repo, {"name": from_repo})
        if to_dep not in self.graph.graph:
            self.add_repository(to_dep, {"name": to_dep})
        
        edge = Edge(
            source=from_repo,
            target=to_dep,
            edge_type="depends_on",
            metadata=dep_info,
        )
        self.graph.add_edge(edge)

    def add_fork_relationship(
        self,
        fork_repo: str,
        parent_repo: str,
        fork_info: Dict,
    ) -> None:
        """Add a fork relationship.
        
        Args:
            fork_repo: Fork repository identifier
            parent_repo: Parent repository identifier
            fork_info: Fork metadata
        """
        # Ensure nodes exist
        if fork_repo not in self.graph.graph:
            self.add_repository(fork_repo, {"name": fork_repo})
        if parent_repo not in self.graph.graph:
            self.add_repository(parent_repo, {"name": parent_repo})
        
        edge = Edge(
            source=parent_repo,
            target=fork_repo,
            edge_type="forked_from",
            metadata=fork_info,
        )
        self.graph.add_edge(edge)

    def add_secret_propagation(
        self,
        secret_id: str,
        repo_id: str,
        propagation_info: Dict,
    ) -> None:
        """Add a secret propagation relationship.
        
        Args:
            secret_id: Secret identifier
            repo_id: Repository where secret was found/propagated
            propagation_info: Propagation metadata
        """
        # Ensure secret node exists
        if secret_id not in self.graph.graph:
            self.add_secret(secret_id, {"name": secret_id})
        
        # Ensure repo node exists
        if repo_id not in self.graph.graph:
            self.add_repository(repo_id, {"name": repo_id})
        
        edge = Edge(
            source=secret_id,
            target=repo_id,
            edge_type="found_in",
            metadata=propagation_info,
        )
        self.graph.add_edge(edge)

    def map_cascade(
        self,
        secret_id: str,
        include_transitive: bool = True,
    ) -> Dict:
        """Map the cascade for a given secret.
        
        Args:
            secret_id: Secret identifier
            include_transitive: Whether to include transitive dependencies
            
        Returns:
            Cascade mapping dict
        """
        return {
            "secret_id": secret_id,
            "blast_radius": self.graph.get_blast_radius(
                secret_id,
                self.max_depth,
            ),
            "propagation_paths": self.graph.get_cascade_paths(
                secret_id,
                self.max_depth,
            ),
            "affected_repos": list(self.graph.get_affected_repos(
                secret_id,
                self.max_depth,
            )),
        }

    def parse_npm_package_json(self, package_json_content: str) -> Dict[str, str]:
        """Parse package.json to extract dependencies.
        
        Args:
            package_json_content: Content of package.json file
            
        Returns:
            Dict of dependency name -> version
        """
        import json
        try:
            data = json.loads(package_json_content)
            deps = {}
            for dep_type in ["dependencies", "devDependencies", "peerDependencies"]:
                deps.update(data.get(dep_type, {}))
            return deps
        except json.JSONDecodeError:
            return {}

    def parse_requirements_txt(self, requirements_content: str) -> Dict[str, str]:
        """Parse requirements.txt to extract Python dependencies.
        
        Args:
            requirements_content: Content of requirements.txt
            
        Returns:
            Dict of package name -> version
        """
        deps = {}
        for line in requirements_content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Handle various formats: name==version, name>=version, name, etc.
            for op in ['==', '>=', '<=', '~=', '!=']:
                if op in line:
                    name, version = line.split(op, 1)
                    deps[name.strip()] = version.strip()
                    break
            else:
                # No version specifier
                deps[line] = "*"
        
        return deps

    def generate_propagation_report(self) -> Dict:
        """Generate comprehensive propagation report.
        
        Returns:
            Propagation report dict
        """
        # Find all secrets in the graph
        secrets = self.graph.nodes_by_type.get("secret", [])
        
        cascades = []
        total_affected_repos = set()
        
        for secret_id in secrets:
            cascade = self.map_cascade(secret_id)
            cascades.append(cascade)
            total_affected_repos.update(cascade.get("affected_repos", []))
        
        return {
            "summary": {
                "total_secrets": len(secrets),
                "total_repositories": len(self.graph.nodes_by_type.get("repo", [])),
                "total_dependencies": len(self.graph.nodes_by_type.get("dependency", [])),
                "total_forks": len(self.graph.nodes_by_type.get("fork", [])),
                "total_affected_repos": len(total_affected_repos),
            },
            "cascades": cascades,
            "graph": self.graph.to_dict(),
            "generated_at": datetime.now(UTC).isoformat(),
        }

    def export_mermaid(self) -> str:
        """Export graph as Mermaid diagram.
        
        Returns:
            Mermaid diagram syntax
        """
        return self.graph.to_mermaid()

    def get_critical_paths(self) -> List[List[str]]:
        """Get critical propagation paths (longest/deepest cascades).
        
        Returns:
            List of critical paths
        """
        all_paths = []
        secrets = self.graph.nodes_by_type.get("secret", [])
        
        for secret_id in secrets:
            paths = self.graph.get_cascade_paths(secret_id, self.max_depth)
            all_paths.extend(paths)
        
        # Sort by length (deepest first)
        return sorted(all_paths, key=len, reverse=True)
