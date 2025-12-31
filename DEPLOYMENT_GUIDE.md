# CASCADE DETECTOR - DEPLOYMENT GUIDE

## Quick Start (5 Minutes)

### 1. Install
```bash
cd /Users/sathvikkurapati/Downloads/cascade-detector
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Verify Installation
```bash
cascade-detector --version
cascade-detector scan --help
```

### 3. Scan Your First Repository
```bash
cascade-detector scan /path/to/your/repo
# or scan current directory
cascade-detector scan .
```

### 4. View Results
```bash
# JSON output for automation
cascade-detector scan . --output json > findings.json

# Read the results
cat findings.json | python3 -m json.tool
```

---

## Configuration (5 Minutes)

### Set Up Configuration
```bash
# View current config
cascade-detector config get-config

# Set custom entropy threshold (for fewer false positives)
cascade-detector config set-config entropy-threshold 8.5

# Enable strict mode (fewer findings, higher precision)
cascade-detector config set-config scan-mode strict

# Enable aggressive mode (more findings, higher recall)
cascade-detector config set-config scan-mode aggressive
```

### Configuration File
Location: `~/.cascade-detector/config.yml`

Example:
```yaml
entropy_threshold: 7.5
scan_mode: normal
include_patterns:
  - "**/config/**"
  - "**/.env*"
  - "**/secrets/**"
exclude_patterns:
  - "**/node_modules/**"
  - "**/vendor/**"
  - "**/.git/**"
verification_enabled: false
llm_enabled: false
```

---

## Pre-Commit Hook Integration (5 Minutes)

### Step 1: Create Hook File
```bash
cat > .git/hooks/pre-commit << 'SCRIPT'
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
staged_files = result.stdout.strip().split("\n")

# Initialize detector in STRICT mode
scanner = SecretScanner(entropy_threshold=8.0)
agent = DiscoveryAgent(scanner=scanner)

has_secrets = False
for file in staged_files:
    if not file:
        continue
    try:
        with open(file) as f:
            findings = agent.scan_blob(f.read(), "staged", file)
        if findings["findings"]:
            print(f"❌ BLOCKED: Secrets detected in {file}")
            for f in findings["findings"]:
                print(f"  - {f['pattern_name']} (confidence: {f['confidence']:.2f})")
            has_secrets = True
    except:
        pass

if has_secrets:
    print("\n⚠️  Commit blocked due to detected secrets")
    print("To override: git commit --no-verify (not recommended!)")
    sys.exit(1)

print("✅ No secrets detected - commit allowed")
sys.exit(0)
SCRIPT

chmod +x .git/hooks/pre-commit
```

### Step 2: Test the Hook
```bash
# Create a file with a secret
echo "AWS_SECRET_KEY = 'wJalrXUtnFEMI/K7MDENG'" > test.py
git add test.py

# Try to commit (should be blocked)
git commit -m "test"  # Will be blocked ✅

# Remove the secret
rm test.py
git reset HEAD test.py

# Now commit works
git commit -m "safe commit"  # Works ✅
```

---

## CI/CD Integration (GitHub Actions)

### Step 1: Create Workflow File
```bash
mkdir -p .github/workflows
cat > .github/workflows/secret-scan.yml << 'YAML'
name: Secret Scan with Cascade Detector

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

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
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Scan for secrets
        run: |
          cascade-detector scan . --output json > findings.json
      
      - name: Check results
        run: |
          python3 << 'PYTHON'
          import json
          findings = json.load(open('findings.json'))
          
          # Show all findings
          print(f"\n🔍 Found {len(findings)} potential secrets")
          
          # Check for critical findings
          critical = [f for f in findings if f['confidence'] > 0.8]
          if critical:
              print(f"\n�� CRITICAL: {len(critical)} high-confidence secrets")
              for f in critical:
                  print(f"  - {f['pattern_name']} in {f['file']}")
              exit(1)
          else:
              print("\n✅ No critical secrets found")
              exit(0)
          PYTHON
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: cascade-detector-results
          path: findings.json
