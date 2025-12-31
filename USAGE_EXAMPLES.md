# CASCADE DETECTOR - REAL-WORLD USAGE EXAMPLES

Copy-paste ready code for common use cases.

---

## Example 1: Quick Repository Scan

Scan your repository for secrets:

```python
from cascade_detector.agents.discovery import DiscoveryAgent
from cascade_detector.core.scanner import SecretScanner

scanner = SecretScanner(entropy_threshold=7.5)
agent = DiscoveryAgent(scanner=scanner, use_llm_analysis=False)

repo_path = "/path/to/your/repo"
results = agent.scan_repository(repo_path)

for secret in results["findings"]:
    print(f"Found: {secret['pattern_name']}")
    print(f"  File: {secret['file']}")
    print(f"  Confidence: {secret['confidence']:.2f}")
    print(f"  Entropy: {secret['entropy']:.2f} bits/char")
```

---

## Example 2: Detect GitHub Tokens

High-priority detection for GitHub tokens specifically:

```python
from cascade_detector.agents.discovery import DiscoveryAgent
from cascade_detector.core.scanner import SecretScanner

scanner = SecretScanner()
agent = DiscoveryAgent(scanner=scanner)

repo_path = "/path/to/repo"
history = agent.scan_git_history(repo_path, max_commits=1000)

github_tokens = [f for f in history["findings"] 
                 if "github" in f["pattern_name"].lower()]

print(f"Found {len(github_tokens)} GitHub tokens in history")
for token in github_tokens:
    print(f"  Commit: {token['commit_hash'][:7]}")
    print(f"  File: {token['file']}")
```

---

## Example 3: AWS Credential Rotation

Find and rotate AWS credentials automatically:

```python
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
        print("\nRotation script:")
        print(patch['rotation_script'])
```

---

## Example 4: Supply Chain Cascade Mapping

Map secrets cascading through dependencies:

```python
from cascade_detector.agents.propagation import PropagationAgent
from cascade_detector.core.graphs import CascadeGraph

# Create graph of your dependency network
graph = CascadeGraph()

graph.add_node("main-repo", type="application")
graph.add_node("util-lib", type="library")
graph.add_node("api-wrapper", type="library")

graph.add_edge("main-repo", "util-lib", relation="imports")
graph.add_edge("main-repo", "api-wrapper", relation="imports")

# Map cascade impact
propagation = PropagationAgent()
affected = propagation.find_cascading_impact("api-wrapper", graph)

print(f"If secret in api-wrapper, affects:")
for repo in affected:
    print(f"  - {repo}")

# Export visualization
mermaid = graph.export_mermaid(highlight_secret="api-wrapper")
print(mermaid)
```

---

## Example 5: Pre-Commit Hook Integration

Prevent secrets from being committed:

```python
#!/usr/bin/env python3
# File: .git/hooks/pre-commit

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
staged_files = result.stdout.strip().split("\n")

# Initialize detector
scanner = SecretScanner(entropy_threshold=8.0)
agent = DiscoveryAgent(scanner=scanner)

has_secrets = False
for file in staged_files:
    try:
        with open(file) as f:
            content = f.read()
        
        findings = agent.scan_blob(content, "staged", file)
        if findings["findings"]:
            print(f"❌ BLOCKED: Secrets in {file}")
            has_secrets = True
    except (FileNotFoundError, IsADirectoryError):
        pass

if has_secrets:
    print("⚠️  Use --no-verify to override")
    sys.exit(1)

print("✅ No secrets detected")
sys.exit(0)
```

---

## Example 6: GitHub Actions CI/CD

Integrate into your GitHub Actions pipeline:

```yaml
# .github/workflows/secret-scan.yml
name: Secret Scan

on: [push, pull_request]

jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Cascade Detector
        run: pip install -r requirements.txt
      
      - name: Scan for secrets
        run: cascade-detector scan . --output json > findings.json
      
      - name: Check for critical secrets
        run: |
          python3 -c "
          import json
          findings = json.load(open('findings.json'))
          critical = [f for f in findings if f['confidence'] > 0.8]
          if critical:
              print(f'FAIL: {len(critical)} secrets found')
              exit(1)
          "
      
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: secret-scan-results
          path: findings.json
```

---

## Example 7: Verify Active Secrets

Check if credentials are actually exploitable:

