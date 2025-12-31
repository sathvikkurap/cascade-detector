"""Core patterns from TruffleHog (500+ secret patterns)."""

# AWS patterns
AWS_PATTERNS = {
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "aws_secret_key": r"aws_secret_access_key\s*=\s*['\"]?[A-Za-z0-9/+=]{40}['\"]?",
    "aws_mfa_device": r"arn:aws:iam::\d{12}:mfa/[A-Za-z0-9_-]+",
}

# GitHub patterns
GITHUB_PATTERNS = {
    "github_token": r"gh[a-z]{2}_[A-Za-z0-9_]{36,255}",
    "github_pat": r"ghp_[A-Za-z0-9_]{36,255}",
    "github_oauth": r"gho_[A-Za-z0-9_]{36,255}",
    "github_app_token": r"ghu_[A-Za-z0-9_]{36,255}",
    "github_refresh_token": r"ghr_[A-Za-z0-9_]{36,255}",
}

# API Key patterns
API_KEY_PATTERNS = {
    "api_key": r"[Aa][Pp][Ii][_-]?[Kk][Ee][Yy]\s*[=:]\s*['\"]?[A-Za-z0-9_-]{20,}['\"]?",
    "api_secret": r"[Aa][Pp][Ii][_-]?[Ss][Ee][Cc][Rr][Ee][Tt]\s*[=:]\s*['\"]?[A-Za-z0-9_-]{20,}['\"]?",
    "secret_key": r"[Ss][Ee][Cc][Rr][Ee][Tt][_-]?[Kk][Ee][Yy]\s*[=:]\s*['\"]?[A-Za-z0-9_-]{20,}['\"]?",
    "access_token": r"[Aa][Cc][Cc][Ee][Ss]{2}[_-]?[Tt][Oo][Kk][Ee][Nn]\s*[=:]\s*['\"]?[A-Za-z0-9_.-]{20,}['\"]?",
}

# Database patterns
DATABASE_PATTERNS = {
    "mongodb_uri": r"mongodb(\+srv)?://[a-zA-Z0-9_:@.\-]+",
    "mysql_password": r"mysql://[a-zA-Z0-9_:@.\-]+",
    "postgres_password": r"postgres(ql)?://[a-zA-Z0-9_:@.\-]+",
    "redis_url": r"redis://[a-zA-Z0-9_:@.\-]+",
    "db_password": r"[Dd][Bb][_-]?[Pp][Aa][Ss]{2}[Ww][Oo][Rr][Dd]\s*[=:]\s*['\"]?[A-Za-z0-9_!@#$%^&*()-]+['\"]?",
}

# Private key patterns
PRIVATE_KEY_PATTERNS = {
    "rsa_private_key": r"-----BEGIN RSA PRIVATE KEY-----",
    "openssh_private_key": r"-----BEGIN OPENSSH PRIVATE KEY-----",
    "pgp_private_key": r"-----BEGIN PGP PRIVATE KEY BLOCK-----",
    "aws_private_key": r"-----BEGIN EC PRIVATE KEY-----",
    "jwt_token": r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
}

# Slack patterns
SLACK_PATTERNS = {
    "slack_bot_token": r"xoxb-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9]{24,34}",
    "slack_user_token": r"xoxp-[0-9]{10,13}-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9]{32}",
    "slack_webhook": r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+",
}

# Google patterns
GOOGLE_PATTERNS = {
    "google_api_key": r"AIza[0-9A-Za-z\-_]{35}",
    "google_oauth_id": r"[0-9]{12,32}-[a-z0-9]{32}\.apps\.googleusercontent\.com",
    "google_service_account": r"\"type\": \"service_account\"",
}

# Stripe patterns
STRIPE_PATTERNS = {
    "stripe_api_key": r"sk_live_[0-9a-zA-Z]{24,}",
    "stripe_restricted_key": r"rk_live_[0-9a-zA-Z]{24,}",
    "stripe_publishable_key": r"pk_live_[0-9a-zA-Z]{24,}",
}

# NPM patterns
NPM_PATTERNS = {
    "npm_token": r"//registry\.npmjs\.org/:_authToken=[A-Za-z0-9_-]+",
    "npm_auth": r"npm_config_registry=https://[a-z0-9\-\.]+",
}

# Twilio patterns
TWILIO_PATTERNS = {
    "twilio_account_sid": r"AC[a-z0-9]{32}",
    "twilio_auth_token": r"SK[a-z0-9]{32}",
}

# Docker patterns
DOCKER_PATTERNS = {
    "docker_registry": r"https://index\.docker\.io/v1/",
    "docker_config": r"\"auths\":\s*{",
}

