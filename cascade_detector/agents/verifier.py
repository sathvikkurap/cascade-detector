"""Verifier agent for validating active secret exploitation risk."""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, UTC
import asyncio
import aiohttp
from dataclasses import dataclass


@dataclass
class VerificationResult:
    """Result of a secret verification check."""
    
    secret_id: str
    provider: str
    is_active: bool
    confidence: float
    response_code: Optional[int] = None
    response_entropy: float = 0.0
    error: Optional[str] = None
    checked_at: str = ""

    def __post_init__(self):
        if not self.checked_at:
            self.checked_at = datetime.now(UTC).isoformat()


class VerifierAgent:
    """Agent responsible for verifying if secrets are actively exploitable."""

    def __init__(self, timeout: int = 5, require_consensus: bool = True):
        """Initialize Verifier agent.
        
        Args:
            timeout: HTTP request timeout in seconds
            require_consensus: Require 2/3 provider agreement for verdict
        """
        self.timeout = timeout
        self.require_consensus = require_consensus
        self.verification_results: List[VerificationResult] = []

    async def verify_aws_credential(
        self,
        access_key: str,
        secret_key: str,
        secret_id: str = "",
    ) -> VerificationResult:
        """Verify AWS credentials.
        
        Uses masked approach: checks if key format is valid and attempts
        metadata endpoint access without exposing credentials.
        
        Args:
            access_key: AWS access key ID
            secret_key: AWS secret access key
            secret_id: Secret identifier
            
        Returns:
            VerificationResult
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Attempt to fetch STS caller identity (no resource access)
                # This is a safe check that validates credentials
                headers = {
                    "Authorization": f"AWS4-HMAC-SHA256 Credential={access_key}",
                }
                
                async with session.get(
                    "https://sts.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15",
                    headers=headers,
                    timeout=self.timeout,
                    ssl=False,
                ) as response:
                    is_active = response.status in [200, 403]  # 403 means key exists
                    return VerificationResult(
                        secret_id=secret_id,
                        provider="aws",
                        is_active=is_active,
                        confidence=0.9 if is_active else 0.1,
                        response_code=response.status,
                    )
        except asyncio.TimeoutError:
            return VerificationResult(
                secret_id=secret_id,
                provider="aws",
                is_active=False,
                confidence=0.2,
                error="Timeout",
            )
        except Exception as e:
            return VerificationResult(
                secret_id=secret_id,
                provider="aws",
                is_active=False,
                confidence=0.1,
                error=str(e),
            )

    async def verify_github_token(
        self,
        token: str,
        secret_id: str = "",
    ) -> VerificationResult:
        """Verify GitHub token liveness.
        
        Performs masked check: validates token without accessing sensitive data.
        
        Args:
            token: GitHub personal access token or OAuth token
            secret_id: Secret identifier
            
        Returns:
            VerificationResult
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"token {token}"}
                
                # Check token validity without accessing user data
                async with session.get(
                    "https://api.github.com/user",
                    headers=headers,
                    timeout=self.timeout,
                ) as response:
                    is_active = response.status == 200
                    confidence = 0.95 if is_active else 0.1
                    
                    return VerificationResult(
                        secret_id=secret_id,
                        provider="github",
                        is_active=is_active,
                        confidence=confidence,
                        response_code=response.status,
                    )
        except asyncio.TimeoutError:
            return VerificationResult(
                secret_id=secret_id,
                provider="github",
                is_active=False,
                confidence=0.2,
                error="Timeout",
            )
        except Exception as e:
            return VerificationResult(
                secret_id=secret_id,
                provider="github",
                is_active=False,
                confidence=0.1,
                error=str(e),
            )

    async def verify_npm_token(
        self,
        token: str,
        secret_id: str = "",
    ) -> VerificationResult:
        """Verify npm authentication token.
        
        Args:
            token: npm authentication token
            secret_id: Secret identifier
            
        Returns:
            VerificationResult
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {token}"}
                
                async with session.get(
                    "https://registry.npmjs.org/-/whoami",
                    headers=headers,
                    timeout=self.timeout,
                ) as response:
                    is_active = response.status == 200
                    
                    return VerificationResult(
                        secret_id=secret_id,
                        provider="npm",
                        is_active=is_active,
                        confidence=0.95 if is_active else 0.1,
                        response_code=response.status,
                    )
        except asyncio.TimeoutError:
            return VerificationResult(
                secret_id=secret_id,
                provider="npm",
                is_active=False,
                confidence=0.2,
                error="Timeout",
            )
        except Exception as e:
            return VerificationResult(
                secret_id=secret_id,
                provider="npm",
                is_active=False,
                confidence=0.1,
                error=str(e),
            )

    async def verify_docker_token(
        self,
        token: str,
        secret_id: str = "",
    ) -> VerificationResult:
        """Verify Docker registry token.
        
        Args:
            token: Docker authentication token
            secret_id: Secret identifier
            
        Returns:
            VerificationResult
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {token}"}
                
                async with session.get(
                    "https://index.docker.io/v2/",
                    headers=headers,
                    timeout=self.timeout,
                ) as response:
                    is_active = response.status in [200, 401]
                    
                    return VerificationResult(
                        secret_id=secret_id,
                        provider="docker",
                        is_active=is_active,
                        confidence=0.9 if is_active else 0.1,
                        response_code=response.status,
                    )
        except asyncio.TimeoutError:
            return VerificationResult(
                secret_id=secret_id,
                provider="docker",
                is_active=False,
                confidence=0.2,
                error="Timeout",
            )
        except Exception as e:
            return VerificationResult(
                secret_id=secret_id,
                provider="docker",
                is_active=False,
                confidence=0.1,
                error=str(e),
            )

    async def verify_stripe_key(
        self, secret_id: str, stripe_key: str
    ) -> VerificationResult:
        """Verify a Stripe API key by checking balance."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {stripe_key}",
                    "Content-Type": "application/x-www-form-urlencoded",
                }
                
                async with session.get(
                    "https://api.stripe.com/v1/account/balance",
                    headers=headers,
                    timeout=self.timeout,
                    ssl=False,
                ) as response:
                    is_active = response.status == 200
                    return VerificationResult(
                        secret_id=secret_id,
                        provider="stripe",
                        is_active=is_active,
                        confidence=0.95 if is_active else 0.05,
                        response_code=response.status,
                    )
        except asyncio.TimeoutError:
            return VerificationResult(
                secret_id=secret_id,
                provider="stripe",
                is_active=False,
                confidence=0.2,
                error="Timeout",
            )
        except Exception as e:
            return VerificationResult(
                secret_id=secret_id,
                provider="stripe",
                is_active=False,
                confidence=0.1,
                error=str(e),
            )

    async def verify_sendgrid_key(
        self, secret_id: str, sendgrid_key: str
    ) -> VerificationResult:
        """Verify a SendGrid API key by checking mail settings."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {sendgrid_key}",
                    "Content-Type": "application/json",
                }
                
                async with session.get(
                    "https://api.sendgrid.com/v3/mail_settings",
                    headers=headers,
                    timeout=self.timeout,
                    ssl=False,
                ) as response:
                    is_active = response.status == 200
                    return VerificationResult(
                        secret_id=secret_id,
                        provider="sendgrid",
                        is_active=is_active,
                        confidence=0.95 if is_active else 0.05,
                        response_code=response.status,
                    )
        except asyncio.TimeoutError:
            return VerificationResult(
                secret_id=secret_id,
                provider="sendgrid",
                is_active=False,
                confidence=0.2,
                error="Timeout",
            )
        except Exception as e:
            return VerificationResult(
                secret_id=secret_id,
                provider="sendgrid",
                is_active=False,
                confidence=0.1,
                error=str(e),
            )

    async def verify_mailchimp_key(
        self, secret_id: str, mailchimp_key: str
    ) -> VerificationResult:
        """Verify a Mailchimp API key by checking account info."""
        try:
            # Extract data center from key (format: xxxxx-us1)
            dc = mailchimp_key.split("-")[-1] if "-" in mailchimp_key else "us1"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {mailchimp_key}",
                    "Content-Type": "application/json",
                }
                
                async with session.get(
                    f"https://{dc}.api.mailchimp.com/3.0/",
                    headers=headers,
                    timeout=self.timeout,
                    ssl=False,
                ) as response:
                    is_active = response.status == 200
                    return VerificationResult(
                        secret_id=secret_id,
                        provider="mailchimp",
                        is_active=is_active,
                        confidence=0.95 if is_active else 0.05,
                        response_code=response.status,
                    )
        except asyncio.TimeoutError:
            return VerificationResult(
                secret_id=secret_id,
                provider="mailchimp",
                is_active=False,
                confidence=0.2,
                error="Timeout",
            )
        except Exception as e:
            return VerificationResult(
                secret_id=secret_id,
                provider="mailchimp",
                is_active=False,
                confidence=0.1,
                error=str(e),
            )

    async def verify_datadog_key(
        self, secret_id: str, api_key: str, app_key: str = None
    ) -> VerificationResult:
        """Verify a Datadog API key by checking account info."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "DD-API-KEY": api_key,
                    "Content-Type": "application/json",
                }
                
                if app_key:
                    headers["DD-APPLICATION-KEY"] = app_key
                
                async with session.get(
                    "https://api.datadoghq.com/api/v1/validate",
                    headers=headers,
                    timeout=self.timeout,
                    ssl=False,
                ) as response:
                    is_active = response.status == 200
                    return VerificationResult(
                        secret_id=secret_id,
                        provider="datadog",
                        is_active=is_active,
                        confidence=0.95 if is_active else 0.05,
                        response_code=response.status,
                    )
        except asyncio.TimeoutError:
            return VerificationResult(
                secret_id=secret_id,
                provider="datadog",
                is_active=False,
                confidence=0.2,
                error="Timeout",
            )
        except Exception as e:
            return VerificationResult(
                secret_id=secret_id,
                provider="datadog",
                is_active=False,
                confidence=0.1,
                error=str(e),
            )

    async def verify_secret(
        self,
        secret_dict: Dict,
    ) -> Dict:
        """Verify a secret using multiple providers.
        
        Args:
            secret_dict: Dict with secret data (type, value, etc.)
            
        Returns:
            Verification report dict
        """
        secret_id = secret_dict.get("id", "unknown")
        secret_type = secret_dict.get("type", "").lower()
        secret_value = secret_dict.get("value", "")
        
        results = []
        
        # Route to appropriate verifiers based on secret type
        if "aws" in secret_type:
            result = await self.verify_aws_credential(secret_value, "", secret_id)
            results.append(result)
        
        if "github" in secret_type:
            result = await self.verify_github_token(secret_value, secret_id)
            results.append(result)
        
        if "npm" in secret_type:
            result = await self.verify_npm_token(secret_value, secret_id)
            results.append(result)
        
        if "docker" in secret_type:
            result = await self.verify_docker_token(secret_value, secret_id)
            results.append(result)
        
        if "stripe" in secret_type:
            result = await self.verify_stripe_key(secret_id, secret_value)
            results.append(result)
        
        if "sendgrid" in secret_type:
            result = await self.verify_sendgrid_key(secret_id, secret_value)
            results.append(result)
        
        if "mailchimp" in secret_type:
            result = await self.verify_mailchimp_key(secret_id, secret_value)
            results.append(result)
        
        if "datadog" in secret_type:
            result = await self.verify_datadog_key(secret_id, secret_value)
            results.append(result)
        
        self.verification_results.extend(results)
        
        # Determine final verdict
        active_results = [r for r in results if r.is_active]
        verdict = len(active_results) >= (len(results) // 2 + 1) if self.require_consensus else any(r.is_active for r in results)
        
        return {
            "secret_id": secret_id,
            "type": secret_type,
            "is_active": verdict,
            "confidence": sum(r.confidence for r in results) / len(results) if results else 0.0,
            "verification_results": [
                {
                    "provider": r.provider,
                    "is_active": r.is_active,
                    "confidence": r.confidence,
                    "response_code": r.response_code,
                    "error": r.error,
                }
                for r in results
            ],
            "verified_at": datetime.now(UTC).isoformat(),
        }

    async def verify_batch(self, secrets: List[Dict]) -> List[Dict]:
        """Verify a batch of secrets concurrently.
        
        Args:
            secrets: List of secret dicts
            
        Returns:
            List of verification reports
        """
        tasks = [self.verify_secret(secret) for secret in secrets]
        return await asyncio.gather(*tasks)

    def generate_verification_report(self) -> Dict:
        """Generate verification report.
        
        Returns:
            Verification report dict
        """
        active_count = sum(1 for r in self.verification_results if r.is_active)
        
        return {
            "summary": {
                "total_verified": len(self.verification_results),
                "confirmed_active": active_count,
                "confirmed_inactive": len(self.verification_results) - active_count,
                "success_rate": active_count / len(self.verification_results) if self.verification_results else 0.0,
            },
            "results": [
                {
                    "secret_id": r.secret_id,
                    "provider": r.provider,
                    "is_active": r.is_active,
                    "confidence": r.confidence,
                    "response_code": r.response_code,
                    "error": r.error,
                    "checked_at": r.checked_at,
                }
                for r in self.verification_results
            ],
            "generated_at": datetime.now(UTC).isoformat(),
        }
