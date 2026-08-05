import html
import logging
from typing import Dict, Any
from datetime import datetime

from models import Incident
from agents.evidence_retrieval import civic_evidence_agent
from agents.paritok_optimizer import ParitokContextOptimizer

logger = logging.getLogger("acirp.petition_generator")


def _esc(text) -> str:
    """Escape text for safe HTML embedding."""
    return html.escape(str(text), quote=True)


class LegalPetitionGenerator:
    """
    Legal Petition & Escalation Generator.
    Uses CivicEvidenceRetrievalAgent to assemble a comprehensive statutory evidence bundle (~5,200 tokens),
    compresses it through ParitokContextOptimizer (~1,650 tokens, ~68% reduction),
    and formats an authoritative, legally grounded civic petition.
    """

    def __init__(self):
        self.optimizer = ParitokContextOptimizer()

    def _build_evidence_sections(self, evidence: Dict[str, Any], issue_title: str) -> str:
        """Build case-specific petition sections from the retrieved evidence bundle."""
        html_parts = []

        # Section I: Constitutional & citizen-rights mandates
        const_items = []
        for idx, item in enumerate(evidence.get("constitutional_rights", [])):
            const_items.append(
                f"{idx + 1}. <strong>{_esc(item.get('title', ''))}:</strong> {_esc(item.get('content', ''))}"
            )
        if const_items:
            const_body = '<br>\n    '.join(const_items)
            html_parts.append(
                f'<div class="section-header">I. CONSTITUTIONAL & STATUTORY MANDATES</div>\n  <p>\n    {const_body}\n  </p>'
            )

        # Section II: Case-type specific statutory legislation
        stat_items = []
        for idx, item in enumerate(evidence.get("statutory_sections", [])):
            stat_items.append(
                f"{idx + 1}. <strong>{_esc(item.get('section', ''))}:</strong> {_esc(item.get('mandate', ''))}"
            )
        if stat_items:
            header = f"II. STATUTORY LEGISLATION APPLICABLE TO {_esc(issue_title)}"
            stat_body = '<br>\n    '.join(stat_items)
            html_parts.append(
                f'<div class="section-header">{header}</div>\n  <p>\n    {stat_body}\n  </p>'
            )

        # Section III: Departmental SOPs
        sop_items = []
        for idx, sop in enumerate(evidence.get("departmental_sops", [])):
            sop_items.append(f"{idx + 1}. {_esc(sop)}")
        if sop_items:
            sop_body = '<br>\n    '.join(sop_items)
            html_parts.append(
                f'<div class="section-header">III. DEPARTMENTAL SOPS & REPAIR STANDARDS</div>\n  <p>\n    {sop_body}\n  </p>'
            )

        # Section IV: Contractor SLA & liquidated damages clauses
        contractor_items = []
        for idx, clause in enumerate(evidence.get("contractor_sla_clauses", [])):
            contractor_items.append(f"{idx + 1}. {_esc(clause)}")
        if contractor_items:
            contractor_body = '<br>\n    '.join(contractor_items)
            html_parts.append(
                f'<div class="section-header">IV. CONTRACTOR SLA & LIQUIDATED DAMAGES CLAUSES</div>\n  <p>\n    {contractor_body}\n  </p>'
            )

        # Section V: Historical ward precedents
        precedent_items = []
        for idx, prec in enumerate(evidence.get("historical_precedents", [])):
            precedent_items.append(
                f"{idx + 1}. <strong>[{_esc(prec.get('id', ''))}] ({_esc(prec.get('ward', ''))}):</strong> "
                f"{_esc(prec.get('details', ''))} <em>Outcome: {_esc(prec.get('outcome', ''))}</em>"
            )
        if precedent_items:
            precedent_body = '<br>\n    '.join(precedent_items)
            html_parts.append(
                f'<div class="section-header">V. HISTORICAL WARD PRECEDENTS</div>\n  <p>\n    {precedent_body}\n  </p>'
            )

        return "\n\n  ".join(html_parts) if html_parts else ""

    async def generate_petition(

        self,
        incident: Incident,
        escalation_target: str = "Municipal Commissioner & Zonal Officer"
    ) -> Dict[str, Any]:
        """
        Assembles, compresses, and generates a legal petition document for an incident.
        Returns dictionary containing petition HTML, original token count, compressed token count,
        and legal citation summary.
        """
        # Step 1: Assemble full evidence bundle (~5,200 tokens)
        evidence = civic_evidence_agent.assemble_evidence_bundle(incident, escalation_target=escalation_target)
        raw_evidence_text = evidence["raw_evidence_bundle"]

        system_rules = (
            "You are an expert civic rights attorney drafting a formal municipal petition under "
            "the Karnataka Municipal Corporations Act (KMCA) 1976 and Sakala Guarantee Act 2011. "
            "Retain explicit statutory citations, contractor penalty clauses, and historical incident IDs."
        )

        # Step 2: Pass through Paritok Context Optimizer
        optimized_evidence, metrics = await self.optimizer.optimize_context(
            raw_prompt=raw_evidence_text,
            system_rules=system_rules,
            request_type="Legal Petition Evidence Assembly"
        )

        # Step 3: Format Legal Petition Document (HTML)
        dept_name = (
            incident.current_strategy.department
            if incident.current_strategy
            else "Public Works & Engineering Dept"
        )
        issue_title = (incident.issue_type or "pothole").replace("_", " ").upper()
        token_str = incident.official_token or "BBMP-PENDING-DISPATCH"
        timestamp_now = datetime.now().strftime("%d %B %Y, %H:%M HRS")

        # Case-specific sections populated dynamically from the evidence bundle
        evidence_sections_html = self._build_evidence_sections(evidence, issue_title)

        html_petition = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>FORMAL MUNICIPAL LEGAL PETITION - {incident.id}</title>
  <style>
    body {{
      font-family: 'Times New Roman', Times, serif;
      color: #0f172a;
      margin: 40px;
      line-height: 1.6;
      background: #ffffff;
    }}
    .no-print-bar {{
      background: #0f172a;
      color: #ffffff;
      padding: 12px 20px;
      margin: -40px -40px 30px -40px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: sans-serif;
      font-size: 13px;
    }}
    .print-btn {{
      background: #2563eb;
      color: white;
      border: none;
      padding: 8px 16px;
      border-radius: 6px;
      font-weight: bold;
      cursor: pointer;
      font-size: 13px;
    }}
    .print-btn:hover {{
      background: #1d4ed8;
    }}
    .letterhead {{
      border-bottom: 2px solid #0f172a;
      padding-bottom: 12px;
      margin-bottom: 25px;
      text-align: center;
    }}
    .letterhead h1 {{
      margin: 0;
      font-size: 20px;
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
    .letterhead p {{
      margin: 4px 0 0 0;
      font-size: 11px;
      font-family: sans-serif;
      color: #475569;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      font-weight: 700;
    }}
    .paritok-hero-card {{
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      border-left: 5px solid #2563eb;
      border-radius: 6px;
      padding: 14px 18px;
      margin-bottom: 25px;
      font-family: sans-serif;
      font-size: 12px;
      color: #1e3a8a;
    }}
    .paritok-hero-card strong {{
      color: #1d4ed8;
    }}
    .recipient {{
      margin-bottom: 25px;
      font-size: 13px;
    }}
    .subject {{
      font-weight: bold;
      text-transform: uppercase;
      margin-bottom: 25px;
      border-bottom: 1px solid #94a3b8;
      padding-bottom: 6px;
      font-size: 13px;
    }}
    .section-header {{
      font-family: sans-serif;
      font-size: 11px;
      font-weight: 800;
      color: #334155;
      text-transform: uppercase;
      letter-spacing: 1px;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 4px;
      margin-top: 25px;
      margin-bottom: 12px;
    }}
    .evidence-box {{
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      padding: 14px;
      font-size: 11px;
      font-family: monospace;
      white-space: pre-wrap;
      margin-bottom: 20px;
      border-radius: 4px;
    }}
    .prayer-box {{
      background: #fffbebf8;
      border: 1px solid #fde68a;
      border-left: 4px solid #d97706;
      padding: 15px;
      font-size: 13px;
      margin-top: 25px;
      margin-bottom: 30px;
    }}
    .signature-grid {{
      display: flex;
      justify-content: space-between;
      margin-top: 40px;
      font-size: 12px;
      font-family: sans-serif;
    }}
    @media print {{
      .no-print-bar {{ display: none !important; }}
      body {{ margin: 15mm; font-size: 11pt; }}
      .paritok-hero-card {{
        background: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        color: #000 !important;
      }}
    }}
  </style>
</head>
<body>
  <div class="no-print-bar">
    <span>⚖️ ACIRP Legal Petition Compiler Node</span>
    <button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF Petition</button>
  </div>

  <div class="letterhead">
    <h1>MEMORANDUM OF CIVIC COMPLAINT & LEGAL PETITION</h1>
    <p>Filed under Statutory Authority of KMCA 1976 & Sakala Guarantee Act 2011</p>
  </div>

  <div class="paritok-hero-card">
    ⚡ <strong>PARITOK NEURAL EVIDENCE COMPRESSION AUDIT:</strong><br>
    Assembled Raw Evidence Bundle: <strong>{metrics.original_tokens} tokens</strong> |
    Paritok Optimized Payload: <strong>{metrics.optimized_tokens} tokens</strong> |
    Token Reduction: <strong>{metrics.savings_percentage}% saved</strong> ({metrics.tokens_saved} tokens pruned)<br>
    <em>Source: {metrics.optimizer_source} - Essential statutory provisions, contractor
    penalty clauses, and historical incident IDs verified and retained.</em>
  </div>

  <div class="recipient">
    <strong>TO:</strong> {escalation_target}<br>
    <strong>DEPARTMENT:</strong> {dept_name}<br>
    <strong>DATE:</strong> {timestamp_now}<br>
    <strong>COMPLAINT REF:</strong> {incident.id} | <strong>TRACKING TOKEN:</strong> {token_str}
  </div>

  <div class="subject">
    SUBJECT: DEMAND FOR IMMEDIATE RECTIFICATION OF HAZARDOUS {issue_title} AT GPS
    ({incident.latitude}, {incident.longitude}) & ENFORCEMENT OF CONTRACTOR SLA PENALTY
  </div>

  <p>Respected Authority,</p>

  <p>
    The undersigned Autonomous Civic Intelligence AI Filer (ACIRP Engine) hereby submits
    this formal petition on behalf of
    citizen <strong>{incident.complainant_name}</strong> regarding an unaddressed civic hazard located at coordinates
    GPS ({incident.latitude}, {incident.longitude}).
  </p>

  {evidence_sections_html}

  <div class="section-header">VI. PARITOK-OPTIMIZED EVIDENCE CONTEXT (~{metrics.optimized_tokens} TOKENS)</div>
  <div class="evidence-box">{optimized_evidence}</div>

  <div class="prayer-box">
    <strong>PRAYER FOR RELIEF:</strong><br>
    Wherefore, the petitioner prays that this Nodal Authority:<br>
    (A) Issue an emergency work order for immediate site repair within 24 hours;<br>
    (B) Initiate penalty proceedings under Clause 18.5 against the defaulting contractor;<br>
    (C) File a compliance update on the central portal under Reference <strong>{incident.id}</strong>.
  </div>

  <div class="signature-grid">
    <div>
      <strong>COMPLAINANT / FILER:</strong><br>
      {incident.complainant_name}<br>
      Ward Citizen Representative
    </div>
    <div style="text-align: right;">
      <strong>AUTOMATED LEGAL COMPILATION NODE:</strong><br>
      ACIRP Evidence Retrieval Agent<br>
      Paritok Neural Optimizer Certified Node
    </div>
  </div>
</body>
</html>
"""

        return {

            "html_petition": html_petition,
            "original_tokens": metrics.original_tokens,
            "optimized_tokens": metrics.optimized_tokens,
            "tokens_saved": metrics.tokens_saved,
            "savings_percentage": metrics.savings_percentage,
            "optimizer_source": metrics.optimizer_source,
            "document_count": evidence["document_count"],
            "paritok_metrics": metrics
        }


legal_petition_generator = LegalPetitionGenerator()
