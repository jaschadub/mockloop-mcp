#!/usr/bin/env python3
"""
Installation verification script for mockloop-mcp.

This script verifies that the package can be installed and works correctly
across different platforms and Python versions.
"""

import argparse
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class InstallationVerifier:
    """Verifies mockloop-mcp installation from PyPI or TestPyPI."""
    
    def __init__(self, version: Optional[str] = None, use_testpypi: bool = False):
        self.version = version
        self.use_testpypi = use_testpypi
        self.results: Dict = {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "python_version": platform.python_version(),
                "python_implementation": platform.python_implementation(),
            },
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "errors": []
            }
        }
    
    def log_test(self, name: str, success: bool, message: str = "", details: Optional[Dict] = None):
        """Log a test result."""
        test_result = {
            "name": name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.results["tests"].append(test_result)
        self.results["summary"]["total"] += 1
        
        if success:
            self.results["summary"]["passed"] += 1
            print(f"✅ {name}: {message}")
        else:
            self.results["summary"]["failed"] += 1
            self.results["summary"]["errors"].append(f"{name}: {message}")
            print(f"❌ {name}: {message}")
    
    def run_command(self, cmd: List[str], capture_output: bool = True, timeout: int = 60) -> Tuple[bool, str, str]:
        """Run a command and return success status, stdout, stderr."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                check=False
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, "", str(e)
    
    def test_pip_installation(self) -> bool:
        """Test package installation via pip."""
        print("\n🔧 Testing pip installation...")
        
        # Prepare installation command
        if self.use_testpypi:
            cmd = [
                sys.executable, "-m", "pip", "install",
                "--index-url", "https://test.pypi.org/simple/",
                "--extra-index-url", "https://pypi.org/simple/",
                "mockloop-mcp"
            ]
            source = "TestPyPI"
        else:
            cmd = [sys.executable, "-m", "pip", "install", "mockloop-mcp"]
            source = "PyPI"
        
        if self.version:
            cmd[-1] += f"=={self.version}"
        
        # Install package
        success, stdout, stderr = self.run_command(cmd, timeout=120)
        
        if success:
            self.log_test(
                "pip_installation",
                True,
                f"Successfully installed from {source}",
                {"source": source, "version": self.version}
            )
        else:
            self.log_test(
                "pip_installation",
                False,
                f"Failed to install from {source}: {stderr}",
                {"source": source, "version": self.version, "error": stderr}
            )
        
        return success
    
    def test_cli_command(self) -> bool:
        """Test that the CLI command works."""
        print("\n🖥️  Testing CLI command...")
        
        # Test --version flag
        success, stdout, stderr = self.run_command([
            sys.executable, "-m", "mockloop_mcp", "--version"
        ])
        
        if success:
            version_output = stdout.strip()
            self.log_test(
                "cli_version",
                True,
                f"CLI version command works: {version_output}",
                {"output": version_output}
            )
        else:
            self.log_test(
                "cli_version",
                False,
                f"CLI version command failed: {stderr}",
                {"error": stderr}
            )
            return False
        
        # Test --help flag
        success, stdout, stderr = self.run_command([
            sys.executable, "-m", "mockloop_mcp", "--help"
        ])
        
        if success and "usage:" in stdout.lower():
            self.log_test(
                "cli_help",
                True,
                "CLI help command works",
                {"help_length": len(stdout)}
            )
        else:
            self.log_test(
                "cli_help",
                False,
                f"CLI help command failed: {stderr}",
                {"error": stderr}
            )
            return False
        
        return True
    
    def test_package_import(self) -> bool:
        """Test that the package can be imported."""
        print("\n📦 Testing package import...")
        
        try:
            import mockloop_mcp
            
            # Test basic attributes
            if hasattr(mockloop_mcp, '__version__'):
                version = mockloop_mcp.__version__
                self.log_test(
                    "package_import",
                    True,
                    f"Package imported successfully, version: {version}",
                    {"version": version}
                )
            else:
                self.log_test(
                    "package_import",
                    True,
                    "Package imported successfully (no version attribute)",
                    {}
                )
            
            # Test main modules
            from mockloop_mcp import generator, parser
            self.log_test(
                "module_imports",
                True,
                "Core modules imported successfully",
                {"modules": ["generator", "parser"]}
            )
            
            return True
            
        except ImportError as e:
            self.log_test(
                "package_import",
                False,
                f"Failed to import package: {e}",
                {"error": str(e)}
            )
            return False
        except Exception as e:
            self.log_test(
                "package_import",
                False,
                f"Unexpected error during import: {e}",
                {"error": str(e)}
            )
            return False
    
    def test_basic_functionality(self) -> bool:
        """Test basic package functionality."""
        print("\n⚙️  Testing basic functionality...")
        
        try:
            # Create a temporary directory for testing
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create a simple test spec
                test_spec = {
                    "openapi": "3.0.0",
                    "info": {"title": "Test API", "version": "1.0.0"},
                    "paths": {
                        "/test": {
                            "get": {
                                "responses": {
                                    "200": {
                                        "description": "Success",
                                        "content": {
                                            "application/json": {
                                                "schema": {"type": "object"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                
                spec_file = temp_path / "test_spec.json"
                with open(spec_file, 'w') as f:
                    json.dump(test_spec, f)
                
                # Test mock generation
                from mockloop_mcp.generator import MockGenerator
                
                generator = MockGenerator()
                output_dir = temp_path / "test_output"
                
                # This should not raise an exception
                generator.generate_mock_server(
                    spec_path=str(spec_file),
                    output_dir=str(output_dir)
                )
                
                # Check if files were generated
                if output_dir.exists() and any(output_dir.iterdir()):
                    self.log_test(
                        "basic_functionality",
                        True,
                        "Mock server generation works",
                        {"output_files": [f.name for f in output_dir.iterdir()]}
                    )
                    return True
                else:
                    self.log_test(
                        "basic_functionality",
                        False,
                        "Mock server generation produced no output",
                        {}
                    )
                    return False
                    
        except Exception as e:
            self.log_test(
                "basic_functionality",
                False,
                f"Basic functionality test failed: {e}",
                {"error": str(e)}
            )
            return False
    
    def test_dependencies(self) -> bool:
        """Test that all dependencies are properly installed."""
        print("\n📚 Testing dependencies...")
        
        required_packages = [
            "fastapi",
            "uvicorn",
            "jinja2",
            "pydantic",
            "click",
            "requests"
        ]
        
        failed_imports = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                failed_imports.append(package)
        
        if not failed_imports:
            self.log_test(
                "dependencies",
                True,
                "All required dependencies are available",
                {"packages": required_packages}
            )
            return True
        else:
            self.log_test(
                "dependencies",
                False,
                f"Missing dependencies: {', '.join(failed_imports)}",
                {"missing": failed_imports, "required": required_packages}
            )
            return False
    
    def run_all_tests(self) -> bool:
        """Run all verification tests."""
        print(f"🚀 Starting installation verification for mockloop-mcp")
        print(f"Platform: {self.results['platform']['system']} {self.results['platform']['release']}")
        print(f"Python: {self.results['platform']['python_version']} ({self.results['platform']['python_implementation']})")
        print(f"Source: {'TestPyPI' if self.use_testpypi else 'PyPI'}")
        if self.version:
            print(f"Version: {self.version}")
        
        # Run tests in order
        tests = [
            self.test_pip_installation,
            self.test_package_import,
            self.test_dependencies,
            self.test_cli_command,
            self.test_basic_functionality,
        ]
        
        all_passed = True
        for test in tests:
            try:
                if not test():
                    all_passed = False
            except Exception as e:
                self.log_test(
                    test.__name__,
                    False,
                    f"Test crashed: {e}",
                    {"error": str(e)}
                )
                all_passed = False
        
        return all_passed
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate a verification report."""
        summary = self.results["summary"]
        
        report = f"""
# MockLoop MCP Installation Verification Report

## Platform Information
- **System**: {self.results['platform']['system']} {self.results['platform']['release']}
- **Architecture**: {self.results['platform']['machine']}
- **Python**: {self.results['platform']['python_version']} ({self.results['platform']['python_implementation']})

## Test Summary
- **Total Tests**: {summary['total']}
- **Passed**: {summary['passed']}
- **Failed**: {summary['failed']}
- **Success Rate**: {(summary['passed'] / summary['total'] * 100) if summary['total'] > 0 else 0:.1f}%

## Test Results
"""
        
        for test in self.results["tests"]:
            status = "✅ PASS" if test["success"] else "❌ FAIL"
            report += f"- **{test['name']}**: {status} - {test['message']}\n"
        
        if summary["errors"]:
            report += "\n## Errors\n"
            for error in summary["errors"]:
                report += f"- {error}\n"
        
        report += f"\n## Raw Results\n```json\n{json.dumps(self.results, indent=2)}\n```\n"
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"\n📄 Report saved to: {output_file}")
        
        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify mockloop-mcp installation from PyPI"
    )
    parser.add_argument(
        "--version",
        help="Specific version to test (default: latest)"
    )
    parser.add_argument(
        "--testpypi",
        action="store_true",
        help="Use TestPyPI instead of PyPI"
    )
    parser.add_argument(
        "--output",
        help="Output file for verification report"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    verifier = InstallationVerifier(
        version=args.version,
        use_testpypi=args.testpypi
    )
    
    success = verifier.run_all_tests()
    
    print(f"\n{'='*60}")
    print(f"🎯 Verification {'PASSED' if success else 'FAILED'}")
    print(f"📊 Results: {verifier.results['summary']['passed']}/{verifier.results['summary']['total']} tests passed")
    
    if args.json:
        print(json.dumps(verifier.results, indent=2))
    else:
        report = verifier.generate_report(args.output)
        if not args.output:
            print(report)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()