from logicpwn.exporters import BaseExporter
from logicpwn.core.reporter.orchestrator import VulnerabilityFinding, ReportMetadata
from typing import List
from logicpwn.core.reporter.template_renderer import TemplateRenderer
import os

class HTMLExporter(BaseExporter):
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
            return renderer.render("html_template.html", context)
        except Exception:
            html = [
                f"<html><head><title>{metadata.title}</title></head><body>",
                f"<h1>{metadata.title}</h1>",
                f"<p><b>Target:</b> {metadata.target_url}<br>",
                f"<b>Assessment Date:</b> {metadata.scan_start_time.strftime('%Y-%m-%d')} - {metadata.scan_end_time.strftime('%Y-%m-%d')}<br>",
                f"<b>Total Findings:</b> {sum(metadata.findings_count.values())}<br>",
                f"<b>Critical Issues:</b> {metadata.findings_count.get('Critical', 0)}</p>",
                "<hr><h2>Vulnerability Details</h2>"
            ]
            for finding in findings:
                html.extend([
                    f"<h3>{finding.severity} - {finding.title}</h3>",
                    f"<b>CVSS Score:</b> {finding.cvss_score if finding.cvss_score is not None else 'N/A'}<br>",
                    f"<b>Affected Endpoints:</b> {', '.join(finding.affected_endpoints)}<br>",
                    f"<b>Description:</b><pre>{finding.description}</pre>",
                    f"<b>Proof of Concept:</b><pre>{finding.proof_of_concept}</pre>",
                    f"<b>Impact:</b><pre>{finding.impact}</pre>",
                    f"<b>Remediation:</b><pre>{finding.remediation}</pre>",
                    f"<b>References:</b> {', '.join(finding.references) if finding.references else 'N/A'}<br>",
                    f"<b>Discovered At:</b> {finding.discovered_at.isoformat()}<hr>"
                ])
            html.append("<h2>Appendix</h2>")
            html.append(f"<ul><li><b>Scan Duration:</b> {metadata.scan_end_time - metadata.scan_start_time}</li>")
            html.append(f"<li><b>LogicPwn Version:</b> {metadata.logicpwn_version}</li>")
            html.append(f"<li><b>Authentication:</b> {metadata.authenticated_user or 'N/A'}</li></ul>")
            html.append("</body></html>")
            return ''.join(html) 