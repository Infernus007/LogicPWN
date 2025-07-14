from logicpwn.exporters import BaseExporter
from logicpwn.core.reporter.orchestrator import VulnerabilityFinding, ReportMetadata
from typing import List
from logicpwn.core.reporter.template_renderer import TemplateRenderer
import os

class MarkdownExporter(BaseExporter):
    def export(self, findings: List[VulnerabilityFinding], metadata: ReportMetadata) -> str:
        renderer = TemplateRenderer()
        context = {
            "title": metadata.title,
            "target_url": metadata.target_url,
            "scan_start_time": metadata.scan_start_time,
            "scan_end_time": metadata.scan_end_time,
            "total_findings": sum(metadata.findings_count.values()),
            "critical_count": metadata.findings_count.get('Critical', 0),
            "findings": [f.model_dump() if hasattr(f, 'model_dump') else f.dict() for f in findings],
            "scan_duration": metadata.scan_end_time - metadata.scan_start_time,
            "logicpwn_version": metadata.logicpwn_version,
            "authenticated_user": metadata.authenticated_user or 'N/A',
        }
        try:
            return renderer.render("markdown_template.md", context)
        except Exception:
            # Fallback to inline rendering
            lines = [
                f"# {metadata.title}",
                f"\n**Target:** {metadata.target_url}",
                f"\n**Assessment Date:** {metadata.scan_start_time.strftime('%Y-%m-%d')} - {metadata.scan_end_time.strftime('%Y-%m-%d')}",
                f"\n**Total Findings:** {sum(metadata.findings_count.values())}",
                f"\n**Critical Issues:** {metadata.findings_count.get('Critical', 0)}",
                "\n---\n",
                "## Vulnerability Details\n"
            ]
            for finding in findings:
                lines.extend([
                    f"### {finding.severity} - {finding.title}",
                    f"**CVSS Score:** {finding.cvss_score if finding.cvss_score is not None else 'N/A'}",
                    f"**Affected Endpoints:** {', '.join(finding.affected_endpoints)}",
                    f"\n**Description:**\n{finding.description}",
                    f"\n**Proof of Concept:**\n```http\n{finding.proof_of_concept}\n```",
                    f"\n**Impact:**\n{finding.impact}",
                    f"\n**Remediation:**\n{finding.remediation}",
                    f"\n**References:** {', '.join(finding.references) if finding.references else 'N/A'}",
                    f"\n**Discovered At:** {finding.discovered_at.isoformat()}",
                    "\n---\n"
                ])
            lines.append("## Appendix\n")
            lines.append(f"- **Scan Duration:** {(metadata.scan_end_time - metadata.scan_start_time)}")
            lines.append(f"- **LogicPwn Version:** {metadata.logicpwn_version}")
            lines.append(f"- **Authentication:** {metadata.authenticated_user or 'N/A'}")
            return '\n'.join(lines) 