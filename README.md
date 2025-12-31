# AI-Powered Secret Cascade Detector

Scans repositories for leaked secrets and traces their propagation through dependencies, forks, and git history. Features automated verification and remediation PRs.

## Features

- **Discovery Agent**: Regex-based pattern matching (500+ patterns) + LLM context scanning with entropy scoring
- **Propagation Agent**: Builds directed graphs of secret cascade through dependencies, forks, and git history
- **Verifier Agent**: Masked behavioral checks to verify if secrets are actively exploitable
- **Remediator Agent**: Auto-generates remediation PRs with hardcoded secret replacements and rotation scripts

## Quick Start

### Prerequisites
- Python 3.11+
- Git
- Docker (for sandbox verification)
- Ollama with local LLM (default: Mistral)
- GitHub API token (for GraphQL queries)

### Installation

```bash
pip install -r requirements.txt
```

### Usage

```bash
# Scan a repository
cascade-detector scan <repo_url_or_path>

# With custom configuration
cascade-detector scan <repo_url_or_path> --config config.yaml --depth 5

# Generate report with visualizations
cascade-detector report --format json,mermaid,html
```

## Architecture

### Agents
- **Discovery**: Finds secrets in git history, lockfiles, and code blobs
- **Propagation**: Maps transitive dependencies and fork networks
- **Verifier**: Validates active secret exploitation risk
- **Remediator**: Generates and tests remediation patches

### Tech Stack
- **GitPython**: Full repository history scanning
- **NetworkX**: Dependency and fork graph construction
- **LangGraph**: Multi-agent orchestration
- **Ollama**: Local LLM inference
- **Streamlit**: Dashboard visualization
- **Docker**: Sandbox verification environment

## Project Structure

```
cascade-detector/
├── agents/                 # Agent implementations
│   ├── discovery.py       # Secret detection and pattern matching
│   ├── propagation.py     # Dependency and fork graph building
│   ├── verifier.py        # Secret verification via behavioral checks
│   └── remediator.py      # PR generation and patch testing
├── core/
│   ├── scanner.py         # Core scanning logic
│   ├── patterns.py        # 500+ secret patterns from TruffleHog
│   ├── llm.py            # Ollama LLM integration
│   └── graphs.py         # NetworkX utilities
├── cli/
│   ├── main.py           # CLI entry point
│   └── config.py         # Configuration management
├── dashboard/            # Streamlit UI
│   └── app.py
├── docker/              # Sandbox environment
│   └── Dockerfile
├── tests/               # Unit and integration tests
│   ├── fixtures/        # Test datasets (DVWA, real breaches)
│   ├── test_discovery.py
│   ├── test_propagation.py
│   ├── test_verifier.py
│   └── test_remediator.py
├── examples/            # Demo repos and results
├── requirements.txt
├── pyproject.toml
├── .github/workflows/   # GitHub Actions
│   └── ci.yml
└── config.yaml         # Default configuration
```

## Milestones

### Phase 1: Core Scanner (10 days)
- MVP CLI with Discovery agent
- Streamlit dashboard demo
- Target: 500 stars, 95% recall on benchmark dataset

### Phase 2: Graph + Propagation (14 days)
- NetworkX integration
- GIF demos of cascade mapping
- Target: Trending on GitHub, 20 contrib PRs

### Phase 3: Verify + Remediate (14 days)
- Docker sandbox verification
- GitHub App for auto-PRs
- VS Code extension
- Target: 5k stars, <1% FP on verified leaks

### Phase 4: Production (7 days)
- CI/CD GitHub Actions
- Benchmark documentation vs TruffleHog
- Target: 10k+ stars, HN frontpage

## Anti-Hallucination Guardrails

- ✅ Data grounding with GitHub's 10k+ leaked secrets dataset
- ✅ Strict CoT prompting (evidence → pattern → score → action)
- ✅ Unit tests on DVWA + real breach datasets
- ✅ Require 2/3 agent consensus for findings
- ✅ Transparent logging of evidence hashes
- ✅ Public evaluation suite for community verification

## References

- [TruffleHog](https://github.com/trufflesecurity/trufflehog) - Inspiration for pattern detection
- [GitHub Secret Scanner](https://docs.github.com/en/code-security/secret-scanning)
- [OWASP DVWA](https://github.com/digininja/DVWA) - Test dataset
- [OSV Database](https://osv.dev) - Dependency vulnerability mapping

## License

MIT

## Contributing

Community contributions welcome! See CONTRIBUTING.md for guidelines.
