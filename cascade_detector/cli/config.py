"""Configuration management for Cascade Detector."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


class Config:
    """Configuration handler."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to config.yaml file
        """
        self.config_path = config_path or self._find_config()
        self.config = self._load_config()

    def _find_config(self) -> str:
        """Find configuration file."""
        # Check current directory
        if Path("config.yaml").exists():
            return "config.yaml"
        
        # Check parent directories
        for parent in Path.cwd().parents:
            if (parent / "config.yaml").exists():
                return str(parent / "config.yaml")
        
        # Return default path
        return str(Path(__file__).parent.parent.parent / "config.yaml")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not Path(self.config_path).exists():
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading config from {self.config_path}: {e}")
            return self._get_default_config()

    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "scanner": {
                "max_depth": 5,
                "entropy_threshold": 7.5,
                "verification_timeout": 5,
                "max_commits": 10000,
            },
            "llm": {
                "provider": "ollama",
                "model": "mistral",
                "base_url": "http://localhost:11434",
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 1024,
            },
            "agents": {
                "discovery": {
                    "enabled": True,
                    "pattern_count": 500,
                    "entropy_check": True,
                    "llm_analysis": True,
                },
                "propagation": {
                    "enabled": True,
                    "transitive_deps": True,
                    "include_forks": True,
                    "max_depth": 5,
                },
                "verifier": {
                    "enabled": True,
                    "require_consensus": True,
                    "min_confidence": 0.8,
                },
                "remediator": {
                    "enabled": True,
                    "test_patch": True,
                    "run_lint": True,
                    "require_approval": True,
                },
            },
            "output": {
                "formats": ["json", "html", "mermaid"],
                "directory": "./reports",
                "include_evidence": True,
                "include_hashes": True,
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key.
        
        Args:
            key: Configuration key (e.g., "scanner.entropy_threshold")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot-separated key.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        keys = key.split(".")
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dict."""
        return self.config.copy()

    def save(self, path: Optional[str] = None) -> None:
        """Save configuration to file.
        
        Args:
            path: Output path (uses self.config_path if not provided)
        """
        output_path = path or self.config_path
        with open(output_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)


# Global configuration instance
_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """Get global configuration instance.
    
    Args:
        config_path: Path to config file (only used for first call)
        
    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config