YAML
```

### Step 2: Commit the Workflow
```bash
git add .github/workflows/secret-scan.yml
git commit -m "Add Cascade Detector to CI/CD"
git push
```

The workflow will now run on every push and pull request!

---

## Verification Agent (Optional but Recommended)

### Step 1: Set Up AWS Credentials
```bash
# For AWS verification
export AWS_ACCESS_KEY_ID="your-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-key"

# For GitHub verification
export GITHUB_TOKEN="your-github-token"

# For npm verification
export NPM_TOKEN="your-npm-token"
```

### Step 2: Enable Verification
```bash
cascade-detector config set-config verification-enabled true
```

### Step 3: Verify Secrets
```bash
cascade-detector verify \
  --aws-key "AKIAIOSFODNN7EXAMPLE" \
  --aws-secret "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Output:
# ✅ AWS credential verified as ACTIVE
# ⚠️  Immediate action required
```

---

## Remediation (Automated Fixes)

### Generate Patches
```python
from cascade_detector.agents.remediator import RemediatorAgent

remediator = RemediatorAgent()

# Generate patch for hardcoded AWS credentials
patch = remediator.generate_patch(
    file_path="config.py",
    secret_location="line 5, column 15",
    secret_type="aws_credential"
)

print("Patch:")
print(patch['diff'])

print("\nRotation script:")
print(patch['rotation_script'])
```

### Apply Patches Automatically
```bash
# 1. Generate all patches
cascade-detector scan . --generate-patches > patches.diff

# 2. Review the patches
less patches.diff

# 3. Apply safely
git apply --check patches.diff  # Dry run
git apply patches.diff          # Actually apply

# 4. Commit and rotate credentials
git commit -am "Fix: Rotate leaked credentials"
# Now run AWS credential rotation, etc.
```

---

## Real-World Examples

### Example 1: GitHub Repository
```bash
# Clone a repository to scan
git clone https://github.com/user/repo
cd repo

# Scan for secrets
cascade-detector scan .

# View summary
cascade-detector scan . --output json | python3 -m json.tool | less
```

### Example 2: Multiple Repositories
```bash
# Create a scan script
cat > scan_repos.sh << 'BASH'
#!/bin/bash
for repo in /path/to/repos/*; do
  echo "Scanning $repo..."
  cascade-detector scan "$repo" --output json > "${repo##*/}_findings.json"
done

# Aggregate results
python3 << 'PYTHON'
import json
import glob

all_findings = []
for file in glob.glob("*_findings.json"):
    with open(file) as f:
        findings = json.load(f)
    all_findings.extend(findings)

print(f"Total secrets found: {len(all_findings)}")
for pattern in set(f['pattern_name'] for f in all_findings):
    count = sum(1 for f in all_findings if f['pattern_name'] == pattern)
    print(f"  {pattern}: {count}")
PYTHON
BASH

chmod +x scan_repos.sh
./scan_repos.sh
```

### Example 3: Supply Chain Security
```bash
from cascade_detector.agents.propagation import PropagationAgent
from cascade_detector.core.graphs import CascadeGraph

# Build dependency graph
graph = CascadeGraph()

# Add repositories and dependencies
repos = [
    ("api-gateway", ["auth-lib", "utils-lib"]),
    ("auth-lib", ["utils-lib", "crypto-lib"]),
    ("utils-lib", []),
]

for repo_name, deps in repos:
    graph.add_node(repo_name, type="library")
    for dep in deps:
        graph.add_node(dep, type="library")
        graph.add_edge(repo_name, dep, relation="depends_on")

# If secret found in utils-lib, show impact
propagation = PropagationAgent()
affected = propagation.find_cascading_impact("utils-lib", graph)

