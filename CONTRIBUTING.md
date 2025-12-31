# Contributing to Cascade Detector

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful of others and follow our Code of Conduct in all interactions.

## How to Contribute

### Reporting Bugs

Report bugs by creating a GitHub issue. Include:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Error messages and stack traces

### Suggesting Enhancements

Suggest enhancements via GitHub issues. Include:
- Clear description of the enhancement
- Use cases and benefits
- Possible implementation approach

### Code Contributions

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make changes** with clear commits
4. **Write/update tests** for your changes
5. **Update documentation** as needed
6. **Submit a pull request** with a clear description

## Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/cascade-detector.git
cd cascade-detector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Set up Ollama
docker pull ollama/ollama
docker run -d -p 11434:11434 ollama/ollama
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_discovery.py -v

# Run with coverage
pytest tests/ --cov=cascade_detector --cov-report=html
```

### Code Quality

```bash
# Format code
black cascade_detector

# Check formatting
black --check cascade_detector

# Lint code
flake8 cascade_detector

# Type checking
mypy cascade_detector

# Security check
bandit -r cascade_detector
```

### Documentation

- Update README.md for user-facing changes
- Add docstrings to all functions and classes
- Update CHANGELOG.md for significant changes

## Standards

### Code Style

- Follow PEP 8 style guide
- Use type hints for all functions
- Maximum line length: 100 characters
- Use descriptive variable and function names

### Commit Messages

- Use clear, concise messages
- Start with a verb (Add, Fix, Update, etc.)
- Reference issue numbers when applicable
- Example: `Fix: resolve entropy calculation bug (fixes #123)`

### Pull Request Process

1. Update documentation
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers
6. Address feedback promptly

## Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Enhancement
- [ ] Documentation update

## Related Issues
Fixes #(issue number)

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No new warnings generated
```

## Recognition

Contributors will be:
- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Recognized in project documentation

## Questions?

- Open an issue for questions
- Check existing discussions
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to making Cascade Detector better!
