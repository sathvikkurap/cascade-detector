#!/usr/bin/env python3
"""
Real-world usage examples and practical scenarios.
Copy-paste ready code for common use cases.
"""

import json
from pathlib import Path


EXAMPLES = {
    "1_quick_repo_scan": """
# EXAMPLE 1: Scan Your Repository for Secrets

from cascade_detector.agents.discovery import DiscoveryAgent
from cascade_detector.core.scanner import SecretScanner

# Initialize with default patterns
scanner = SecretScanner(entropy_threshold=7.5)
agent = DiscoveryAgent(scanner=scanner, use_llm_analysis=False)

# Scan a repository
repo_path = "/path/to/your/repo"
results = agent.scan_repository(repo_path)

# Print findings
for secret in results["findings"]:
    print(f"Found: {secret['pattern_name']}")
    print(f"  File: {secret['file']}")
    print(f"  Confidence: {secret['confidence']:.2f}")
    print(f"  Entropy: {secret['entropy']:.2f} bits/char")
    print()
""",
    
    "2_github_token_detection": """
# EXAMPLE 2: Detect GitHub Tokens (High Priority)

from cascade_detector.agents.discovery import DiscoveryAgent
from cascade_detector.core.scanner import SecretScanner

scanner = SecretScanner()
agent = DiscoveryAgent(scanner=scanner)

# Scan recent git history for GitHub tokens
repo_path = "/path/to/repo"
history = agent.scan_git_history(repo_path, max_commits=1000)

# Filter for GitHub tokens only
github_tokens = [f for f in history["findings"] 
                 if "github" in f["pattern_name"].lower()]

print(f"Found {len(github_tokens)} GitHub tokens in history")
for token in github_tokens:
    print(f"  Commit: {token['commit_hash'][:7]}")
    print(f"  File: {token['file']}")
    print(f"  Author: {token.get('author', 'Unknown')}")
""",

    "3_aws_credential_rotation": """
# EXAMPLE 3: Find and Rotate AWS Credentials

from cascade_detector.agents.discovery import DiscoveryAgent
from cascade_detector.agents.remediator import RemediatorAgent
from cascade_detector.core.scanner import SecretScanner

scanner = SecretScanner()
discovery = DiscoveryAgent(scanner=scanner)
remediator = RemediatorAgent()

# Find AWS credentials
findings = discovery.scan_blob(
    open("/path/to/config.py").read(),
    "hash",
    "config.py"
)

# Generate rotation patch
for finding in findings["findings"]:
    if "aws" in finding["pattern_name"].lower():
        patch = remediator.generate_patch(
            file_path="config.py",
            secret_location=finding['location'],
            secret_type="aws_credential"
        )
        
        print("Generated patch:")
        print(patch['diff'])
        print("\\nRotation script:")
        print(patch['rotation_script'])
""",

    "4_supply_chain_cascade": """
# EXAMPLE 4: Map Secret Cascade Through Dependencies

from cascade_detector.agents.propagation import PropagationAgent
from cascade_detector.core.graphs import CascadeGraph

# Create graph of your dependency network
graph = CascadeGraph()

# Add your repositories and their dependencies
graph.add_node("main-repo", type="application")
graph.add_node("util-lib", type="library")
graph.add_node("api-wrapper", type="library")

graph.add_edge("main-repo", "util-lib", relation="imports")
graph.add_edge("main-repo", "api-wrapper", relation="imports")
graph.add_edge("util-lib", "api-wrapper", relation="imports")

# If secret found in api-wrapper, map cascade
propagation = PropagationAgent()
affected = propagation.find_cascading_impact("api-wrapper", graph)

print(f"If secret found in api-wrapper, affects:")
for repo in affected:
    print(f"  - {repo}")

# Export as visualization
mermaid_graph = graph.export_mermaid(
    highlight_secret="api-wrapper"
)
print("\\nVisualization:")
print(mermaid_graph)
""",

    "5_pre_commit_integration": """
# EXAMPLE 5: Pre-Commit Hook Integration

# File: .git/hooks/pre-commit
#!/usr/bin/env python3

import subprocess
import sys
from cascade_detector.agents.discovery import DiscoveryAgent
from cascade_detector.core.scanner import SecretScanner

# Get staged files
result = subprocess.run(
    ["git", "diff", "--cached", "--name-only"],
    capture_output=True,
    text=True
)
staged_files = result.stdout.strip().split("\\n")

# Initialize detector
scanner = SecretScanner(entropy_threshold=8.0)  # Strict mode
agent = DiscoveryAgent(scanner=scanner)

# Check each file
has_secrets = False
for file in staged_files:
    try:
        with open(file) as f:
            content = f.read()
        
        findings = agent.scan_blob(content, "staged", file)
        if findings["findings"]:
            print(f"❌ BLOCKED: Secrets detected in {file}")
            for finding in findings["findings"]:
                print(f"  - {finding['pattern_name']}")
            has_secrets = True
    except (FileNotFoundError, IsADirectoryError):
        pass

if has_secrets:
    print("\\n⚠️  Commit blocked due to secrets.")
    print("Use --no-verify to override (not recommended!)")
    sys.exit(1)

print("✅ No secrets detected - proceeding with commit")
sys.exit(0)
""",

    "6_github_actions_ci_cd": """
# EXAMPLE 6: GitHub Actions CI/CD Integration

# File: .github/workflows/secret-scan.yml
# name: Secret Scan with Cascade Detector
# on: [push, pull_request]
# jobs:
#   secret-scan:
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v3
#         with:
#           fetch-depth: 0
#       - name: Set up Python
#         uses: actions/setup-python@v4
#         with:
#           python-version: '3.11'
#       - name: Install Cascade Detector
#         run: pip install -r requirements.txt
#       - name: Scan for secrets
#         run: cascade-detector scan . --output json > findings.json
#       - name: Upload results
#         if: always()
#         uses: actions/upload-artifact@v3
#         with:
#           name: secret-scan-results
#           path: findings.json

# See /examples/github_actions_example.yml for full YAML

import subprocess
result = subprocess.run(
    ["cascade-detector", "scan", ".", "--output", "json"],
    capture_output=True,
    text=True
)

import json
findings = json.loads(result.stdout)
critical = [f for f in findings if f['confidence'] > 0.8]
if critical:
    print(f'CRITICAL: {len(critical)} high-confidence secrets found')
    exit(1)
""",

    "7_verify_active_secrets": """
# EXAMPLE 7: Verify if Secrets Are Actually Exploitable

from cascade_detector.agents.verifier import VerifierAgent

verifier = VerifierAgent()

# Test credentials against real services (non-destructive)
secrets_to_check = [
    {
        "type": "aws",
        "access_key": "AKIAIOSFODNN7EXAMPLE",
        "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    },
    {
        "type": "github",
        "token": "ghp_16C7e42F292c6912E7710c838347Ae178B4a",
    },
    {
        "type": "npm",
        "token": "npm_1234567890abcdefghijklmnopqrs",
    },
]

results = verifier.verify_secrets(secrets_to_check)

for result in results:
    print(f"Secret: {result['type']}")
    print(f"  Valid: {result['is_valid']}")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Verified By: {result['verification_providers']}")
    print()
""",

    "8_mass_remediation": """
# EXAMPLE 8: Generate Mass Remediation Plan

from cascade_detector.agents.discovery import DiscoveryAgent
from cascade_detector.agents.remediator import RemediatorAgent
from cascade_detector.core.scanner import SecretScanner

scanner = SecretScanner()
discovery = DiscoveryAgent(scanner=scanner)
remediator = RemediatorAgent()

# Scan multiple repositories
repos = [
    "/path/to/repo1",
    "/path/to/repo2",
    "/path/to/repo3",
]

all_patches = []
for repo in repos:
    findings = discovery.scan_repository(repo)
    
    for finding in findings["findings"]:
        patch = remediator.generate_patch(
            file_path=finding['file'],
            secret_location=finding['location'],
            secret_type=finding['pattern_name']
        )
        all_patches.append({
            'repo': repo,
            'file': finding['file'],
            'patch': patch['diff'],
            'rotation': patch['rotation_script'],
        })

# Generate remediation report
print(f"Total secrets found: {len(all_patches)}")
print("\\nRemediation Plan:")
print("-" * 60)

for patch_info in all_patches:
    print(f"\\nRepository: {patch_info['repo']}")
    print(f"File: {patch_info['file']}")
    print("Patch:")
    print(patch_info['patch'])
    print("\\nRotation Script:")
    print(patch_info['rotation'])
    print("-" * 60)

# Save as JSON for automation
import json
with open('remediation_plan.json', 'w') as f:
    json.dump(all_patches, f, indent=2)

print(f"\\n✅ Remediation plan saved to remediation_plan.json")
""",

    "9_custom_patterns": """
# EXAMPLE 9: Add Custom Secret Patterns for Your Organization

from cascade_detector.core.scanner import SecretScanner

# Create scanner and add custom patterns
scanner = SecretScanner()

# Add pattern for internal API keys
scanner.add_pattern(
    name="internal_api_key",
    pattern=r"INTERNAL_API_KEY['\"]?\\s*[=:]['\"]?([a-zA-Z0-9]{32})['\"]?",
    category="api_keys",
    priority=0.8  # High confidence if matched
)

# Add pattern for internal database URLs
scanner.add_pattern(
    name="internal_db_url",
    pattern=r"(?:DATABASE_URL|DB_URL)['\"]?\\s*[=:]['\"]?(?:postgresql|mysql)://[^\\s]+['\"]?",
    category="database",
    priority=0.9
)

# Test custom patterns
test_code = """
INTERNAL_API_KEY="a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
DATABASE_URL="postgresql://user:pass@internal-db.company.com/prod"
"""

findings = scanner.scan_blob(test_code, "test_hash", "config.py")
for finding in findings['findings']:
    print(f"Detected: {finding['pattern_name']}")
    print(f"  Confidence: {finding['confidence']}")
    print(f"  Entropy: {finding['entropy']:.2f}")
""",

    "10_reporting_and_audit": """
# EXAMPLE 10: Generate Audit Report

from cascade_detector.agents.discovery import DiscoveryAgent
from cascade_detector.core.scanner import SecretScanner
import json
from datetime import datetime

scanner = SecretScanner()
agent = DiscoveryAgent(scanner=scanner)

# Scan repository
findings = agent.scan_repository("/path/to/repo")

# Create audit report
audit_report = {
    "timestamp": datetime.now().isoformat(),
    "repository": "/path/to/repo",
    "total_secrets_found": len(findings['findings']),
    "secrets_by_type": {},
    "findings": findings['findings'],
}

# Aggregate by type
for finding in findings['findings']:
    pattern = finding['pattern_name']
    if pattern not in audit_report['secrets_by_type']:
        audit_report['secrets_by_type'][pattern] = 0
    audit_report['secrets_by_type'][pattern] += 1

# Save audit trail
audit_file = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(audit_file, 'w') as f:
    json.dump(audit_report, f, indent=2, default=str)

print(f"✅ Audit report saved to {audit_file}")
print(f"\\nSummary:")
print(f"  Total secrets: {audit_report['total_secrets_found']}")
print(f"  By type:")
for secret_type, count in audit_report['secrets_by_type'].items():
    print(f"    - {secret_type}: {count}")
""",
}


