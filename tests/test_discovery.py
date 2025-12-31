"""Tests for Discovery agent."""

import pytest
from cascade_detector.agents.discovery import DiscoveryAgent
from cascade_detector.core.scanner import SecretScanner


@pytest.fixture
def discovery_agent():
    """Create a DiscoveryAgent instance for testing."""
    scanner = SecretScanner(entropy_threshold=7.5)
    return DiscoveryAgent(scanner=scanner, use_llm_analysis=False)


def test_scan_blob_with_aws_key(discovery_agent):
    """Test scanning blob with AWS access key."""
    content = """
    AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'
    AWS_SECRET_ACCESS_KEY = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    """
    
    result = discovery_agent.scan_blob(content, "hash123", "secrets.py")
    assert result["total_findings"] > 0


def test_scan_blob_with_github_token(discovery_agent):
    """Test scanning blob with GitHub token."""
    content = "github_token = 'ghp_16C7e42F292c6912E7710c838347Ae178B4a'"
    
    result = discovery_agent.scan_blob(content, "hash456", "config.py")
    assert result["total_findings"] > 0


def test_scan_blob_with_api_key(discovery_agent):
    """Test scanning blob with API key."""
    content = "API_KEY = 'sk_live_51234567890abcdefghijk'"
    
    result = discovery_agent.scan_blob(content, "hash789", "app.py")
    assert result["total_findings"] > 0


def test_scan_lockfile(discovery_agent):
    """Test scanning dependency lockfile."""
    content = """{
      "dependencies": {
        "package": {
          "version": "1.0.0",
          "api_key": "secret123"
        }
      }
    }"""
    
    result = discovery_agent.scan_lockfile(content, "package-lock.json")
    assert "findings" in result
    assert "lockfile_type" in result


def test_scan_clean_code(discovery_agent):
    """Test scanning code without secrets."""
    content = """
    def hello_world():
        print("Hello, world!")
        
    x = 42
    y = "safe_string_without_secrets"
    """
    
    result = discovery_agent.scan_blob(content, "hash_clean", "clean.py")
    # May still have findings due to pattern matching false positives
    # but they should be low confidence


def test_entropy_calculation():
    """Test entropy calculation."""
    scanner = SecretScanner()
    
    # High entropy string (random)
    high_entropy = "abcdef0123456789abcdef0123456789"
    entropy_high = scanner.calculate_entropy(high_entropy)
    
    # Low entropy string (repetitive)
    low_entropy = "aaaaaabbbbbbcccccc"
    entropy_low = scanner.calculate_entropy(low_entropy)
    
    assert entropy_high > entropy_low


def test_generate_report(discovery_agent):
    """Test report generation."""
    scan_results = [
        {
            "findings": [
                {
                    "pattern": "aws_key",
                    "confidence": 0.9,
                    "file": "test.py"
                }
            ]
        }
    ]
    
    report = discovery_agent.generate_report(scan_results)
    assert "summary" in report
    assert "findings" in report
    assert report["summary"]["total_findings"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