# Certificate patterns
CERTIFICATE_PATTERNS = {
    "private_key": r"-----BEGIN PRIVATE KEY-----",
    "certificate": r"-----BEGIN CERTIFICATE-----",
}

# Email patterns with context
EMAIL_PATTERNS = {
    "email_with_password": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}['\"]?\s*[=:]\s*['\"][A-Za-z0-9_!@#$%^&*()-]{8,}['\"]",
}

# Databricks patterns
DATABRICKS_PATTERNS = {
    "databricks_token": r"dapi[a-f0-9]{32}",
    "databricks_pat": r"dapi[a-z0-9]{32}",
}

# Slack additional patterns
SLACK_ADDITIONAL = {
    "slack_app_token": r"xapp-[0-9a-zA-Z]{10,50}",
    "slack_oauth_token": r"xox[abpr]-[0-9]{10,13}-[0-9]{10,13}-[0-9a-zA-Z]{32}",
}

# PagerDuty patterns
PAGERDUTY_PATTERNS = {
    "pagerduty_api_key": r"['\"]?[a-zA-Z0-9]{20}['\"]?\s*[=:]\s*pagerduty",
    "pagerduty_token": r"token=[a-zA-Z0-9_\-]{40,}",
}

# SendGrid patterns
SENDGRID_PATTERNS = {
    "sendgrid_api_key": r"SG\.[a-zA-Z0-9_\-]{60,}",
}

# Mailchimp patterns
MAILCHIMP_PATTERNS = {
    "mailchimp_api_key": r"[a-z0-9]{32}-us[0-9]{1,2}",
}

# GitLab patterns
GITLAB_PATTERNS = {
    "gitlab_pat": r"glpat-[a-zA-Z0-9_\-]{20,}",
    "gitlab_token": r"gl[0-9a-zA-Z_\-]{20,}",
    "gitlab_runner_token": r"glrt_[a-zA-Z0-9_\-]{20,}",
}

# Bitbucket patterns
BITBUCKET_PATTERNS = {
    "bitbucket_app_password": r"[a-zA-Z0-9]{32}",  # App password pattern
    "bitbucket_token": r"ey[A-Za-z0-9_\-]{40,}",
}

# Azure patterns
AZURE_PATTERNS = {
    "azure_subscription_id": r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
    "azure_storage_key": r"DefaultEndpointsProtocol=https;AccountName=[a-z0-9]+;AccountKey=[A-Za-z0-9+/]{88}==",
    "azure_cosmos_key": r"['\"]?accountKey['\"]?\s*:\s*['\"]?[A-Za-z0-9+/]{88}==['\"]?",
}

# Algolia patterns
ALGOLIA_PATTERNS = {
    "algolia_app_id": r"[A-Z0-9]{10}",
    "algolia_api_key": r"[a-z0-9]{32}",
    "algolia_admin_key": r"[a-z0-9]{32}",
}

# Segment patterns
SEGMENT_PATTERNS = {
    "segment_write_key": r"[a-z0-9]{32}",
}

# Amplitude patterns
AMPLITUDE_PATTERNS = {
    "amplitude_api_key": r"[a-z0-9]{32}",
}

# New Relic patterns
NEWRELIC_PATTERNS = {
    "newrelic_api_key": r"NRJS-[a-z0-9]{32}",
    "newrelic_license_key": r"[a-z0-9]{40}",
}

# Datadog patterns
DATADOG_PATTERNS = {
    "datadog_api_key": r"[a-f0-9]{32}",
    "datadog_app_key": r"[a-f0-9]{40}",
}

# Sentry patterns
SENTRY_PATTERNS = {
    "sentry_dsn": r"https://[a-f0-9]+@[a-z0-9\-\.]+\.ingest\.sentry\.io/[0-9]+",
    "sentry_token": r"sntrys_[a-z0-9_\-]+",
}

# OAuth2 patterns
OAUTH2_PATTERNS = {
    "oauth_client_id": r"[0-9]{18,}\.apps\.googleusercontent\.com",
    "oauth_client_secret": r"[A-Za-z0-9_\-]{32,}",
    "oauth_refresh_token": r"[A-Za-z0-9_\-\.]{50,}",
}

# API Gateway patterns
APIGW_PATTERNS = {
    "api_key_header": r"x-api-key:\s*[A-Za-z0-9_\-]{32,}",
    "bearer_token": r"Bearer\s+[A-Za-z0-9_\-.]+",
}

# Firebase patterns
FIREBASE_PATTERNS = {
    "firebase_api_key": r"AIza[0-9A-Za-z\-_]{35}",
    "firebase_auth_domain": r"[a-z0-9\-]+\.firebaseapp\.com",
}

# Heroku patterns
HEROKU_PATTERNS = {
    "heroku_api_key": r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
    "heroku_oauth_token": r"[a-f0-9]{32}",
}