def print_examples():
    """Print all examples with nice formatting."""
    print("\n" + "=" * 80)
    print("CASCADE DETECTOR - REAL-WORLD USAGE EXAMPLES")
    print("=" * 80)
    
    for title, code in EXAMPLES.items():
        num, name = title.split("_", 1)
        print(f"\n{'=' * 80}")
        print(f"EXAMPLE {num.replace('_', '')}: {name.replace('_', ' ').title()}")
        print("=" * 80)
        print(code)
    
    print("\n" + "=" * 80)
    print("✅ All examples are copy-paste ready!")
    print("=" * 80)
    print("\nFor more help:")
    print("  cascade-detector --help")
    print("  cascade-detector scan --help")
    print("  cascade-detector verify --help")
    print("\nDocumentation: See /docs directory")
    print("=" * 80 + "\n")


def save_examples_to_file():
    """Save all examples to individual files."""
    examples_dir = Path("/Users/sathvikkurapati/Downloads/cascade-detector/examples")
    examples_dir.mkdir(exist_ok=True)
    
    for title, code in EXAMPLES.items():
        filename = examples_dir / f"{title}.py"
        with open(filename, 'w') as f:
            f.write(code)
    
    print(f"✅ Examples saved to {examples_dir}/")


if __name__ == "__main__":
    print_examples()
    save_examples_to_file()
