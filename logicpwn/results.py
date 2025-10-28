"""
Rich result objects with analysis methods and export capabilities.

Provides structured result objects that make it easy to:
- Analyze security test results
- Export results in multiple formats
- Generate summaries and reports
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SecurityTestResult:
    """
    Rich result object for security tests with analysis methods.

    Attributes:
        test_type: Type of security test (e.g., "IDOR", "Auth", "XSS")
        target_url: URL of tested target
        total_tests: Total number of tests executed
        vulnerabilities: List of found vulnerabilities
        safe_endpoints: List of secure endpoints
        test_duration: Time taken for tests (seconds)
        timestamp: When the test was executed

    Examples:
        >>> result = SecurityTestResult(
        ...     test_type="IDOR",
        ...     target_url="https://api.example.com",
        ...     total_tests=10,
        ...     vulnerabilities=[vuln1, vuln2],
        ...     safe_endpoints=[safe1, safe2]
        ... )
        >>> print(result.summary())
        >>> result.export_json("report.json")
    """

    test_type: str
    target_url: str
    total_tests: int
    vulnerabilities: list[Any] = field(default_factory=list)
    safe_endpoints: list[Any] = field(default_factory=list)
    test_duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def vulnerable_count(self) -> int:
        """Number of vulnerabilities found."""
        return len(self.vulnerabilities)

    @property
    def safe_count(self) -> int:
        """Number of secure endpoints."""
        return len(self.safe_endpoints)

    @property
    def is_vulnerable(self) -> bool:
        """True if any vulnerabilities were found."""
        return self.vulnerable_count > 0

    @property
    def pass_rate(self) -> float:
        """
        Percentage of tests that passed (no vulnerabilities).

        Returns:
            Float between 0.0 and 100.0
        """
        if self.total_tests == 0:
            return 0.0
        return (self.safe_count / self.total_tests) * 100

    @property
    def vulnerability_rate(self) -> float:
        """
        Percentage of tests that found vulnerabilities.

        Returns:
            Float between 0.0 and 100.0
        """
        return 100.0 - self.pass_rate

    def summary(self) -> str:
        """
        Generate human-readable summary of test results.

        Returns:
            Multi-line string with test summary

        Examples:
            >>> print(result.summary())
            IDOR Test Results:
              Target: https://api.example.com
              Total Tests: 10
              Vulnerabilities: 3 (30.0%)
              Secure: 7 (70.0%)
              Status: 🚨 VULNERABLE
        """
        status = "🚨 VULNERABLE" if self.is_vulnerable else "✅ SECURE"

        return (
            f"{self.test_type} Test Results:\n"
            f"  Target: {self.target_url}\n"
            f"  Total Tests: {self.total_tests}\n"
            f"  Vulnerabilities: {self.vulnerable_count} ({self.vulnerability_rate:.1f}%)\n"
            f"  Secure: {self.safe_count} ({self.pass_rate:.1f}%)\n"
            f"  Duration: {self.test_duration:.2f}s\n"
            f"  Status: {status}"
        )

    def detailed_summary(self) -> str:
        """
        Generate detailed summary including vulnerability details.

        Returns:
            Multi-line string with detailed information
        """
        summary = self.summary()

        if self.vulnerabilities:
            summary += "\n\n🚨 Vulnerabilities Found:\n"
            for i, vuln in enumerate(self.vulnerabilities, 1):
                vuln_url = getattr(vuln, "endpoint_url", "Unknown")
                vuln_status = getattr(vuln, "status_code", "N/A")
                summary += f"  {i}. {vuln_url} (Status: {vuln_status})\n"

        return summary

    def to_dict(self) -> dict[str, Any]:
        """
        Convert result to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the result
        """
        return {
            "test_type": self.test_type,
            "target_url": self.target_url,
            "total_tests": self.total_tests,
            "vulnerable_count": self.vulnerable_count,
            "safe_count": self.safe_count,
            "pass_rate": self.pass_rate,
            "vulnerability_rate": self.vulnerability_rate,
            "is_vulnerable": self.is_vulnerable,
            "test_duration": self.test_duration,
            "timestamp": self.timestamp.isoformat(),
            "vulnerabilities": [self._serialize_item(v) for v in self.vulnerabilities],
            "safe_endpoints": [self._serialize_item(e) for e in self.safe_endpoints],
            "metadata": self.metadata,
        }

    def _serialize_item(self, item: Any) -> dict[str, Any]:
        """Serialize vulnerability or endpoint object."""
        if hasattr(item, "model_dump"):
            # Pydantic model
            return item.model_dump()
        elif hasattr(item, "__dict__"):
            # Regular class
            return {k: str(v) for k, v in item.__dict__.items()}
        elif isinstance(item, dict):
            return item
        else:
            return {"value": str(item)}

    def get_critical_vulnerabilities(self) -> list[Any]:
        """
        Get only critical severity vulnerabilities.

        Returns:
            List of critical vulnerabilities
        """
        return [
            v
            for v in self.vulnerabilities
            if getattr(v, "severity", "medium").lower() == "critical"
        ]

    def get_high_vulnerabilities(self) -> list[Any]:
        """
        Get only high severity vulnerabilities.

        Returns:
            List of high severity vulnerabilities
        """
        return [
            v
            for v in self.vulnerabilities
            if getattr(v, "severity", "medium").lower() == "high"
        ]

    def export_json(self, filename: str, indent: int = 2) -> None:
        """
        Export results to JSON file.

        Args:
            filename: Output filename
            indent: JSON indentation level (default: 2)

        Examples:
            >>> result.export_json("security_report.json")
            >>> result.export_json("report.json", indent=4)
        """
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=indent, default=str)

    def export_markdown(self, filename: str) -> None:
        """
        Export results to Markdown file.

        Args:
            filename: Output filename

        Examples:
            >>> result.export_markdown("security_report.md")
        """
        md = f"# {self.test_type} Security Test Report\n\n"
        md += f"**Target:** {self.target_url}\n\n"
        md += f"**Date:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md += f"**Duration:** {self.test_duration:.2f} seconds\n\n"

        # Summary section
        md += "## Summary\n\n"
        md += f"- **Total Tests:** {self.total_tests}\n"
        md += f"- **Vulnerabilities Found:** {self.vulnerable_count} ({self.vulnerability_rate:.1f}%)\n"
        md += f"- **Secure Endpoints:** {self.safe_count} ({self.pass_rate:.1f}%)\n"
        md += f"- **Overall Status:** {'🚨 VULNERABLE' if self.is_vulnerable else '✅ SECURE'}\n\n"

        # Vulnerabilities section
        if self.vulnerabilities:
            md += "## Vulnerabilities Found\n\n"
            for i, vuln in enumerate(self.vulnerabilities, 1):
                vuln_url = getattr(vuln, "endpoint_url", "Unknown")
                vuln_status = getattr(vuln, "status_code", "N/A")
                vuln_evidence = getattr(vuln, "vulnerability_evidence", "N/A")

                md += f"### {i}. {vuln_url}\n\n"
                md += f"- **Status Code:** {vuln_status}\n"
                md += f"- **Evidence:** {vuln_evidence[:200]}...\n\n"
        else:
            md += "## Vulnerabilities Found\n\n"
            md += "✅ No vulnerabilities detected.\n\n"

        # Secure endpoints section
        if self.safe_endpoints:
            md += "## Secure Endpoints\n\n"
            for endpoint in self.safe_endpoints[:10]:  # Limit to first 10
                endpoint_url = getattr(endpoint, "endpoint_url", str(endpoint))
                md += f"- {endpoint_url}\n"

            if len(self.safe_endpoints) > 10:
                md += f"\n_...and {len(self.safe_endpoints) - 10} more secure endpoints_\n"

        with open(filename, "w") as f:
            f.write(md)

    def export_csv(self, filename: str) -> None:
        """
        Export vulnerabilities to CSV file.

        Args:
            filename: Output filename

        Examples:
            >>> result.export_csv("vulnerabilities.csv")
        """
        import csv

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Endpoint", "Status Code", "Vulnerable", "Evidence"])

            # Write vulnerabilities
            for vuln in self.vulnerabilities:
                endpoint = getattr(vuln, "endpoint_url", "Unknown")
                status = getattr(vuln, "status_code", "N/A")
                evidence = getattr(vuln, "vulnerability_evidence", "N/A")
                writer.writerow([endpoint, status, "Yes", evidence[:100]])

            # Write safe endpoints
            for safe in self.safe_endpoints:
                endpoint = getattr(safe, "endpoint_url", str(safe))
                status = getattr(safe, "status_code", "N/A")
                writer.writerow([endpoint, status, "No", ""])

    def print_summary(self) -> None:
        """Print summary to console."""
        print(self.summary())

    def print_detailed(self) -> None:
        """Print detailed summary to console."""
        print(self.detailed_summary())


@dataclass
class ExploitChainResult:
    """
    Result object for exploit chain execution.

    Attributes:
        chain_name: Name of the exploit chain
        total_steps: Total number of steps
        successful_steps: Number of successful steps
        failed_steps: Number of failed steps
        step_results: List of individual step results
        execution_time: Total execution time
    """

    chain_name: str
    total_steps: int
    successful_steps: int = 0
    failed_steps: int = 0
    step_results: list[Any] = field(default_factory=list)
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def success_rate(self) -> float:
        """Percentage of successful steps."""
        if self.total_steps == 0:
            return 0.0
        return (self.successful_steps / self.total_steps) * 100

    @property
    def all_succeeded(self) -> bool:
        """True if all steps succeeded."""
        return self.successful_steps == self.total_steps

    def summary(self) -> str:
        """Generate summary of exploit chain execution."""
        status = "✅ SUCCESS" if self.all_succeeded else "❌ FAILED"

        return (
            f"Exploit Chain: {self.chain_name}\n"
            f"  Total Steps: {self.total_steps}\n"
            f"  Successful: {self.successful_steps}\n"
            f"  Failed: {self.failed_steps}\n"
            f"  Success Rate: {self.success_rate:.1f}%\n"
            f"  Execution Time: {self.execution_time:.2f}s\n"
            f"  Status: {status}"
        )

    def print_summary(self) -> None:
        """Print summary to console."""
        print(self.summary())


# Export public API
__all__ = [
    "SecurityTestResult",
    "ExploitChainResult",
]
