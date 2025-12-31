# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in Cascade Detector, please **do not** open a public GitHub issue. Instead, please report it responsibly to us at [skurap@uw.edu](mailto:skurap@uw.edu).

### How to Report

1. Email [skurap@uw.edu](mailto:skurap@uw.edu) with the subject "Security Vulnerability Report"
2. Include a clear description of the vulnerability
3. Provide steps to reproduce if possible
4. Do not disclose the vulnerability publicly until we've had time to address it

### What to Expect

- We will acknowledge your report within 48 hours
- We will provide a timeline for fixes
- You will be credited in security advisories if you wish
- We will keep you updated on the progress

## Supported Versions

| Version | Supported          | End of Life |
|---------|-------------------|-------------|
| 1.0.x   | ✅ Yes            | Jan 2027    |
| < 1.0   | ❌ No             | N/A         |

## Security Best Practices

When using Cascade Detector:

1. **Keep it updated**: Always use the latest version for security patches
2. **Protect credentials**: Never commit API keys or secrets to version control
3. **Use environment variables**: Store sensitive data in environment variables or secure vaults
4. **Review outputs carefully**: Always review detection results before taking action
5. **Test in staging first**: Test remediation features in non-production environments

## Dependencies

We regularly audit our dependencies for security vulnerabilities. You can check the security status by reviewing the [dependencies](./pyproject.toml).

## Security Advisories

Security advisories and patch releases will be announced on:
- GitHub Releases (https://github.com/sathvikkurap/cascade-detector/releases)
- GitHub Security Advisories (https://github.com/sathvikkurap/cascade-detector/security/advisories)

## PGP Key

For highly sensitive security reports, you may encrypt your email using PGP. Contact us at [skurap@uw.edu](mailto:skurap@uw.edu) to request our public key.

Thank you for helping keep Cascade Detector secure!
