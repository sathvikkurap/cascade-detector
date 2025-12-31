"""Core scanner for secret detection."""

import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, UTC
import math
from cascade_detector.core.patterns import get_all_patterns


class SecretScanner:
    """Scanner for detecting secrets in code."""

    def __init__(self, entropy_threshold: float = 7.5):
        """Initialize secret scanner.
        
        Args:
            entropy_threshold: Entropy threshold for flagging (bits/char)
        """
        self.patterns = get_all_patterns()
        self.entropy_threshold = entropy_threshold
        self.compiled_patterns = {
            name: re.compile(pattern, re.MULTILINE | re.IGNORECASE)
            for name, pattern in self.patterns.items()
        }

    def scan_content(self, content: str, source: str = "") -> List[Dict]:
        """Scan content for secrets.
        
        Args:
            content: Text content to scan
            source: Source identifier (file path, etc.)
            
        Returns:
            List of findings
        """
        findings = []
        
        for pattern_name, regex in self.compiled_patterns.items():
            for match in regex.finditer(content):
                # Calculate entropy
                secret_value = match.group(0)
                entropy = self.calculate_entropy(secret_value)
                
                # Get line number
                line_num = content[:match.start()].count('\n') + 1
                
                finding = {
                    "pattern": pattern_name,
                    "matched_text": secret_value[:50] + "..." if len(secret_value) > 50 else secret_value,
                    "source": source,
                    "line": line_num,
                    "start": match.start(),
                    "end": match.end(),
                    "entropy": entropy,
                    "entropy_flagged": entropy > self.entropy_threshold,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                
                findings.append(finding)
        
        return findings

    @staticmethod
    def calculate_entropy(text: str) -> float:
        """Calculate Shannon entropy of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Entropy in bits/character
        """
        if not text:
            return 0.0
        
        # Count character frequencies
        frequency = {}
        for char in text:
            frequency[char] = frequency.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        for count in frequency.values():
            prob = count / len(text)
            entropy -= prob * math.log2(prob)
        
        return entropy

    def filter_findings(
        self,
        findings: List[Dict],
        min_entropy: Optional[float] = None,
        patterns: Optional[List[str]] = None,
    ) -> List[Dict]:
        """Filter findings by criteria.
        
        Args:
            findings: List of findings
            min_entropy: Minimum entropy threshold
            patterns: Pattern names to include
            
        Returns:
            Filtered findings
        """
        filtered = findings
        
        if min_entropy is not None:
            filtered = [f for f in filtered if f["entropy"] >= min_entropy]
        
        if patterns:
            filtered = [f for f in filtered if f["pattern"] in patterns]
        
        return filtered

    def deduplicate_findings(self, findings: List[Dict]) -> List[Dict]:
        """Remove duplicate findings.
        
        Args:
            findings: List of findings
            
        Returns:
            Deduplicated findings
        """
        seen = set()
        deduplicated = []
        
        for finding in findings:
            # Use pattern + matched text as key
            key = (finding["pattern"], finding["matched_text"])
            if key not in seen:
                seen.add(key)
                deduplicated.append(finding)
        
        return deduplicated
