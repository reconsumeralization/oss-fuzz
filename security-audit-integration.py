#!/usr/bin/env python3
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
################################################################################

"""
Security Audit Integration Script for OSS-Fuzz Master Compliance and Deployment System

This script processes security audit reports and integrates them into the master
compliance and deployment system to ensure security vulnerabilities are addressed
before deployment.
"""

import json
import re
import os
import sys
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security-audit-integration.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

@dataclass
class Vulnerability:
    """Represents a security vulnerability from an audit report."""
    id: str
    title: str
    severity: Severity
    cwe: str
    cvss_vector: str
    summary: str
    description: str
    reproduction_steps: List[str]
    root_cause: str
    mitigation: str
    patch: str
    poc: str
    impact_analysis: str
    business_impact: str
    affected_files: List[str]
    status: str = "OPEN"
    created_date: str = ""
    last_updated: str = ""

@dataclass
class SecurityAudit:
    """Represents a complete security audit report."""
    repository_url: str
    executive_summary: str
    vulnerabilities: List[Vulnerability]
    overall_security_posture: str
    audit_date: str
    auditor: str

class SecurityAuditProcessor:
    """Processes security audit reports and integrates them into compliance system."""
    
    def __init__(self, audit_file: str):
        self.audit_file = audit_file
        self.audit_data = None
        self.vulnerabilities = []
        
    def parse_markdown_audit(self) -> SecurityAudit:
        """Parse a markdown-formatted security audit report."""
        logger.info(f"Parsing security audit from: {self.audit_file}")
        
        with open(self.audit_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract repository URL
        repo_match = re.search(r'\*\*Repository URL\*\*: \[([^\]]+)\]', content)
        repository_url = repo_match.group(1) if repo_match else "Unknown"
        
        # Extract executive summary
        exec_summary_match = re.search(r'## Executive Summary\n\n(.*?)(?=\n##)', content, re.DOTALL)
        executive_summary = exec_summary_match.group(1).strip() if exec_summary_match else ""
        
        # Extract vulnerabilities
        vulnerabilities = self._extract_vulnerabilities(content)
        
        # Extract overall security posture
        posture_match = re.search(r'## Overall Security Posture\n\n(.*?)(?=\n---|$)', content, re.DOTALL)
        overall_posture = posture_match.group(1).strip() if posture_match else ""
        
        return SecurityAudit(
            repository_url=repository_url,
            executive_summary=executive_summary,
            vulnerabilities=vulnerabilities,
            overall_security_posture=overall_posture,
            audit_date=datetime.now().isoformat(),
            auditor="Security Audit Integration System"
        )
    
    def _extract_vulnerabilities(self, content: str) -> List[Vulnerability]:
        """Extract individual vulnerabilities from the audit content."""
        vulnerabilities = []
        
        # Split content by vulnerability sections
        vuln_sections = re.split(r'### \d+\. Vulnerability:', content)
        
        for i, section in enumerate(vuln_sections[1:], 1):  # Skip first empty section
            try:
                vuln = self._parse_vulnerability_section(section, i)
                if vuln:
                    vulnerabilities.append(vuln)
            except Exception as e:
                logger.warning(f"Failed to parse vulnerability {i}: {e}")
                continue
        
        return vulnerabilities
    
    def _parse_vulnerability_section(self, section: str, vuln_num: int) -> Optional[Vulnerability]:
        """Parse a single vulnerability section."""
        lines = section.strip().split('\n')
        
        # Extract title
        title_match = re.search(r'^([^:]+):', lines[0])
        if not title_match:
            return None
        title = title_match.group(1).strip()
        
        # Extract severity
        severity_match = re.search(r'\*\*Severity\*\*: (\w+)', section)
        severity_str = severity_match.group(1) if severity_match else "MEDIUM"
        try:
            severity = Severity(severity_str)
        except ValueError:
            severity = Severity.MEDIUM
        
        # Extract CWE
        cwe_match = re.search(r'\*\*CWE\*\*: (CWE-\d+)', section)
        cwe = cwe_match.group(1) if cwe_match else "CWE-Unknown"
        
        # Extract CVSS
        cvss_match = re.search(r'\*\*CVSS Vector\*\*: `([^`]+)`', section)
        cvss_vector = cvss_match.group(1) if cvss_match else ""
        
        # Extract summary
        summary_match = re.search(r'\*\*Summary\*\*: (.+?)(?=\n\n|\n\*\*|\n###|\n---|$)', section, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else ""
        
        # Extract description
        desc_match = re.search(r'### Vulnerability Explanation\n\n(.*?)(?=\n###|\n---|$)', section, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""
        
        # Extract reproduction steps
        repro_match = re.search(r'### Reproduction Steps\n\n(.*?)(?=\n###|\n---|$)', section, re.DOTALL)
        reproduction_steps = []
        if repro_match:
            steps_text = repro_match.group(1)
            steps = re.findall(r'\d+\.\s+(.+?)(?=\n\d+\.|\n\n|\n###|\n---|$)', steps_text, re.DOTALL)
            reproduction_steps = [step.strip() for step in steps]
        
        # Extract root cause
        root_match = re.search(r'### Root Cause Analysis\n\n(.*?)(?=\n###|\n---|$)', section, re.DOTALL)
        root_cause = root_match.group(1).strip() if root_match else ""
        
        # Extract mitigation
        mit_match = re.search(r'### Suggested Mitigation\n\n(.*?)(?=\n###|\n---|$)', section, re.DOTALL)
        mitigation = mit_match.group(1).strip() if mit_match else ""
        
        # Extract patch
        patch_match = re.search(r'### Suggested Patch\n\n(.*?)(?=\n###|\n---|$)', section, re.DOTALL)
        patch = patch_match.group(1).strip() if patch_match else ""
        
        # Extract PoC
        poc_match = re.search(r'### Fuzzer Proof-of-Concept\n\n(.*?)(?=\n###|\n---|$)', section, re.DOTALL)
        poc = poc_match.group(1).strip() if poc_match else ""
        
        # Extract impact analysis
        impact_match = re.search(r'### Impact Analysis\n\n(.*?)(?=\n###|\n---|$)', section, re.DOTALL)
        impact_analysis = impact_match.group(1).strip() if impact_match else ""
        
        # Extract business impact
        business_match = re.search(r'### Business Impact Analysis\n\n(.*?)(?=\n###|\n---|$)', section, re.DOTALL)
        business_impact = business_match.group(1).strip() if business_match else ""
        
        # Extract affected files (simplified - would need more sophisticated parsing)
        affected_files = []
        
        return Vulnerability(
            id=f"VULN-{vuln_num:03d}",
            title=title,
            severity=severity,
            cwe=cwe,
            cvss_vector=cvss_vector,
            summary=summary,
            description=description,
            reproduction_steps=reproduction_steps,
            root_cause=root_cause,
            mitigation=mitigation,
            patch=patch,
            poc=poc,
            impact_analysis=impact_analysis,
            business_impact=business_impact,
            affected_files=affected_files,
            created_date=datetime.now().isoformat()
        )
    
    def generate_compliance_report(self, audit: SecurityAudit) -> Dict[str, Any]:
        """Generate a compliance report based on the security audit."""
        logger.info("Generating compliance report from security audit")
        
        # Count vulnerabilities by severity
        severity_counts = {}
        for severity in Severity:
            severity_counts[severity.value] = len([
                v for v in audit.vulnerabilities if v.severity == severity
            ])
        
        # Identify critical and high severity issues
        critical_issues = [v for v in audit.vulnerabilities if v.severity in [Severity.CRITICAL, Severity.HIGH]]
        
        # Generate compliance status
        compliance_status = "FAILED" if critical_issues else "PASSED"
        
        report = {
            "audit_metadata": {
                "repository_url": audit.repository_url,
                "audit_date": audit.audit_date,
                "auditor": audit.auditor,
                "total_vulnerabilities": len(audit.vulnerabilities),
                "severity_breakdown": severity_counts,
                "compliance_status": compliance_status
            },
            "critical_issues": [
                {
                    "id": v.id,
                    "title": v.title,
                    "severity": v.severity.value,
                    "cwe": v.cwe,
                    "summary": v.summary,
                    "status": v.status
                }
                for v in critical_issues
            ],
            "executive_summary": audit.executive_summary,
            "overall_security_posture": audit.overall_security_posture,
            "recommendations": self._generate_recommendations(audit)
        }
        
        return report
    
    def _generate_recommendations(self, audit: SecurityAudit) -> List[str]:
        """Generate recommendations based on the audit findings."""
        recommendations = []
        
        critical_count = len([v for v in audit.vulnerabilities if v.severity == Severity.CRITICAL])
        high_count = len([v for v in audit.vulnerabilities if v.severity == Severity.HIGH])
        
        if critical_count > 0:
            recommendations.append(f"CRITICAL: Address {critical_count} critical vulnerabilities before deployment")
        
        if high_count > 0:
            recommendations.append(f"HIGH: Prioritize fixing {high_count} high severity vulnerabilities")
        
        # Add specific recommendations based on vulnerability types
        cwe_counts = {}
        for vuln in audit.vulnerabilities:
            cwe_counts[vuln.cwe] = cwe_counts.get(vuln.cwe, 0) + 1
        
        for cwe, count in cwe_counts.items():
            if count > 1:
                recommendations.append(f"Multiple {cwe} vulnerabilities detected - implement systematic fixes")
        
        recommendations.append("Implement automated security scanning in CI/CD pipeline")
        recommendations.append("Establish security review process for all code changes")
        recommendations.append("Regular security audits and penetration testing")
        
        return recommendations
    
    def create_deployment_blockers(self, audit: SecurityAudit) -> List[Dict[str, Any]]:
        """Create deployment blockers for critical security issues."""
        blockers = []
        
        for vuln in audit.vulnerabilities:
            if vuln.severity in [Severity.CRITICAL, Severity.HIGH]:
                blocker = {
                    "id": f"BLOCKER-{vuln.id}",
                    "type": "SECURITY_VULNERABILITY",
                    "severity": vuln.severity.value,
                    "title": vuln.title,
                    "description": vuln.summary,
                    "cwe": vuln.cwe,
                    "required_action": "FIX_BEFORE_DEPLOYMENT",
                    "mitigation": vuln.mitigation,
                    "created_date": datetime.now().isoformat()
                }
                blockers.append(blocker)
        
        return blockers
    
    def save_audit_data(self, audit: SecurityAudit, output_dir: str = "."):
        """Save the processed audit data to files."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save full audit data
        audit_file = os.path.join(output_dir, "security-audit-data.json")
        with open(audit_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(audit), f, indent=2, default=str)
        
        # Save compliance report
        compliance_report = self.generate_compliance_report(audit)
        compliance_file = os.path.join(output_dir, "security-compliance-report.json")
        with open(compliance_file, 'w', encoding='utf-8') as f:
            json.dump(compliance_report, f, indent=2)
        
        # Save deployment blockers
        blockers = self.create_deployment_blockers(audit)
        blockers_file = os.path.join(output_dir, "deployment-blockers.json")
        with open(blockers_file, 'w', encoding='utf-8') as f:
            json.dump(blockers, f, indent=2)
        
        logger.info(f"Audit data saved to {output_dir}")
        return audit_file, compliance_file, blockers_file

def main():
    parser = argparse.ArgumentParser(description="Security Audit Integration for OSS-Fuzz")
    parser.add_argument("audit_file", help="Path to security audit markdown file")
    parser.add_argument("--output-dir", default=".", help="Output directory for processed data")
    parser.add_argument("--generate-report", action="store_true", help="Generate detailed compliance report")
    parser.add_argument("--check-blockers", action="store_true", help="Check for deployment blockers")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.audit_file):
        logger.error(f"Audit file not found: {args.audit_file}")
        sys.exit(1)
    
    try:
        # Process the audit
        processor = SecurityAuditProcessor(args.audit_file)
        audit = processor.parse_markdown_audit()
        
        logger.info(f"Processed audit with {len(audit.vulnerabilities)} vulnerabilities")
        
        # Save processed data
        audit_file, compliance_file, blockers_file = processor.save_audit_data(audit, args.output_dir)
        
        # Generate additional reports if requested
        if args.generate_report:
            compliance_report = processor.generate_compliance_report(audit)
            print("\n" + "="*80)
            print("SECURITY COMPLIANCE REPORT")
            print("="*80)
            print(f"Repository: {compliance_report['audit_metadata']['repository_url']}")
            print(f"Status: {compliance_report['audit_metadata']['compliance_status']}")
            print(f"Total Vulnerabilities: {compliance_report['audit_metadata']['total_vulnerabilities']}")
            print(f"Severity Breakdown: {compliance_report['audit_metadata']['severity_breakdown']}")
            
            if compliance_report['critical_issues']:
                print(f"\nCritical Issues ({len(compliance_report['critical_issues'])}):")
                for issue in compliance_report['critical_issues']:
                    print(f"  - {issue['id']}: {issue['title']} ({issue['severity']})")
            
            print(f"\nRecommendations:")
            for rec in compliance_report['recommendations']:
                print(f"  - {rec}")
        
        if args.check_blockers:
            blockers = processor.create_deployment_blockers(audit)
            if blockers:
                print(f"\nDEPLOYMENT BLOCKERS ({len(blockers)}):")
                for blocker in blockers:
                    print(f"  - {blocker['id']}: {blocker['title']} ({blocker['severity']})")
                print(f"\nDeployment blocked due to {len(blockers)} security vulnerabilities")
            else:
                print("\nNo deployment blockers found")
        
        logger.info("Security audit integration completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to process security audit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
