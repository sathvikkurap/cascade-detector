"""Discovery agent for secret detection."""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, UTC
from cascade_detector.core.scanner import SecretScanner
from cascade_detector.core.llm import OllamaLLM
from cascade_detector.core.patterns import PATTERN_GROUPS


class DiscoveryAgent:
    """Agent responsible for discovering secrets in repositories."""

    def __init__(
        self,
        scanner: Optional[SecretScanner] = None,
        llm: Optional[OllamaLLM] = None,
        entropy_threshold: float = 7.5,
        use_llm_analysis: bool = True,
    ):
        """Initialize Discovery agent.
        
        Args:
            scanner: SecretScanner instance
            llm: OllamaLLM instance for context analysis
            entropy_threshold: Entropy threshold for flagging
            use_llm_analysis: Whether to use LLM for context analysis
        """
        self.scanner = scanner or SecretScanner(entropy_threshold=entropy_threshold)
        self.llm = llm
        self.use_llm_analysis = use_llm_analysis and llm is not None
        self.entropy_threshold = entropy_threshold

    def scan_blob(
        self,
        content: str,
        blob_hash: str,
        file_path: str = "",
        context: Dict = None,
    ) -> Dict:
        """Scan a git blob for secrets.
        
        Args:
            content: Blob content
            blob_hash: Git blob hash
            file_path: File path in repository
            context: Additional context (commit, author, etc.)
            
        Returns:
            Scan results dict
        """
        if context is None:
            context = {}
        
        findings = self.scanner.scan_content(content, source=file_path)
        findings = self.scanner.deduplicate_findings(findings)
        
        # Enrich with LLM analysis if enabled
        if self.use_llm_analysis and findings:
            for finding in findings:
                # Get code context around match
                lines = content.split('\n')
                line_idx = finding["line"] - 1
                context_lines = lines[
                    max(0, line_idx - 2) : min(len(lines), line_idx + 3)
                ]
                code_context = '\n'.join(context_lines)
                
                try:
                    analysis = self.llm.analyze_secret_context(
                        code_context,
                        finding["matched_text"],
                    )
                    finding["llm_analysis"] = analysis
                    finding["confidence"] = analysis.get("confidence", 0.5)
                except Exception as e:
                    finding["llm_analysis"] = None
                    finding["confidence"] = 0.5  # Default confidence
        else:
            # Use entropy as confidence proxy
            for finding in findings:
                finding["confidence"] = min(
                    1.0,
                    finding["entropy"] / 10.0,
                )
        
        return {
            "blob_hash": blob_hash,
            "file_path": file_path,
            "findings": findings,
            "total_findings": len(findings),
            "high_confidence_findings": sum(
                1 for f in findings if f.get("confidence", 0) >= 0.8
            ),
            "context": context,
            "scanned_at": datetime.now(UTC).isoformat(),
        }

    def scan_lockfile(
        self,
        content: str,
        file_path: str,
        lockfile_type: str = "unknown",
    ) -> Dict:
        """Scan dependency lockfile for secrets.
        
        Supports: package-lock.json, yarn.lock, poetry.lock, Pipfile.lock, etc.
        
        Args:
            content: Lockfile content
            file_path: File path
            lockfile_type: Type of lockfile
            
        Returns:
            Scan results dict
        """
        findings = self.scanner.scan_content(content, source=file_path)
        
        return {
            "lockfile_path": file_path,
            "lockfile_type": lockfile_type,
            "findings": findings,
            "total_findings": len(findings),
            "scanned_at": datetime.now(UTC).isoformat(),
        }

    def scan_history(
        self,
        commits: List[Dict],
        max_commits: Optional[int] = None,
    ) -> Dict:
        """Scan git history for secrets.
        
        Args:
            commits: List of commit dicts with 'hash', 'message', 'author', 'blobs'
            max_commits: Maximum commits to scan
            
        Returns:
            Scan results dict
        """
        all_findings = []
        scanned_count = 0
        
        for i, commit in enumerate(commits[:max_commits] if max_commits else commits):
            scanned_count += 1
            
            # Process each blob in the commit
            for blob in commit.get("blobs", []):
                result = self.scan_blob(
                    blob["content"],
                    blob.get("hash", ""),
                    blob.get("path", ""),
                    context={
                        "commit_hash": commit["hash"],
                        "commit_message": commit.get("message", ""),
                        "author": commit.get("author", ""),
                        "timestamp": commit.get("timestamp", ""),
                    },
                )
                all_findings.extend(result["findings"])
        
        return {
            "commits_scanned": scanned_count,
            "total_findings": len(all_findings),
            "findings": all_findings,
            "findings_by_pattern": self._group_by_pattern(all_findings),
            "high_confidence_findings": sum(
                1 for f in all_findings if f.get("confidence", 0) >= 0.8
            ),
            "scanned_at": datetime.now(UTC).isoformat(),
        }

    def generate_report(self, scan_results: List[Dict]) -> Dict:
        """Generate comprehensive discovery report.
        
        Args:
            scan_results: List of scan result dicts
            
        Returns:
            Comprehensive report dict
        """
        all_findings = []
        for result in scan_results:
            all_findings.extend(result.get("findings", []))
        
        return {
            "summary": {
                "total_scans": len(scan_results),
                "total_findings": len(all_findings),
                "high_confidence": sum(
                    1 for f in all_findings if f.get("confidence", 0) >= 0.8
                ),
                "medium_confidence": sum(
                    1 for f in all_findings 
                    if 0.5 <= f.get("confidence", 0) < 0.8
                ),
                "low_confidence": sum(
                    1 for f in all_findings if f.get("confidence", 0) < 0.5
                ),
            },
            "findings_by_pattern": self._group_by_pattern(all_findings),
            "findings_by_category": self._group_by_category(all_findings),
            "high_confidence_findings": [
                f for f in all_findings if f.get("confidence", 0) >= 0.8
            ],
            "findings": all_findings,
            "generated_at": datetime.now(UTC).isoformat(),
        }

    @staticmethod
    def _group_by_pattern(findings: List[Dict]) -> Dict[str, int]:
        """Group findings by pattern name."""
        groups = {}
        for finding in findings:
            pattern = finding.get("pattern", "unknown")
            groups[pattern] = groups.get(pattern, 0) + 1
        return groups

    @staticmethod
    def _group_by_category(findings: List[Dict]) -> Dict[str, int]:
        """Group findings by category."""
        groups = {}
        for finding in findings:
            pattern = finding.get("pattern", "unknown")
            # Find which category this pattern belongs to
            category = "unknown"
            for cat, patterns in PATTERN_GROUPS.items():
                if pattern in patterns:
                    category = cat
                    break
            groups[category] = groups.get(category, 0) + 1
        return groups