print(f"If secret in utils-lib, affects: {affected}")
print("\nMermaid visualization:")
print(graph.export_mermaid(highlight_secret="utils-lib"))
```

---

## Troubleshooting

### Issue: "No patterns matched"
**Solution**: Your entropy threshold might be too high. Lower it:
```bash
cascade-detector config set-config entropy-threshold 6.0
```

### Issue: "Too many false positives"
**Solution**: Increase entropy threshold for stricter matching:
```bash
cascade-detector config set-config entropy-threshold 9.0
```

### Issue: "LLM not available"
**Solution**: This is optional. Install Ollama if you want LLM enhancement:
```bash
# Install Ollama (optional)
brew install ollama

# Download mistral model
ollama pull mistral

# Then set config:
cascade-detector config set-config llm-enabled true
```

### Issue: "Verification failing"
**Solution**: Make sure credentials are set:
```bash
# Check AWS credentials
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY

# If empty, set them
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"

# Try again
cascade-detector verify --aws-key AKIA... --aws-secret ...
```

### Issue: "Permission denied" on pre-commit hook
**Solution**: Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Performance Tips

### 1. Exclude Large Directories
```bash
# Scan but exclude node_modules, etc
cascade-detector scan . \
  --exclude "node_modules" \
  --exclude ".git" \
  --exclude "dist" \
  --exclude "build"
```

### 2. Use Strict Mode for Large Repos
```bash
cascade-detector config set-config scan-mode strict
cascade-detector scan /huge/repo

# Strict mode: Faster, fewer FP, but might miss some secrets
```

### 3. Scan Only Changed Files (CI/CD)
```bash
# In your CI/CD, only scan changed files
git diff main...HEAD --name-only | \
  xargs cascade-detector scan
```

### 4. Cache Results
```bash
# First scan
cascade-detector scan . --output json > baseline.json

# Later, scan incrementally
cascade-detector scan . --output json > latest.json

# Compare
diff baseline.json latest.json
```

---

## Support & Documentation

- **Quick Reference**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
- **Detailed Report**: [REAL_WORLD_VALIDATION_REPORT.md](REAL_WORLD_VALIDATION_REPORT.md)
- **Validation Summary**: [FINAL_VALIDATION_SUMMARY.md](FINAL_VALIDATION_SUMMARY.md)
- **Source Code**: See `cascade_detector/` directory
- **Tests**: See `tests/` directory

---

## Next Steps After Deployment

### Week 1
- [ ] Install and test locally
- [ ] Add pre-commit hook
- [ ] Add GitHub Actions workflow
- [ ] Fix any found secrets

### Week 2-3
- [ ] Enable verification agent
- [ ] Set up automated remediation
- [ ] Configure custom patterns
- [ ] Set up monitoring

### Month 1+
- [ ] Evaluate GitHub App integration
- [ ] Implement supply chain monitoring
- [ ] Consider enterprise features
- [ ] Collect team feedback

---

## Success Criteria

✅ **You'll know it's working when:**
1. Pre-commit hook blocks commits with secrets
2. GitHub Actions catches secrets in PRs
3. Cascade detector finds real secrets in your repos
4. False positive rate is <2%
5. Team adopts it as standard practice

---

## Quick Command Reference

```bash
# Scan
cascade-detector scan .
cascade-detector scan /path/to/repo
cascade-detector scan . --output json > findings.json

# Configuration
cascade-detector config get-config
cascade-detector config set-config entropy-threshold 8.0

# Verification
cascade-detector verify --aws-key KEY --aws-secret SECRET

# Help
cascade-detector --help
cascade-detector scan --help
```

---

## ROI Tracking

Track the value delivered:
```bash
# Track incidents prevented
echo "Secrets found: $(cascade-detector scan . --output json | jq length)"

# Track false positives
echo "Review rate: X% of findings are reviewed"

# Track MTTR improvement
echo "Average response time: Y minutes (was 4-8 hours before)"
```

---

**You're all set! Start scanning now!** 🎉

For detailed information, see:
- [FINAL_VALIDATION_SUMMARY.md](FINAL_VALIDATION_SUMMARY.md) - Complete validation
- [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - 10 copy-paste examples
- [REAL_WORLD_VALIDATION_REPORT.md](REAL_WORLD_VALIDATION_REPORT.md) - Deep technical report