# CircleCI patterns
CIRCLECI_PATTERNS = {
    "circleci_token": r"[a-f0-9]{40}",
}

# Travis CI patterns
TRAVISCI_PATTERNS = {
    "travis_token": r"[a-zA-Z0-9]{22}",
}

# Jenkins patterns
JENKINS_PATTERNS = {
    "jenkins_api_token": r"[0-9a-f]{32}",
}

# Combination pattern dictionary
ALL_PATTERNS = {
    **AWS_PATTERNS,
    **GITHUB_PATTERNS,
    **API_KEY_PATTERNS,
    **DATABASE_PATTERNS,
    **PRIVATE_KEY_PATTERNS,
    **SLACK_PATTERNS,
    **GOOGLE_PATTERNS,
    **STRIPE_PATTERNS,
    **NPM_PATTERNS,
    **TWILIO_PATTERNS,
    **DOCKER_PATTERNS,
    **CERTIFICATE_PATTERNS,
    **EMAIL_PATTERNS,
    **DATABRICKS_PATTERNS,
    **SLACK_ADDITIONAL,
    **PAGERDUTY_PATTERNS,
    **SENDGRID_PATTERNS,
    **MAILCHIMP_PATTERNS,
    **GITLAB_PATTERNS,
    **BITBUCKET_PATTERNS,
    **AZURE_PATTERNS,
    **ALGOLIA_PATTERNS,
    **SEGMENT_PATTERNS,
    **AMPLITUDE_PATTERNS,
    **NEWRELIC_PATTERNS,
    **DATADOG_PATTERNS,
    **SENTRY_PATTERNS,
    **OAUTH2_PATTERNS,
    **APIGW_PATTERNS,
    **FIREBASE_PATTERNS,
    **HEROKU_PATTERNS,
    **CIRCLECI_PATTERNS,
    **TRAVISCI_PATTERNS,
    **JENKINS_PATTERNS,
}

# Pattern groups for categorization
PATTERN_GROUPS = {
    "aws": list(AWS_PATTERNS.keys()),
    "github": list(GITHUB_PATTERNS.keys()),
    "api_keys": list(API_KEY_PATTERNS.keys()),
    "database": list(DATABASE_PATTERNS.keys()),
    "private_keys": list(PRIVATE_KEY_PATTERNS.keys()),
    "slack": list(SLACK_PATTERNS.keys()) + list(SLACK_ADDITIONAL.keys()),
    "google": list(GOOGLE_PATTERNS.keys()),
    "stripe": list(STRIPE_PATTERNS.keys()),
    "npm": list(NPM_PATTERNS.keys()),
    "twilio": list(TWILIO_PATTERNS.keys()),
    "docker": list(DOCKER_PATTERNS.keys()),
    "certificates": list(CERTIFICATE_PATTERNS.keys()),
    "email": list(EMAIL_PATTERNS.keys()),
    "databricks": list(DATABRICKS_PATTERNS.keys()),
    "pagerduty": list(PAGERDUTY_PATTERNS.keys()),
    "sendgrid": list(SENDGRID_PATTERNS.keys()),
    "mailchimp": list(MAILCHIMP_PATTERNS.keys()),
    "gitlab": list(GITLAB_PATTERNS.keys()),
    "bitbucket": list(BITBUCKET_PATTERNS.keys()),
    "azure": list(AZURE_PATTERNS.keys()),
    "algolia": list(ALGOLIA_PATTERNS.keys()),
    "segment": list(SEGMENT_PATTERNS.keys()),
    "amplitude": list(AMPLITUDE_PATTERNS.keys()),
    "newrelic": list(NEWRELIC_PATTERNS.keys()),
    "datadog": list(DATADOG_PATTERNS.keys()),
    "sentry": list(SENTRY_PATTERNS.keys()),
    "oauth2": list(OAUTH2_PATTERNS.keys()),
    "api_gateway": list(APIGW_PATTERNS.keys()),
    "firebase": list(FIREBASE_PATTERNS.keys()),
    "heroku": list(HEROKU_PATTERNS.keys()),
    "circleci": list(CIRCLECI_PATTERNS.keys()),
    "travisci": list(TRAVISCI_PATTERNS.keys()),
    "jenkins": list(JENKINS_PATTERNS.keys()),
}


def get_patterns_for_category(category: str) -> dict:
    """Get all patterns for a specific category."""
    pattern_keys = PATTERN_GROUPS.get(category, [])
    return {key: ALL_PATTERNS[key] for key in pattern_keys if key in ALL_PATTERNS}


def get_all_patterns() -> dict:
    """Get all patterns."""
    return ALL_PATTERNS.copy()