```python
from cascade_detector.agents.verifier import VerifierAgent

verifier = VerifierAgent()

secrets = [
    {
        "type": "aws",
        "access_key": "AKIAIOSFODNN7EXAMPLE",
        "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    },
    {
        "type": "github",
        "token": "ghp_16C7e42F292c6912E7710c838347Ae178B4a",
    },
]

results = verifier.verify_secrets(secrets)

for result in results:
    print(f"Secret: {result['type']}")
    print(f"  Valid: {result['is_valid']}")
    print(f"  Risk Level: {result['risk_level']}")
```

---

## Example 8: Mass Remediation Plan

Generate patches for all secrets across multiple repos:

```python
from cascade_detector.agents.discovery import DiscoveryAgent
from cascade_detector.agents.remediator import RemediatorAgent
from cascade_detector.core.scanner import SecretScanner
import json

scanner = SecretScanner()
discovery = DiscoveryAgent(scanner=scanner)
remediator = RemediatorAgent()

repos = ["/repo1", "/repo2", "/repo3"]
patches = []

for repo in repos:
    findings = discovery.scan_repository(repo)
    
    for finding in findings["findings"]:
        patch = remediator.generate_patch(
            file_path=finding['file'],
            secret_location=finding['location'],
            secret_type=finding['pattern_name']
        )
        patches.append({
            'repo': repo,
            'file': finding['file'],
            'patch': patch['diff'],
        })

# Save remediation plan
with open('remediation_plan.json', 'w') as f:
    json.dump(patches, f, indent=2)

print(f"✅ {len(patches)} patches generated")
```

---

## Example 9: Add Custom Patterns

Add organization-specific secret patterns:

```python
from cascade_detector.core.scanner import SecretScanner

scanner = SecretScanner()

# Internal API key pattern
scanner.add_pattern(
    name="internal_api_key",
    pattern=r"INTERNAL_API_KEY['\"]?\s*[=:]['\"]?([a-zA-Z0-9]{32})['\"]?",
    category="api_keys",
    priority=0.8
)

# Internal database URL
scanner.add_pattern(
    name="internal_db_url",
    pattern=r"(?:DATABASE_URL|DB_URL)['\"]?\s*[=:]['\"]?(?:postgresql|mysql)://[^\s]+['\"]?",
    category="database",
    priority=0.9
)

# Test patterns
test = 'INTERNAL_API_KEY="a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"'
findings = scanner.scan_blob(test, "test", "config.py")
for f in findings['findings']:
    print(f"✅ Detected: {f['pattern_name']}")
```

---

## Example 10: Audit Trail & Reporting

Generate compliance audit reports:

```python
from cascade_detector.agents.discovery import DiscoveryAgent
from cascade_detector.core.scanner import SecretScanner
import json
from datetime import datetime

scanner = SecretScanner()
agent = DiscoveryAgent(scanner=scanner)

findings = agent.scan_repository("/path/to/repo")

audit_report = {
    "timestamp": datetime.now().isoformat(),
    "repository": "/path/to/repo",
    "total_secrets": len(findings['findings']),
    "secrets_by_type": {},
    "findings": findings['findings'],
}

for f in findings['findings']:
    pattern = f['pattern_name']
    audit_report['secrets_by_type'][pattern] = \
        audit_report['secrets_by_type'].get(pattern, 0) + 1

audit_file = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(audit_file, 'w') as f:
    json.dump(audit_report, f, indent=2)

print(f"✅ Audit report saved: {audit_file}")
```

---

## Quick CLI Commands

```bash
# Scan current directory
cascade-detector scan .

# Scan specific repository
cascade-detector scan /path/to/repo

# Scan with custom config
cascade-detector scan . --config custom-config.yml

# Verify if secrets are active (requires API credentials)
cascade-detector verify --aws-key AKIA... --aws-secret ...

# Set configuration
cascade-detector config set-config key value

# View current config
cascade-detector config get-config

# Output as JSON for automation
cascade-detector scan . --output json > results.json
```

---

## Deployment Checklist

- [ ] Install locally: `pip install -r requirements.txt`
- [ ] Test on sample repo: `cascade-detector scan`
- [ ] Add pre-commit hook (Example 5)
- [ ] Integrate with CI/CD (Example 6)
- [ ] Add custom patterns (Example 9)
- [ ] Set up monitoring/alerts
- [ ] Configure remediation automation (Example 8)
- [ ] Enable verification agent (Example 7)

---

## For More Help

```bash
cascade-detector --help
cascade-detector scan --help
cascade-detector verify --help
```

See documentation in `/docs` directory.
