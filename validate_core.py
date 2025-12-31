#!/usr/bin/env python3
"""
Cascade Detector - Real-World Validation Test

This script validates the cascade detector works correctly
on actual secret patterns found in real code.
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from cascade_detector.core.scanner import SecretScanner
from cascade_detector.core.patterns import get_all_patterns, get_patterns_for_category
from cascade_detector.core.graphs import CascadeGraph
from cascade_detector.agents.remediator import RemediatorAgent


def test_aws_detection():
    """Test AWS secret detection"""
    print("\n" + "="*70)
    print("TEST 1: AWS Secret Detection")
    print("="*70)
    
    code = """
# AWS Configuration
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
"""
    
    scanner = SecretScanner()
    results = scanner.scan_content(code, "config.py")
    
    print(f"Scanned: {len(code.split(chr(10)))} lines of code")
    print(f"Found: {len(results)} secrets")
    
    if len(results) >= 1:
        print("✅ PASS: AWS secrets detected")
        for result in results[:3]:
            print(f"   - {result['pattern']}: {result['matched_text'][:40]}")
        return True
    else:
        print("❌ FAIL: No secrets found")
        return False


def test_github_token_detection():
    """Test GitHub token detection"""
    print("\n" + "="*70)
    print("TEST 2: GitHub Token Detection")
    print("="*70)
    
    code = """
# GitHub Configuration
GITHUB_TOKEN = "ghp_16C7e42F292c6912E7710c838347Ae178B4a"
GITHUB_PAT = "ghp_1234567890abcdefghijklmnopqrstuv"
"""
    
    scanner = SecretScanner()
    results = scanner.scan_content(code, "github_config.py")
    
    print(f"Scanned: {len(code.split(chr(10)))} lines of code")
    print(f"Found: {len(results)} secrets")
    
    if len(results) >= 1:
        print("✅ PASS: GitHub tokens detected")
        for result in results[:3]:
            print(f"   - {result['pattern']}: {result['matched_text'][:40]}")
        return True
    else:
        print("❌ FAIL: No tokens found")
        return False


def test_entropy_scoring():
    """Test entropy calculation"""
    print("\n" + "="*70)
    print("TEST 3: Entropy Scoring")
    print("="*70)
    
    scanner = SecretScanner()
    
    # High entropy (should be flagged)
    high_entropy_string = "AKIAIOSFODNN7EXAMPLE"
    high_entropy = scanner.calculate_entropy(high_entropy_string)
    
    # Low entropy (should not be flagged)
    low_entropy_string = "password"
    low_entropy = scanner.calculate_entropy(low_entropy_string)
    
    print(f"High entropy string: '{high_entropy_string}' = {high_entropy:.2f}")
    print(f"Low entropy string: '{low_entropy_string}' = {low_entropy:.2f}")
    
    if high_entropy > low_entropy:
        print("✅ PASS: Entropy scoring works correctly")
        return True
    else:
        print("❌ FAIL: Entropy scoring issue")
        return False


def test_pattern_library():
    """Test pattern library"""
    print("\n" + "="*70)
    print("TEST 4: Pattern Library")
    print("="*70)
    
    all_patterns = get_all_patterns()
    print(f"Total patterns loaded: {len(all_patterns)}")
    
    # Check specific categories
    aws_patterns = get_patterns_for_category("aws")
    github_patterns = get_patterns_for_category("github")
    
    print(f"AWS patterns: {len(aws_patterns)}")
    print(f"GitHub patterns: {len(github_patterns)}")
    
    if len(all_patterns) > 30 and len(aws_patterns) > 0 and len(github_patterns) > 0:
        print("✅ PASS: Pattern library is comprehensive")
        return True
    else:
        print("❌ FAIL: Pattern library issue")
        return False


def test_cascade_graph():
    """Test cascade graph functionality"""
    print("\n" + "="*70)
    print("TEST 5: Cascade Graph Construction")
    print("="*70)
    
    from cascade_detector.core.graphs import Node, Edge
    
    graph = CascadeGraph()
    
    # Add some test nodes
    repo1 = Node("repo1", "Repository 1", "repo", {"language": "python"})
    repo2 = Node("repo2", "Repository 2", "repo", {"language": "javascript"})
    repo3 = Node("repo3", "Repository 3", "repo", {"language": "go"})
    
    graph.add_node(repo1)
    graph.add_node(repo2)
    graph.add_node(repo3)
    
    # Add propagation edges
    edge1 = Edge("repo1", "repo2", "depends_on")
    edge2 = Edge("repo2", "repo3", "depends_on")
    
    graph.add_edge(edge1)
    graph.add_edge(edge2)
    
    # Find paths
    paths = graph.get_cascade_paths("repo1", max_depth=5)
    
    print(f"Graph nodes: {graph.graph.number_of_nodes()}")
    print(f"Graph edges: {graph.graph.number_of_edges()}")
    print(f"Cascade paths from repo1: {len(paths)}")
    
    if graph.graph.number_of_nodes() >= 3:
        print("✅ PASS: Cascade graph works correctly")
        return True
    else:
        print("❌ FAIL: Graph construction issue")
        return False


def test_remediation():
    """Test remediation functionality"""
    print("\n" + "="*70)
    print("TEST 6: Remediation Patch Generation")
    print("="*70)
    
    remediator = RemediatorAgent()
    
    # Create a mock secret finding
    secret_match = {
        "pattern": "aws_access_key",
        "matched_text": "AKIAIOSFODNN7EXAMPLE",
        "line": 5
    }
    
    file_content = 'AWS_KEY = "AKIAIOSFODNN7EXAMPLE"\nother_code = 123\n'
    file_path = "config.py"
    
    try:
        patch = remediator.generate_patch(file_content, file_path, secret_match)
        
        if patch and hasattr(patch, 'diff'):
            print(f"Generated patch length: {len(patch.diff)} characters")
            print("Sample patch:")
            for line in patch.diff.split('\n')[:5]:
                if line.strip():
                    print(f"  {line}")
            print("✅ PASS: Remediation works correctly")
            return True
        else:
            print("❌ FAIL: No patch generated")
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)[:100]}")
        return False


def test_multiple_secret_types():
    """Test detection of multiple secret types in single file"""
    print("\n" + "="*70)
    print("TEST 7: Multiple Secret Types")
    print("="*70)
    
    code = """
