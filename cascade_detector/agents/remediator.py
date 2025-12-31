"""Remediator agent for generating remediation patches and PRs."""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, UTC
from cascade_detector.core.llm import OllamaLLM


class RemediationPatch:
    """Represents a remediation patch."""

    def __init__(
        self,
        file_path: str,
        original_content: str,
        patched_content: str,
        secret_type: str,
        pattern: str,
    ):
        """Initialize remediation patch.
        
        Args:
            file_path: Path to file being patched
            original_content: Original file content
            patched_content: Patched file content
            secret_type: Type of secret being remediated
            pattern: Pattern that matched the secret
        """
        self.file_path = file_path
        self.original_content = original_content
        self.patched_content = patched_content
        self.secret_type = secret_type
        self.pattern = pattern
        self.diff = self._generate_diff()

    def _generate_diff(self) -> str:
        """Generate unified diff of the patch."""
        import difflib
        
        original_lines = self.original_content.split('\n')
        patched_lines = self.patched_content.split('\n')
        
        diff = difflib.unified_diff(
            original_lines,
            patched_lines,
            fromfile=self.file_path,
            tofile=self.file_path,
            lineterm='',
        )
        
        return '\n'.join(diff)


class RemediatorAgent:
    """Agent responsible for generating remediation patches and PRs."""

    def __init__(
        self,
        llm: Optional[OllamaLLM] = None,
        test_patch: bool = True,
        run_lint: bool = True,
    ):
        """Initialize Remediator agent.
        
        Args:
            llm: OllamaLLM instance for generating patches
            test_patch: Whether to test patches with git apply
            run_lint: Whether to run linting on patched files
        """
        self.llm = llm or OllamaLLM()
        self.test_patch = test_patch
        self.run_lint = run_lint
        self.patches: List[RemediationPatch] = []

    def generate_patch(
        self,
        file_content: str,
        file_path: str,
        secret_match: Dict,
    ) -> Optional[RemediationPatch]:
        """Generate a remediation patch for a secret.
        
        Args:
            file_content: Original file content
            file_path: Path to file
            secret_match: Dict with pattern, matched_text, line, etc.
            
        Returns:
            RemediationPatch or None if generation fails
        """
        secret_type = secret_match.get("pattern", "api_key")
        pattern = secret_match.get("matched_text", "")
        
        # Replace hardcoded secret with environment variable reference
        patched_content = self._apply_remediation(
            file_content,
            pattern,
            secret_type,
        )
        
        # If LLM is available and basic replacement didn't work, try LLM
        if self.llm and patched_content == file_content:
            try:
                remediation_code = self.llm.generate_remediation(secret_type, file_content)
                patched_content = remediation_code
            except Exception:
                # LLM failed, use basic replacement
                pass
        
        patch = RemediationPatch(
            file_path=file_path,
            original_content=file_content,
            patched_content=patched_content,
            secret_type=secret_type,
            pattern=pattern,
        )
        
        self.patches.append(patch)
        return patch

    def _apply_remediation(
        self,
        content: str,
        pattern: str,
        secret_type: str,
    ) -> str:
        """Apply basic remediation by replacing secret with env var.
        
        Args:
            content: File content
            pattern: Pattern to replace
            secret_type: Type of secret
            
        Returns:
            Patched content
        """
        import re
        
        # Determine env var name
        env_var_name = self._get_env_var_name(secret_type)
        
        # Find the assignment or usage context
        # Pattern: KEY = "value" or KEY=value or KEY: "value"
        
        # Simple case: API_KEY = "abc..." -> API_KEY = os.getenv("API_KEY")
        if secret_type == "api_key" or "api" in secret_type.lower():
            patched = re.sub(
                r'([A-Z_]+_KEY|[A-Z_]+_SECRET|[A-Z_]+_TOKEN)\s*=\s*["\']?[A-Za-z0-9_\-]+["\']?',
                rf'\1 = os.getenv("{env_var_name}")',
                content,
                count=1,
            )
            return patched
        
        # Default: just remove the pattern
        return content.replace(pattern, f'os.getenv("{env_var_name}")')

    @staticmethod
    def _get_env_var_name(secret_type: str) -> str:
        """Get environment variable name for secret type.
        
        Args:
            secret_type: Type of secret
            
        Returns:
            Environment variable name
        """
        type_map = {
            "aws_access_key": "AWS_ACCESS_KEY_ID",
            "aws_secret_key": "AWS_SECRET_ACCESS_KEY",
            "github_token": "GITHUB_TOKEN",
            "api_key": "API_KEY",
            "api_secret": "API_SECRET",
            "database_password": "DB_PASSWORD",
            "stripe_key": "STRIPE_API_KEY",
        }
        
        return type_map.get(secret_type, secret_type.upper())

    def test_patch(self, patch: RemediationPatch) -> Tuple[bool, str]:
        """Test a patch with git apply.
        
        Args:
            patch: RemediationPatch to test
            
        Returns:
            (success, error_message)
        """
        import subprocess
        import tempfile
        import os
        
        try:
            # Write patch to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as f:
                f.write(patch.diff)
                patch_file = f.name
            
            try:
                # Test with git apply --check
                result = subprocess.run(
                    ["git", "apply", "--check", patch_file],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                
                success = result.returncode == 0
                error = result.stderr if result.returncode != 0 else ""
                
                return success, error
            finally:
                os.unlink(patch_file)
        
        except Exception as e:
            return False, str(e)

    def generate_pr_description(
        self,
        secret_type: str,
        affected_files: List[str],
        confidence: float,
    ) -> str:
        """Generate PR description for remediation.
        
        Args:
            secret_type: Type of secret being remediated
            affected_files: List of affected files
            confidence: Confidence score
            
        Returns:
            PR description markdown
        """
        return f"""# Security Fix: Hardcoded {secret_type} Remediation

## Summary
This PR remediates hardcoded {secret_type}(s) that were detected with {confidence:.1%} confidence.

## Changes
- Replaced hardcoded secrets with environment variable references
- Added example .env configuration
- Updated documentation

## Affected Files
{chr(10).join(f"- `{f}`" for f in affected_files)}

## Testing
- [ ] Verify application runs with new environment variables
- [ ] Check that all secret types are properly configured
- [ ] Run security scan to confirm remediation

## Security Notes
- Ensure all necessary environment variables are set in deployment
- Consider implementing secret rotation policy
- Review git history to ensure no other instances exist

**Generated by Cascade Detector - AI-Powered Secret Scanner**
"""

    def create_rotation_script(self, secret_type: str) -> str:
        """Create a secret rotation script template.
        
        Args:
            secret_type: Type of secret to rotate
            
        Returns:
            Bash script template for rotation
        """
        script_templates = {
            "aws": """#!/bin/bash
# AWS Credential Rotation Script
# Run: bash rotate_aws_credentials.sh

set -e

echo "Starting AWS credential rotation..."

# Step 1: Generate new credentials
aws iam create-access-key --user-name YOUR_USER

# Step 2: Update environment variables
# Edit .env with new credentials
nano .env

# Step 3: Test new credentials
aws sts get-caller-identity

# Step 4: Deactivate old credentials
aws iam update-access-key --access-key-id OLD_KEY_ID --status Inactive --user-name YOUR_USER

# Step 5: Delete old credentials after verification period
# aws iam delete-access-key --access-key-id OLD_KEY_ID --user-name YOUR_USER

echo "AWS credential rotation complete!"
""",
            "github": """#!/bin/bash
# GitHub Token Rotation Script
# Run: bash rotate_github_token.sh

set -e

echo "Starting GitHub token rotation..."

# Step 1: Create new token via GitHub UI
echo "1. Visit https://github.com/settings/tokens/new"
echo "2. Create new personal access token with same scopes"
echo "3. Copy the token"
read -sp "Enter new GitHub token: " NEW_TOKEN

# Step 2: Update environment variable
export GITHUB_TOKEN="$NEW_TOKEN"
echo "export GITHUB_TOKEN='$NEW_TOKEN'" >> .env

# Step 3: Test new token
curl -H "Authorization: token $NEW_TOKEN" https://api.github.com/user

# Step 4: Delete old token from GitHub UI
echo "4. Delete old token from: https://github.com/settings/tokens"

echo "GitHub token rotation complete!"
""",
            "default": """#!/bin/bash
# Secret Rotation Script

set -e

echo "Starting secret rotation..."

# Step 1: Generate new secret
echo "Generate a new secret using your provider's interface"

# Step 2: Update environment variable
# export SECRET_NAME="new_secret_value"
# echo "export SECRET_NAME='new_secret_value'" >> .env

# Step 3: Test new secret
echo "Test the new secret with your application"

# Step 4: Revoke old secret
echo "Revoke the old secret from your provider"

echo "Secret rotation complete!"
""",
        }
        
        key = "default"
        for k in script_templates:
            if k in secret_type.lower():
                key = k
                break
        
        return script_templates[key]

    def generate_remediation_report(self) -> Dict:
        """Generate comprehensive remediation report.
        
        Returns:
            Remediation report dict
        """
        tested_patches = []
        if self.test_patch:
            for patch in self.patches:
                success, error = self.test_patch(patch)
                tested_patches.append({
                    "file": patch.file_path,
                    "success": success,
                    "error": error,
                })
        
        return {
            "summary": {
                "total_patches": len(self.patches),
                "patches_tested": len(tested_patches),
                "patches_passed": sum(1 for p in tested_patches if p["success"]),
                "patches_failed": sum(1 for p in tested_patches if not p["success"]),
            },
            "patches": [
                {
                    "file": p.file_path,
                    "secret_type": p.secret_type,
                    "pattern": p.pattern,
                    "diff": p.diff,
                }
                for p in self.patches
            ],
            "test_results": tested_patches,
            "generated_at": datetime.now(UTC).isoformat(),
        }
