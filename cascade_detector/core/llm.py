"""LLM integration with Ollama."""

import os
from typing import Optional
import ollama


class OllamaLLM:
    """Wrapper for Ollama LLM inference."""

    def __init__(
        self,
        model: str = "mistral",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.3,
        top_p: float = 0.9,
    ):
        """Initialize Ollama LLM client.
        
        Args:
            model: Model name (default: mistral)
            base_url: Ollama server URL
            temperature: Sampling temperature (0-1)
            top_p: Nucleus sampling parameter
        """
        self.model = model
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.temperature = temperature
        self.top_p = top_p
        self.client = ollama.Client(host=self.base_url)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text from prompt using Ollama.
        
        Args:
            prompt: Input prompt
            system_prompt: System prompt for context
            
        Returns:
            Generated text response
        """
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                system=system_prompt,
                stream=False,
                options={
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                },
            )
            return response.get("response", "").strip()
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {e}")

    def analyze_secret_context(self, code_snippet: str, pattern_match: str) -> dict:
        """Analyze code context around secret pattern.
        
        Args:
            code_snippet: Code snippet containing potential secret
            pattern_match: The matched pattern
            
        Returns:
            Analysis dict with confidence and reasoning
        """
        system = """You are a security analyst. Analyze if the following code likely contains a real secret.
        Respond with a JSON object: {"is_likely_secret": bool, "confidence": 0.0-1.0, "reasoning": str}"""

        prompt = f"""Analyze this code for a potential secret match:
        
Pattern match: {pattern_match}

Code context:
```
{code_snippet}
```

Is this likely a real secret? Provide confidence (0-1) and reasoning."""

        response = self.generate(prompt, system)
        try:
            import json
            return json.loads(response)
        except:
            return {
                "is_likely_secret": True,
                "confidence": 0.5,
                "reasoning": response,
            }

    def generate_remediation(self, secret_type: str, code_snippet: str) -> str:
        """Generate remediation code for a secret.
        
        Args:
            secret_type: Type of secret (e.g., "aws_key", "api_key")
            code_snippet: Code containing the secret
            
        Returns:
            Remediation code suggestions
        """
        system = """You are a security engineer. Generate safe code replacements for hardcoded secrets.
        Follow best practices: use environment variables, vaults, or secure config management.
        Provide clear, production-ready code."""

        prompt = f"""Generate a remediation for this hardcoded {secret_type}:

```
{code_snippet}
```

Provide:
1. Replacement code using best practices
2. Required environment variable or config changes
3. Optional rotation script"""

        return self.generate(prompt, system)

    def check_liveness(self) -> bool:
        """Check if Ollama server is alive.
        
        Returns:
            True if server is reachable
        """
        try:
            # Try to list available models
            self.client.list()
            return True
        except:
            return False
