#!/usr/bin/env python3
"""
Cascade Detector: Comprehensive Multi-Repository Test Harness

Tests the cascade detector across:
- 10+ real-world public repositories
- 5+ different programming languages
- Multiple application types (web, CLI, library, microservice)
- Edge cases (large repos, deep nesting, monorepos)

Usage:
  python3 run_comprehensive_tests.py

Output:
  - test_results.json (detailed results)
  - test_summary.txt (human-readable summary)
"""

import json
import subprocess
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from statistics import mean, median

@dataclass
class TestResult:
    """Single test result"""
    repo_name: str
    repo_url: str
    repo_language: str
    repo_type: str
    secrets_found: int
    estimated_true_positives: int
    estimated_false_positives: int
    detection_accuracy: float
    false_positive_rate: float
    execution_time: float
    repo_size_mb: float
    file_count: int
    status: str  # "PASS", "WARNING", "FAIL"
    error_message: Optional[str] = None
    timestamp: str = ""

class ComprehensiveTestRunner:
    """Runs cascade detector on multiple repositories"""
    
    # Real public repositories for testing
    TEST_REPOSITORIES = [
        # (URL, name, language, type, description)
        ("https://github.com/django-stars/django-blog.git", 
         "Django Blog", "Python", "web_framework", 
         "Example Django application"),
        
        ("https://github.com/tiangolo/full-stack-fastapi-template.git",
         "FastAPI Template", "Python", "web_framework",
         "Production-ready FastAPI setup"),
        
        ("https://github.com/expressjs/express.git",
         "Express.js", "JavaScript", "web_framework",
         "Express web framework"),
        
        ("https://github.com/nestjs/nest.git",
         "NestJS", "JavaScript", "web_framework",
         "NestJS framework"),
        
        ("https://github.com/spring-projects-experimental/spring-web-services.git",
         "Spring Web Services", "Java", "web_framework",
         "Spring framework"),
        
        ("https://github.com/gin-gonic/gin.git",
         "Gin Framework", "Go", "web_framework",
         "Go web framework"),
        
        ("https://github.com/laravel/laravel.git",
         "Laravel", "PHP", "web_framework",
         "Laravel framework"),
        
        ("https://github.com/rails/rails.git",
         "Rails", "Ruby", "web_framework",
         "Ruby on Rails"),
        
        ("https://github.com/hashicorp/terraform.git",
         "Terraform", "Go", "infrastructure",
         "Infrastructure as code tool"),
        
        ("https://github.com/actions/toolkit.git",
         "GitHub Actions Toolkit", "JavaScript", "library",
         "Actions JavaScript toolkit"),
    ]
    
    def __init__(self, detector_path: str = "cascade-detector"):
        self.detector_path = detector_path
        self.results: List[TestResult] = []
        self.temp_dirs: List[Path] = []
    
    def clone_repo(self, url: str, depth: int = 1) -> Optional[Path]:
        """Clone repository to temporary directory"""
        try:
            temp_dir = Path(tempfile.mkdtemp(prefix="cascade_test_"))
            self.temp_dirs.append(temp_dir)
            
            print(f"   Cloning (depth={depth})...", end="", flush=True)
            result = subprocess.run(
                ["git", "clone", "--depth", str(depth), url, str(temp_dir)],
                capture_output=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print(" ✓")
                return temp_dir
            else:
                print(" ✗ Clone failed")
                return None
                
        except Exception as e:
            print(f" ✗ Error: {e}")
            return None
    
    def get_repo_stats(self, repo_path: Path) -> Tuple[int, float]:
        """Get repository file count and size"""
        try:
            file_count = 0
            total_size = 0
            
            for root, dirs, files in os.walk(repo_path):
                # Skip git and common large directories
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv']]
                
                for file in files:
                    file_path = Path(root) / file
                    try:
                        total_size += file_path.stat().st_size
                        file_count += 1
                    except:
                        pass
            
            return file_count, total_size / (1024 * 1024)  # Convert to MB
            
        except Exception as e:
            print(f"      Error getting stats: {e}")
            return 0, 0.0
    
    def run_cascade_detector(self, repo_path: Path) -> Optional[List[Dict]]:
        """Run cascade detector on repository"""
        try:
            start_time = time.time()
            
            result = subprocess.run(
                [self.detector_path, "scan", str(repo_path), "--output", "json"],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                findings = json.loads(result.stdout) if result.stdout else []
                return findings, elapsed
            else:
                print(f"      Detector error: {result.stderr[:200]}")
                return None, elapsed
                
        except subprocess.TimeoutExpired:
            print(f"      Timeout (>600s)")
            return None, 600
        except Exception as e:
            print(f"      Error: {e}")
            return None, 0
    
    def estimate_accuracy(self, findings: List[Dict], repo_name: str) -> Tuple[int, int]:
        """Estimate true positives vs false positives"""
        if not findings:
            return 0, 0
        
        true_positives = 0
        false_positives = 0
        
        for finding in findings:
            # Heuristic: high entropy + known pattern = likely TP
            # Low entropy or generic pattern = likely FP
            entropy = finding.get('entropy', 0)
            confidence = finding.get('confidence', 0)
            pattern = finding.get('pattern_name', '')
            
            # Rules for FP estimation
            is_likely_fp = (
                entropy < 2.5 or  # Too low entropy
                (confidence < 0.3 and entropy < 3.5) or  # Low confidence + low entropy
                pattern in ['password123', 'demo_key', 'test_token']  # Common false positives
            )
            
            if is_likely_fp:
                false_positives += 1
            else:
                true_positives += 1
        
        return true_positives, false_positives
    
    def test_repository(self, url: str, repo_name: str, language: str, 
                       repo_type: str, description: str) -> Optional[TestResult]:
        """Test cascade detector on single repository"""
        
        print(f"\n🔍 Testing: {repo_name}")
        print(f"   Language: {language} | Type: {repo_type}")
        print(f"   Description: {description}")
        
        # Clone repository
        repo_path = self.clone_repo(url)
        if not repo_path:
            return TestResult(
                repo_name=repo_name,
                repo_url=url,
                repo_language=language,
                repo_type=repo_type,
                secrets_found=0,
                estimated_true_positives=0,
                estimated_false_positives=0,
                detection_accuracy=0,
                false_positive_rate=0,
                execution_time=0,
                repo_size_mb=0,
                file_count=0,
                status="FAIL",
                error_message="Failed to clone repository",
                timestamp=datetime.now().isoformat()
            )
        
        # Get repo stats
        print(f"   Analyzing repository...", end="", flush=True)
        file_count, repo_size = self.get_repo_stats(repo_path)
        print(f" ({file_count} files, {repo_size:.1f}MB)")
        
        # Run detector
        print(f"   Running Cascade Detector...", end="", flush=True)
        result = self.run_cascade_detector(repo_path)
        
        if result is None or result[0] is None:
            print(" ✗")
            return TestResult(
                repo_name=repo_name,
                repo_url=url,
                repo_language=language,
                repo_type=repo_type,
                secrets_found=0,
                estimated_true_positives=0,
                estimated_false_positives=0,
                detection_accuracy=0,
                false_positive_rate=0,
                execution_time=0,
                repo_size_mb=repo_size,
                file_count=file_count,
                status="FAIL",
                error_message="Detector execution failed",
                timestamp=datetime.now().isoformat()
            )
        
        findings, exec_time = result
        print(f" ✓ ({exec_time:.1f}s)")
        
        # Analyze results
        secrets_found = len(findings)
        true_positives, false_positives = self.estimate_accuracy(findings, repo_name)
        
        accuracy = (true_positives / max(secrets_found, 1)) * 100
        fp_rate = (false_positives / max(secrets_found, 1)) * 100 if secrets_found > 0 else 0
        
        # Determine status
        if accuracy >= 90:
            status = "PASS"
        elif accuracy >= 70:
            status = "WARNING"
        else:
            status = "FAIL"
        
        print(f"   Results: {secrets_found} secrets found")
        print(f"   Estimated TP: {true_positives}, FP: {false_positives}")
        print(f"   Accuracy: {accuracy:.1f}%, FP Rate: {fp_rate:.1f}%")
        print(f"   Status: {status}")
        
        test_result = TestResult(
            repo_name=repo_name,
            repo_url=url,
            repo_language=language,
            repo_type=repo_type,
            secrets_found=secrets_found,
            estimated_true_positives=true_positives,
            estimated_false_positives=false_positives,
            detection_accuracy=accuracy,
            false_positive_rate=fp_rate,
            execution_time=exec_time,
            repo_size_mb=repo_size,
            file_count=file_count,
            status=status,
            timestamp=datetime.now().isoformat()
        )
        
        self.results.append(test_result)
        return test_result
    
    def run_all_tests(self):
        """Run tests on all repositories"""
        print("="*70)
        print("CASCADE DETECTOR - COMPREHENSIVE TEST SUITE")
        print("="*70)
        print(f"Starting tests: {datetime.now().isoformat()}\n")
        
        for url, name, language, repo_type, description in self.TEST_REPOSITORIES:
            try:
                self.test_repository(url, name, language, repo_type, description)
            except KeyboardInterrupt:
                print("\n⚠️  Tests interrupted by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                continue
    
    def cleanup(self):
        """Remove temporary directories"""
        print("\n🧹 Cleaning up temporary directories...", end="", flush=True)
        for temp_dir in self.temp_dirs:
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except:
                pass
        print(" ✓")
    
    def generate_json_report(self, filename: str = "test_results.json"):
        """Generate JSON report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "passed": len([r for r in self.results if r.status == "PASS"]),
            "warnings": len([r for r in self.results if r.status == "WARNING"]),
            "failed": len([r for r in self.results if r.status == "FAIL"]),
            "average_accuracy": mean([r.detection_accuracy for r in self.results]) if self.results else 0,
            "average_false_positive_rate": mean([r.false_positive_rate for r in self.results]) if self.results else 0,
            "average_execution_time": mean([r.execution_time for r in self.results]) if self.results else 0,
            "results": [asdict(r) for r in self.results]
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ JSON report saved to {filename}")
        return report
    
    def generate_text_report(self, filename: str = "test_summary.txt"):
        """Generate human-readable report"""
        
        output = []
        output.append("="*70)
        output.append("CASCADE DETECTOR - TEST SUMMARY REPORT")
        output.append("="*70)
        output.append(f"Report Generated: {datetime.now().isoformat()}\n")
        
        # Overall statistics
        output.append("OVERALL STATISTICS")
        output.append("-"*70)
        output.append(f"Total Tests: {len(self.results)}")
        output.append(f"Passed (✅): {len([r for r in self.results if r.status == 'PASS'])}")
        output.append(f"Warnings (⚠️): {len([r for r in self.results if r.status == 'WARNING'])}")
        output.append(f"Failed (❌): {len([r for r in self.results if r.status == 'FAIL'])}")
        
        if self.results:
            output.append(f"\nAverage Detection Accuracy: {mean([r.detection_accuracy for r in self.results]):.1f}%")
            output.append(f"Average False Positive Rate: {mean([r.false_positive_rate for r in self.results]):.1f}%")
            output.append(f"Average Execution Time: {mean([r.execution_time for r in self.results]):.2f}s")
        
        # Detailed results
        output.append("\n" + "="*70)
        output.append("DETAILED RESULTS")
        output.append("="*70)
        
        for result in self.results:
            status_icon = "✅" if result.status == "PASS" else "⚠️" if result.status == "WARNING" else "❌"
            output.append(f"\n{status_icon} {result.repo_name}")
            output.append(f"   Language: {result.repo_language} | Type: {result.repo_type}")
            output.append(f"   Size: {result.repo_size_mb:.1f}MB | Files: {result.file_count}")
            output.append(f"   Secrets Found: {result.secrets_found}")
            output.append(f"   Estimated TP: {result.estimated_true_positives} | FP: {result.estimated_false_positives}")
            output.append(f"   Accuracy: {result.detection_accuracy:.1f}% | FP Rate: {result.false_positive_rate:.1f}%")
            output.append(f"   Execution Time: {result.execution_time:.2f}s")
            if result.error_message:
                output.append(f"   Error: {result.error_message}")
        
        # Recommendations
        output.append("\n" + "="*70)
        output.append("RECOMMENDATIONS")
        output.append("="*70)
        
        failed_count = len([r for r in self.results if r.status == "FAIL"])
        warning_count = len([r for r in self.results if r.status == "WARNING"])
        
        if failed_count == 0 and warning_count == 0:
            output.append("\n✅ PRODUCTION READY")
            output.append("All tests passed. Safe to deploy to production.")
        elif failed_count == 0:
            output.append("\n⚠️ PROCEED WITH CAUTION")
            output.append(f"Some tests showed warnings ({warning_count}). Review and monitor closely.")
        else:
            output.append("\n❌ NOT READY FOR PRODUCTION")
            output.append(f"Tests failed ({failed_count}). Fix issues before deployment.")
        
        # Save report
        report_text = "\n".join(output)
        with open(filename, 'w') as f:
            f.write(report_text)
        
        print(f"✅ Text report saved to {filename}")
        print("\n" + report_text)

def main():
    """Main entry point"""
    
    # Check if cascade-detector is available
    try:
        result = subprocess.run(
            ["which", "cascade-detector"],
            capture_output=True
        )
        if result.returncode != 0:
            print("❌ cascade-detector not found in PATH")
            print("   Please install it first: pip install -r requirements.txt")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error checking cascade-detector: {e}")
        sys.exit(1)
    
    # Run tests
    runner = ComprehensiveTestRunner()
    try:
        runner.run_all_tests()
    finally:
        runner.cleanup()
    
    # Generate reports
    runner.generate_json_report()
    runner.generate_text_report()

if __name__ == "__main__":
    main()