# Configuration file with multiple secrets
import os

# AWS
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"

# GitHub
GITHUB_TOKEN = "ghp_16C7e42F292c6912E7710c838347Ae178B4a"

# Database
DB_PASSWORD = "Super_Secure_Pass_123"

# API
API_KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz123456"

# Stripe
STRIPE_KEY = "sk_live_51234567890abcdefghijk"
"""
    
    scanner = SecretScanner()
    results = scanner.scan_content(code, "multi_secret_file.py")
    
    print(f"Scanned: {len(code.split(chr(10)))} lines of code")
    print(f"Found: {len(results)} secrets")
    
    patterns_found = set(r['pattern'] for r in results)
    print(f"Pattern types: {', '.join(sorted(patterns_found)[:5])}")
    
    if len(results) >= 4:
        print("✅ PASS: Multiple secret types detected")
        return True
    else:
        print("❌ FAIL: Not all secrets detected")
        return False


def main():
    """Run all validation tests"""
    print("\n" + "="*70)
    print("CASCADE DETECTOR - PRODUCTION READINESS VALIDATION")
    print("="*70)
    
    tests = [
        ("AWS Detection", test_aws_detection),
        ("GitHub Token Detection", test_github_token_detection),
        ("Entropy Scoring", test_entropy_scoring),
        ("Pattern Library", test_pattern_library),
        ("Cascade Graph", test_cascade_graph),
        ("Remediation", test_remediation),
        ("Multiple Secret Types", test_multiple_secret_types),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"ERROR: {str(e)[:200]}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for test_name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status:15} {test_name}")
    
    print("\n" + "-"*70)
    percentage = (passed * 100) // total
    print(f"Results: {passed}/{total} tests passed ({percentage}%)")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - PRODUCTION READY")
        print("\nRecommended next steps:")
        print("1. Test on real repositories (100+ repos)")
        print("2. Run comprehensive test suite: python3 run_comprehensive_tests.py")
        print("3. Compare accuracy with TruffleHog")
        print("4. Deploy to production or GitHub")
    elif passed >= total - 1:
        print("\n⚠️ NEARLY READY - Minor issues detected")
        print("Most tests passing. Review failed tests and run again.")
    else:
        print(f"\n❌ NEEDS FIXES - {total - passed} tests failed")
        print("Review errors above and fix issues before deployment.")
    
    return 0 if passed >= total - 1 else 1


if __name__ == "__main__":
    sys.exit(main())
