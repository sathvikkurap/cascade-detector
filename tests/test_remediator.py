"""Tests for Remediator agent."""

import pytest
from cascade_detector.agents.remediator import RemediatorAgent, RemediationPatch


@pytest.fixture
def remediator_agent():
    """Create a RemediatorAgent instance for testing."""
    return RemediatorAgent(test_patch=False)


def test_remediation_patch_creation(remediator_agent):
    """Test creating a remediation patch."""
    original = """
    API_KEY = "sk_live_secret123"
    """
    
    patched = """
    API_KEY = os.getenv("API_KEY")
    """
    
    patch = RemediationPatch(
        file_path="config.py",
        original_content=original,
        patched_content=patched,
        secret_type="api_key",
        pattern="sk_live_secret123",
    )
    
    assert patch.file_path == "config.py"
    assert "sk_live_secret123" in patch.original_content
    assert "os.getenv" in patch.patched_content


def test_generate_patch(remediator_agent):
    """Test patch generation."""
    content = """
    API_KEY = "sk_live_secret123"
    print("Hello")
    """
    
    secret_match = {
        "pattern": "api_key",
        "matched_text": "sk_live_secret123",
        "line": 2,
    }
    
    patch = remediator_agent.generate_patch(content, "test.py", secret_match)
    
    assert patch is not None
    assert patch.file_path == "test.py"


def test_get_env_var_name():
    """Test environment variable name generation."""
    agent = RemediatorAgent()
    
    test_cases = [
        ("aws_access_key", "AWS_ACCESS_KEY_ID"),
        ("github_token", "GITHUB_TOKEN"),
        ("api_key", "API_KEY"),
    ]
    
    for secret_type, expected_name in test_cases:
        name = agent._get_env_var_name(secret_type)
        assert name == expected_name


def test_generate_pr_description(remediator_agent):
    """Test PR description generation."""
    description = remediator_agent.generate_pr_description(
        secret_type="API_KEY",
        affected_files=["config.py", "settings.py"],
        confidence=0.95,
    )
    
    assert "Security Fix" in description
    assert "API_KEY" in description
    assert "config.py" in description


def test_create_rotation_script(remediator_agent):
    """Test secret rotation script generation."""
    aws_script = remediator_agent.create_rotation_script("aws_key")
    assert "aws" in aws_script.lower()
    
    github_script = remediator_agent.create_rotation_script("github_token")
    assert "github" in github_script.lower()


def test_generate_remediation_report(remediator_agent):
    """Test remediation report generation."""
    # Generate some patches first
    content = "API_KEY = 'secret'"
    secret_match = {"pattern": "api_key", "matched_text": "secret", "line": 1}
    
    remediator_agent.generate_patch(content, "test1.py", secret_match)
    remediator_agent.generate_patch(content, "test2.py", secret_match)
    
    report = remediator_agent.generate_remediation_report()
    
    assert "summary" in report
    assert report["summary"]["total_patches"] == 2
    assert "patches" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
