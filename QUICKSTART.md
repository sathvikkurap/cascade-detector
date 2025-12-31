# Quick Start Guide

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/cascade-detector.git
cd cascade-detector
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up Ollama (Optional but Recommended)

For LLM-enhanced analysis:

```bash
# Using Docker
docker pull ollama/ollama
docker run -d -p 11434:11434 --name ollama ollama/ollama

# Pull a model
docker exec ollama ollama pull mistral

# Or install locally from https://ollama.ai
```

## Basic Usage

### CLI Scanning

```bash
# Scan a local repository
cascade-detector scan /path/to/repo

# Scan with custom options
cascade-detector scan /path/to/repo \
  --depth 5 \
  --entropy-threshold 7.5 \
  --output ./reports \
  --format json,html,mermaid

# Without LLM analysis
cascade-detector scan /path/to/repo --no-llm
```

### Python API

```python
from cascade_detector import (
    DiscoveryAgent,
    PropagationAgent,
    VerifierAgent,
    RemediatorAgent,
)
from cascade_detector.core import SecretScanner, OllamaLLM
from cascade_detector.orchestration import CascadeOrchestrator

# Using orchestrator (recommended)
orchestrator = CascadeOrchestrator()
result = orchestrator.run("/path/to/repo")

print(f"Findings: {result['discovery_report']['summary']}")
print(f"Cascade paths: {result['propagation_report']}")

# Or use agents individually
scanner = SecretScanner(entropy_threshold=7.5)
discovery = DiscoveryAgent(scanner=scanner)

# Scan content
findings = discovery.scan_blob(
    "API_KEY = 'sk_live_secret'",
    blob_hash="abc123",
    file_path="config.py"
)

print(f"Found {len(findings['findings'])} potential secrets")
```

## Configuration

### config.yaml

Edit `config.yaml` to customize:

```yaml
scanner:
  entropy_threshold: 7.5  # Adjust sensitivity
  max_depth: 5  # For dependency traversal

llm:
  model: "mistral"  # Change LLM model
  base_url: "http://localhost:11434"

agents:
  discovery:
    llm_analysis: true  # Enable/disable LLM
  verifier:
    require_consensus: true  # Require multi-provider agreement
```

### CLI Config Commands

```bash
# View current configuration
cascade-detector config

# Set a value
cascade-detector set-config --key scanner.entropy_threshold --value 8.0 --type float
```

## Interpreting Results

### Discovery Report

```json
{
  "summary": {
    "total_findings": 42,
    "high_confidence": 8,
    "medium_confidence": 12,
    "low_confidence": 22
  },
  "findings_by_category": {
    "aws": 5,
    "github": 2,
    "api_keys": 35
  }
}
```

- **High Confidence (≥0.8)**: Likely real secrets
- **Medium Confidence (0.5-0.8)**: Manual review recommended
- **Low Confidence (<0.5)**: Probable false positives

### Propagation Report

Shows how secrets cascade through:
- Dependencies (npm, pip, etc.)
- Repository forks
- Git history

### Verification Report

Indicates which secrets are:
- **Active**: Confirmed valid (high risk)
- **Inactive**: Invalid or revoked (lower risk)
- **Unverified**: Could not be checked

## Common Workflows

### 1. Quick Scan

```bash
cascade-detector scan /path/to/repo --format json
# Check ./reports/report.json
```

### 2. Comprehensive Analysis

```bash
cascade-detector scan /path/to/repo \
  --depth 5 \
  --format json,html,mermaid
# View ./reports/cascade-diagram.mermaid in Mermaid viewer
```

### 3. Generate Patches

```python
from cascade_detector.agents.remediator import RemediatorAgent

remediator = RemediatorAgent()

# Generate patch for a finding
patch = remediator.generate_patch(
    file_content="API_KEY = 'secret'",
    file_path="config.py",
    secret_match={"pattern": "api_key", ...}
)

print(patch.diff)  # Review before applying
```

### 4. Create Rotation Script

```python
script = remediator.create_rotation_script("aws_key")
# Run script to rotate AWS credentials
```

## Troubleshooting

### Ollama not responding
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart container
docker restart ollama

# Or run scan without LLM
cascade-detector scan /path/to/repo --no-llm
```

### Memory issues
```bash
# Limit repo scan with smaller file size
cascade-detector scan /path/to/small-repo

# Increase Docker memory
docker run -m 4g -p 11434:11434 ollama/ollama
```

### High false positive rate
```bash
# Increase entropy threshold
cascade-detector scan /path/to/repo --entropy-threshold 8.5
```

## Next Steps

- Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Read [documentation](docs/) for detailed API docs
- Join discussions for questions
- Report issues on GitHub

## Performance Tips

1. **Filter by file type**: Scan only suspicious file types
2. **Limit depth**: Reduce `max_depth` for faster propagation analysis
3. **Use pattern categories**: Scan specific secret types
4. **Batch processing**: Process repositories in parallel

## Security Notes

- **No data exfiltration**: All scanning happens locally
- **Offline mode**: Works without internet connection
- **Masked verification**: Never sends actual secrets to endpoints
- **Clean up reports**: Remove reports with sensitive findings after review

## Further Reading

- [Architecture Overview](docs/architecture.md)
- [API Documentation](docs/api.md)
- [Threat Model](docs/threat-model.md)
- [Benchmarks](docs/benchmarks.md)
