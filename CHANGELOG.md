# Changelog

All notable changes to Cascade Detector will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup and core architecture
- Discovery agent with 500+ secret patterns
- Propagation agent for dependency and fork graph mapping
- Verifier agent for secret liveness validation
- Remediator agent for automated patch generation
- CLI interface with comprehensive commands
- Configuration management system
- Unit tests for all components
- GitHub Actions CI/CD pipeline
- Documentation and contribution guidelines

## [0.1.0] - 2025-12-30

### Added
- **Discovery Agent**: Pattern-based and LLM-enhanced secret detection
  - 500+ regex patterns from TruffleHog
  - Entropy scoring (Shannon entropy calculation)
  - Git history scanning
  - Dependency lockfile analysis
  
- **Propagation Agent**: Cascade mapping through dependencies and forks
  - NetworkX-based graph construction
  - Dependency tree parsing (npm, Python, etc.)
  - Fork relationship tracking
  - BFS traversal for transitive dependencies
  
- **Verifier Agent**: Liveness validation for discovered secrets
  - Masked verification endpoints (AWS STS, GitHub API, etc.)
  - Multi-provider consensus checking
  - Timeout-safe HTTP checks
  
- **Remediator Agent**: Automated remediation patch generation
  - Environment variable replacement
  - Git apply compatibility
  - Secret rotation scripts
  - PR description generation
  
- **CLI Interface**:
  - `cascade-detector scan`: Repository scanning
  - `cascade-detector config`: Configuration management
  - `cascade-detector verify`: Dependency verification
  
- **Core Modules**:
  - Pattern database with 13 secret categories
  - Ollama LLM integration
  - NetworkX graph utilities
  - Configuration system
  
- **Testing**:
  - Comprehensive unit tests
  - Test fixtures and utilities
  - Coverage reporting
  
- **Documentation**:
  - README with quick start guide
  - CONTRIBUTING guidelines
  - Configuration examples
  - Architecture documentation

### Known Limitations
- LLM analysis requires local Ollama instance
- Dependency parsing limited to common formats
- GitHub API requires authentication for fork traversal
- Secret verification is non-destructive but may trigger rate limits

## Future Roadmap

### Phase 2: Graph + Propagation (Q1 2026)
- Enhanced fork network mapping
- Transitive dependency visualization
- GIF demo generation
- GitHub integration improvements

### Phase 3: Verify + Remediate (Q2 2026)
- Docker sandbox verification
- GitHub App for auto-PRs
- VS Code extension
- Enhanced remediation templates

### Phase 4: Production (Q3 2026)
- Full GitHub Actions integration
- Benchmark suite
- Community plugins
- Advanced reporting

---

For more details, visit the [GitHub repository](https://github.com/yourusername/cascade-detector).
