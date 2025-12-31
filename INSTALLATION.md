# Installation Guide

## Prerequisites

- **Python**: 3.8 or higher
- **pip**: Package manager (comes with Python)
- **Git**: For cloning the repository
- **OpenAI API Key**: For AI-powered pattern analysis (optional, uses local patterns as fallback)

---

## Quick Install (Recommended)

### 1. Install via pip (Easiest)
```bash
pip install cascade-detector
```

Verify installation:
```bash
cascade-detector --version
```

---

## Development Installation

### 1. Clone the repository
```bash
git clone https://github.com/sathvikkurap/cascade-detector.git
cd cascade-detector
```

### 2. Create virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run tests to verify
```bash
pytest tests/ -v
```

Expected output:
```
24 passed, 3 skipped in 0.35s
```

### 5. Install in development mode
```bash
pip install -e .
```

---

## Platform-Specific Instructions

### macOS
```bash
# Using Homebrew
brew install python3

# Or using conda
conda create -n cascade python=3.10
conda activate cascade

# Then follow Quick Install above
pip install cascade-detector
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip

pip3 install cascade-detector
```

### Linux (Fedora/CentOS)
```bash
sudo dnf install python3 python3-pip

pip3 install cascade-detector
```

### Windows
```powershell
# Using Python installer from python.org
python -m pip install --upgrade pip
pip install cascade-detector
```

---

## Configuration

### OpenAI API Key (Optional)
For enhanced pattern detection, set your OpenAI API key:

```bash
# macOS/Linux
export OPENAI_API_KEY="sk-..."

# Windows
set OPENAI_API_KEY=sk-...
```

Or create `.env` file in your project:
```
OPENAI_API_KEY=sk-...
```

---

## Verification

### 1. Test command-line interface
```bash
cascade-detector --help
```

Should show available commands and options.

### 2. Run on sample code
```bash
cascade-detector scan /path/to/repo
```

### 3. Full test suite
```bash
# If installed from source
pytest tests/ -v

# Should show:
# 24 passed, 3 skipped in 0.35s
```

---

## Upgrading

### Update pip version
```bash
pip install --upgrade cascade-detector
```

### Update from source
```bash
cd cascade-detector
git pull origin main
pip install -r requirements.txt
```

---

## Troubleshooting

### Issue: "command not found: cascade-detector"
**Solution**:
```bash
# Verify pip installation
pip list | grep cascade-detector

# If not listed, reinstall
pip install --force-reinstall cascade-detector

# Or use python module
python -m cascade_detector
```

### Issue: "ModuleNotFoundError"
**Solution**:
```bash
# Ensure dependencies installed
pip install -r requirements.txt

# Upgrade pip
pip install --upgrade pip
```

### Issue: "OpenAI API key not found"
**Solution**:
```bash
# Set environment variable
export OPENAI_API_KEY="your-key-here"

# Or create .env file
echo 'OPENAI_API_KEY="your-key-here"' > .env
```

### Issue: Tests failing
**Solution**:
```bash
# Update packages
pip install --upgrade -r requirements.txt

# Run tests with verbose output
pytest tests/ -v --tb=short

# Check Python version (must be 3.8+)
python --version
```

---

## Next Steps

1. Read [QUICKSTART.md](QUICKSTART.md) for 5-minute quick start
2. Try basic scan: `cascade-detector scan .`
3. Read [README.md](README.md) for full documentation
4. Check [API_COVERAGE_REPORT.md](API_COVERAGE_REPORT.md) for supported patterns

---

## Getting Help

- **Issues**: https://github.com/sathvikkurap/cascade-detector/issues
- **Discussions**: https://github.com/sathvikkurap/cascade-detector/discussions
- **Documentation**: See [README.md](README.md)

---

**Status**: ✅ Installation guide verified and tested
