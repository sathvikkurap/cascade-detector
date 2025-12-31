"""Tests for Propagation agent."""

import pytest
from cascade_detector.agents.propagation import PropagationAgent
from cascade_detector.core.graphs import Node, Edge


@pytest.fixture
def propagation_agent():
    """Create a PropagationAgent instance for testing."""
    return PropagationAgent(max_depth=5)


def test_add_secret(propagation_agent):
    """Test adding a secret to the graph."""
    secret_info = {
        "pattern": "aws_key",
        "confidence": 0.95,
        "line": 42,
    }
    
    propagation_agent.add_secret("secret_1", secret_info)
    assert "secret_1" in propagation_agent.graph.graph


def test_add_repository(propagation_agent):
    """Test adding a repository to the graph."""
    repo_info = {
        "url": "https://github.com/example/repo",
        "name": "example-repo",
    }
    
    propagation_agent.add_repository("repo_1", repo_info)
    assert "repo_1" in propagation_agent.graph.graph


def test_add_dependency(propagation_agent):
    """Test adding a dependency relationship."""
    propagation_agent.add_repository("repo_1", {"name": "app"})
    propagation_agent.add_repository("dep_1", {"name": "library"})
    
    propagation_agent.add_dependency("repo_1", "dep_1", {"version": "1.0.0"})
    
    # Check edge was created
    assert propagation_agent.graph.graph.has_edge("repo_1", "dep_1")


def test_add_fork_relationship(propagation_agent):
    """Test adding a fork relationship."""
    propagation_agent.add_repository("parent", {"name": "original"})
    propagation_agent.add_repository("fork", {"name": "fork"})
    
    propagation_agent.add_fork_relationship("fork", "parent", {})
    
    assert propagation_agent.graph.graph.has_edge("parent", "fork")


def test_add_secret_propagation(propagation_agent):
    """Test adding secret propagation relationship."""
    propagation_agent.add_secret("secret_1", {"pattern": "api_key"})
    propagation_agent.add_repository("repo_1", {"name": "app"})
    
    propagation_agent.add_secret_propagation("secret_1", "repo_1", {})
    
    assert propagation_agent.graph.graph.has_edge("secret_1", "repo_1")


def test_map_cascade(propagation_agent):
    """Test cascade mapping."""
    # Build a cascade: secret -> repo1 -> repo2 -> repo3
    propagation_agent.add_secret("secret_1", {"pattern": "api_key"})
    propagation_agent.add_repository("repo_1", {"name": "app"})
    propagation_agent.add_repository("repo_2", {"name": "lib"})
    propagation_agent.add_repository("repo_3", {"name": "service"})
    
    propagation_agent.add_secret_propagation("secret_1", "repo_1", {})
    propagation_agent.add_dependency("repo_1", "repo_2", {})
    propagation_agent.add_dependency("repo_2", "repo_3", {})
    
    cascade = propagation_agent.map_cascade("secret_1")
    
    assert "blast_radius" in cascade
    assert "propagation_paths" in cascade
    assert "affected_repos" in cascade


def test_parse_npm_package_json():
    """Test parsing package.json."""
    agent = PropagationAgent()
    
    content = """{
        "dependencies": {
            "express": "^4.17.1",
            "lodash": "^4.17.21"
        },
        "devDependencies": {
            "jest": "^27.0.0"
        }
    }"""
    
    deps = agent.parse_npm_package_json(content)
    assert "express" in deps
    assert "jest" in deps
    assert len(deps) == 3


def test_parse_requirements_txt():
    """Test parsing requirements.txt."""
    agent = PropagationAgent()
    
    content = """
    requests==2.28.0
    flask>=1.0.0
    django
    # Comment line
    sqlalchemy~=1.4.0
    """
    
    deps = agent.parse_requirements_txt(content)
    assert "requests" in deps
    assert "flask" in deps
    assert "django" in deps
    assert deps["django"] == "*"


def test_export_mermaid(propagation_agent):
    """Test Mermaid diagram export."""
    propagation_agent.add_secret("secret_1", {"pattern": "api_key"})
    propagation_agent.add_repository("repo_1", {"name": "app"})
    propagation_agent.add_secret_propagation("secret_1", "repo_1", {})
    
    mermaid = propagation_agent.export_mermaid()
    
    assert "graph TD" in mermaid
    assert "secret_1" in mermaid
    assert "repo_1" in mermaid


def test_generate_propagation_report(propagation_agent):
    """Test propagation report generation."""
    propagation_agent.add_secret("secret_1", {"pattern": "api_key"})
    propagation_agent.add_repository("repo_1", {"name": "app"})
    propagation_agent.add_secret_propagation("secret_1", "repo_1", {})
    
    report = propagation_agent.generate_propagation_report()
    
    assert "summary" in report
    assert "cascades" in report
    assert "graph" in report
    assert report["summary"]["total_secrets"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
