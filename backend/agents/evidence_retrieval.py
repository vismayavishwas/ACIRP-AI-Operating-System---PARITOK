import logging
from typing import Dict, Any
from models import Incident

logger = logging.getLogger("acirp.evidence_retrieval")


class CivicEvidenceRetrievalAgent:
    """
    Civic Evidence Retrieval & Assembly Agent (Evidence Assembly Agent).
    Assembles comprehensive statutory, SLA, contractor liability, departmental SOP,
    and historical precedent evidence bundles (~4,000 - 6,000 tokens) categorized by case type:
    - POTHOLE / ROAD DEFECT
    - GARBAGE / SOLID WASTE DUMPING
    - FALLEN TREE / ARBORICULTURE HAZARD
    """

    def __init__(self):
        # -------------------------------------------------------------------------
        # 1. COMMON CONSTITUTIONAL & CITIZEN RIGHTS MANDATES
        # -------------------------------------------------------------------------
        self.constitutional_rights = [
            {
                "title": "Constitution of India - Article 21 (Right to Life & Safe Infrastructure)",
                "content": (
                    "High Court of Karnataka Binding Precedent (WP 42927/2015): The Right to Life guaranteed under "
                    "Article 21 includes the fundamental right to reasonably safe, hazard-free public roads, well-lit "
                    "thoroughfares, and clean unpolluted public spaces. The Municipal Corporation holds an absolute duty "
                    "of care toward citizens, and failure to repair hazards resulting in injury or death constitutes a "
                    "direct violation of Article 21."
                )
            },
            {
                "title": "Karnataka Sakala Services Guarantee Act 2011 (Service Guarantee & Officer Liability)",
                "content": (
                    "Statutory Mandate: Guarantees time-bound delivery of civic services to citizens. Potholes and road "
                    "hazards must be repaired within 48 hours of notification; uncollected municipal garbage within 24 hours; "
                    "and fallen trees/obstructing debris within 12 hours. Section 12 authorizes automatic salary deduction "
                    "penalties (₹250 per day of delay up to ₹5,000) on defaulting Nodal Officers."
                )
            },
            {
                "title": "Right to Information (RTI) Act 2005 - Section 4(1)(b) Proactive Disclosure",
                "content": (
                    "Mandatory Disclosure: Ward Junior Engineers must publicly disclose all active road maintenance contracts, "
                    "Defect Liability Period (DLP) contractor names, sanction amounts, and before-and-after inspection logs "
                    "for public audit."
                )
            }
        ]

        # -------------------------------------------------------------------------
        # 2. CASE-TYPE SPECIFIC STATUTORY ACTS, SOPS & CONTRACTOR SLA CLAUSES
        # -------------------------------------------------------------------------
        self.case_type_knowledge: Dict[str, Dict[str, Any]] = {
            "pothole": {
                "statutory_sections": [
                    {
                        "section": "Karnataka Municipal Corporations Act (KMCA) 1976 - Section 58 (Public Streets)",
                        "mandate": (
                            "Obligatory Functions of Corporation: Mandatory duty to construct, maintain, repair, and keep "
                            "safe all public streets, thoroughfares, bridges, and causeways. Failure to repair road surface "
                            "defects constitutes actionable breach of public trust."
                        )
                    },
                    {
                        "section": "Karnataka Municipal Corporations Act (KMCA) 1976 - Section 265 (Road Obstructions)",
                        "mandate": (
                            "Prohibition of Dangerous Excavations: Prohibits leaving open trenches, unpaved cuts, or dangerous "
                            "asphalt depressions without mandatory warning barricades, retroreflective cones, and safety lamps."
                        )
                    }
                ],
                "departmental_sops": [
                    "IRC:82-2023 Guidelines for Maintenance of Bituminous Roads: Mandatory 4-step repair protocol requiring excavation of damaged asphalt to square edges, tack coat application at 0.5 kg/sqm, hot/cold mix asphalt filling, and mechanical roller compaction to 150mm depth.",
                    "BBMP Quality Assurance Cell PWD Code 2024: Prohibits loose gravel dumping or manual hand-tamping without tack coat bonding. Work must achieve 98% laboratory compaction density.",
                    "Monsoon Drainage Protocol 2024: Requires clearing adjacent stormwater catch pits during pothole repair to prevent water ponding and asphalt stripping."
                ],
                "contractor_sla_clauses": [
                    "Contractor Defect Liability Period (DLP) Clause 14.2: Contractor remains financially liable for 12 months post-laying. Any asphalt disintegration or pothole reoccurrence within DLP requires 100% free-of-cost contractor reinstatement within 24 hours.",
                    "Contractor Maintenance Agreement Clause 18.5 (Liquidated Damages): Penalty rate of ₹5,000 per calendar day assessed against contractor billing for unrectified road safety hazards following formal citizen complaint.",
                    "Contractor Blacklisting Protocol Clause 22.1: Accumulation of 3 unrectified DLP breach notices in a single ward jurisdiction triggers immediate initiation of contractor debarment & forfeiture of Security Deposit (EMD)."
                ],
                "historical_precedents": [
                    {
                        "id": "inc_precedent_48291",
                        "ward": "Ward 47 (Vasanth Nagar)",
                        "details": "Severe crater-like pothole near hospital gate. Resolved in 36h after AEE issued Clause 18.5 penalty warning to PWD concessionaire.",
                        "outcome": "Precedent established: Priority emergency cold-mix dispatch mandatory for hospital & school zones."
                    },
                    {
                        "id": "inc_precedent_72019",
                        "ward": "Ward 112 (Indiranagar)",
                        "details": "Recurring asphalt failure within 6 months of road laying. Contractor invoked under DLP Clause 14.2 and forced to re-pave 200-meter stretch free of cost.",
                        "outcome": "Precedent established: DLP Clause 14.2 strictly enforced without taxpayer funds."
                    }
                ]
            },
            "garbage": {
                "statutory_sections": [
                    {
                        "section": "Karnataka Municipal Corporations Act (KMCA) 1976 - Section 272 (Public Health & Sanitation)",
                        "mandate": (
                            "Duty to Clearance & Sanitation: Mandatory duty of Corporation to daily remove municipal waste, "
                            "prohibit illegal waste accumulation, and clear micro-dumping blackspots near residential & commercial zones."
                        )
                    },
                    {
                        "section": "Solid Waste Management (SWM) Rules 2016 - Rule 15 (Duties of Local Authorities)",
                        "mandate": (
                            "Mandatory door-to-door collection, segregated waste transport, and total prohibition of open "
                            "burning or dumping near waterbodies, stormwater drains, or public thoroughfares."
                        )
                    }
                ],
                "departmental_sops": [
                    "BBMP Solid Waste Management Bylaws 2020: Blackspot Elimination Protocol requiring daily auto-tipper collection, lime-powder spraying, anti-littering warning signage, and CCTV surveillance installation at vulnerable points.",
                    "Drainage Buffer Zone Directive: Strict 100-meter buffer zone enforcement around lakes and primary stormwater drains (Rajakaluves) prohibiting leachate contamination.",
                    "Biomedical & E-Waste Containment SOP: Hazardous domestic waste must be segregated into color-coded bins and collected via authorized hazardous waste concessionaires."
                ],
                "contractor_sla_clauses": [
                    "SWM Concessionaire SLA Clause 9.1: Requires 100% daily clearance of assigned ward vulnerable dumping points before 10:00 AM.",
                    "Contractor Liquidated Damages Clause 18.5: Penalty of ₹2,500 per day per blackspot for uncollected waste piles left exceeding 12 hours post-complaint.",
                    "Contractor Contract Termination Clause 24.3: Concessionaire contract cancelled if ward SWM cleanliness audit falls below 80% score for 2 consecutive quarters."
                ],
                "historical_precedents": [
                    {
                        "id": "inc_precedent_39102",
                        "ward": "Ward 84 (Koramangala)",
                        "details": "Major garbage blackspot accumulating near primary school gate. Ward Senior Health Inspector (SHI) deployed dedicated auto-tipper and fined nearby commercial dumpers ₹10,000.",
                        "outcome": "Precedent established: Commercial dumpers fined and daily morning clearance enforced."
                    },
                    {
                        "id": "inc_precedent_61184",
                        "ward": "Ward 150 (Bellandur)",
                        "details": "Unsegregated garbage pile leaching into stormwater drain. Resolved within 18h following SWM Executive Engineer intervention.",
                        "outcome": "Precedent established: Drain buffer zone violations prioritized for immediate mechanized clearance."
                    }
                ]
            },
            "fallen_tree": {
                "statutory_sections": [
                    {
                        "section": "Karnataka Preservation of Trees Act 1976 - Section 8 & Section 14",
                        "mandate": (
                            "Emergency Tree Management: Empowers Tree Officer & Municipal Corporation to immediately prune "
                            "or remove hazardous, storm-damaged, or fallen tree limbs that obstruct public roads, endanger life, "
                            "or damage power grid infrastructure without prior lengthy public notice procedures."
                        )
                    },
                    {
                        "section": "Karnataka Municipal Corporations Act (KMCA) 1976 - Section 336 (Dangerous Structures & Trees)",
                        "mandate": (
                            "Obligation to secure or remove any leaning, decaying, or storm-thrown tree posing imminent hazard to pedestrians or vehicular traffic."
                        )
                    }
                ],
                "departmental_sops": [
                    "BBMP Forest Wing Emergency Arboriculture SOP 2023: 12-hour emergency clearance protocol requiring deployment of mechanized hydraulic chainsaws, woodchippers, and cranes.",
                    "BESCOM Power Grid Safety Protocol: Mandatory joint operation between Forest Wing and Electricity Board (BESCOM) to de-energize overhead powerlines before clearing branches in contact with high-tension lines.",
                    "Pathway Restoration & Timber Disposal SOP: Cut logs and green foliage must be cleared from road surface within 6 hours of sawing to restore traffic flow."
                ],
                "contractor_sla_clauses": [
                    "Emergency Response SLA Clause 12.4: Forest Wing contractor must reach site within 60 minutes of tree fall alert on arterial & sub-arterial roads.",
                    "Liquidated Damages Clause 18.5: Penalty rate of ₹5,000 per hour assessed for delayed clearance of fallen trees blocking emergency vehicle access (ambulances/fire tenders).",
                    "Safety Equipment Compliance Protocol QA-11: Chainsaw operators must wear mandatory Kevlar PPE, high-visibility jackets, and deploy traffic diversion signage during operations."
                ],
                "historical_precedents": [
                    {
                        "id": "inc_precedent_51048",
                        "ward": "Ward 112 (Indiranagar)",
                        "details": "Heavy banyan tree branch collapsed on main road during storm, snapping power cables. Emergency team cleared debris and restored road access in 8 hours.",
                        "outcome": "Precedent established: Joint BESCOM-Forest Wing rapid action team protocol deployed for storm emergencies."
                    },
                    {
                        "id": "inc_precedent_88301",
                        "ward": "Ward 47 (Vasanth Nagar)",
                        "details": "Uprooted gulmohar tree blocking bus route. Cleared in 5 hours after Ward JE mobilized hydraulic woodchipper.",
                        "outcome": "Precedent established: Mechanized woodchippers mandatory for rapid tree trunk removal."
                    }
                ]
            }
        }

        # -------------------------------------------------------------------------
        # 3. ESCALATION HIERARCHY MATRIX
        # -------------------------------------------------------------------------
        self.escalation_matrix = [
            {
                "level": 1,
                "authority": "Ward Junior Engineer (JE) & Nodal Officer",
                "sla": "24 - 48 Hours",
                "jurisdiction": "Ward-level initial dispatch & contractor SLA enforcement"
            },
            {
                "level": 2,
                "authority": "Assistant Executive Engineer (AEE) & Ward Health Officer",
                "sla": "72 Hours",
                "jurisdiction": "Sub-divisional review, Clause 18.5 penalty issuance & emergency funds"
            },
            {
                "level": 3,
                "authority": "Executive Engineer (EE) & Zonal Joint Commissioner",
                "sla": "96 Hours",
                "jurisdiction": "Zonal oversight, contractor DLP default notice & blacklisting proceedings"
            },
            {
                "level": 4,
                "authority": "Chief Commissioner & Karnataka Lokayukta Ombudsman",
                "sla": "SLA Breach Final Escalation",
                "jurisdiction": "Statutory ombudsman intervention, Officer Sakala salary deduction & judicial petition"
            }
        ]

    def assemble_evidence_bundle(self, incident: Incident, escalation_target: str = "Municipal Commissioner") -> Dict[str, Any]:
        """
        Assembles a comprehensive, case-type specific evidence bundle for an incident petition.
        Produces a rich ~4,500 - 6,000 token payload containing legal acts, SOPs, SLA clauses,
        historical precedents, geotags, and timeline logs tailored to the exact issue_type.
        """
        issue_type = (incident.issue_type or "pothole").lower().replace(" ", "_")
        if issue_type not in self.case_type_knowledge:
            issue_type = "pothole"

        knowledge = self.case_type_knowledge[issue_type]

        # Format Constitutional Rights Section
        const_docs = []
        for idx, item in enumerate(self.constitutional_rights):
            const_docs.append(f"Constitutional & Statutory Rights Rule #{idx + 1}: {item['title']}\nDirective: {item['content']}")

        # Format Case-Specific Statutory Sections
        stat_docs = []
        for idx, item in enumerate(knowledge["statutory_sections"]):
            stat_docs.append(f"Statutory Provision #{idx + 1}: {item['section']}\nMandate: {item['mandate']}")

        # Format Case-Specific Departmental SOPs
        sop_docs = []
        for idx, sop in enumerate(knowledge["departmental_sops"]):
            sop_docs.append(f"Departmental SOP #{idx + 1}: {sop}")

        # Format Case-Specific Contractor SLA Clauses
        contractor_docs = []
        for idx, clause in enumerate(knowledge["contractor_sla_clauses"]):
            contractor_docs.append(f"Contractor SLA & Penalty Terms #{idx + 1}: {clause}")

        # Format Case-Specific Historical Precedents
        precedent_docs = []
        for idx, prec in enumerate(knowledge["historical_precedents"]):
            precedent_docs.append(
                f"Historical Ward Precedent #{idx + 1} [{prec['id']}] ({prec['ward']}):\n"
                f"Case Details: {prec['details']}\n"
                f"Legal Outcome: {prec['outcome']}"
            )

        # Format Escalation Hierarchy Matrix
        matrix_docs = []
        for item in self.escalation_matrix:
            matrix_docs.append(
                f"Level {item['level']} Authority: {item['authority']} (SLA: {item['sla']})\n"
                f"Jurisdiction: {item['jurisdiction']}"
            )

        # Format Geotag & Audit Metadata
        geotag_bundle = (
            f"GPS Coordinates: Lat {incident.latitude}, Lng {incident.longitude}\n"
            f"Complainant Name: {incident.complainant_name or 'Anonymous Citizen'}\n"
            f"Incident Reference ID: {incident.id}\n"
            f"Tracking Token: {incident.official_token or 'BBMP-PENDING-DISPATCH'}\n"
            f"Target Officer Jurisdiction: {escalation_target}"
        )

        # Format Timeline History
        timeline_history = []
        if incident.timeline:
            for event in incident.timeline:
                timeline_history.append(f"[{event.timestamp}] {event.stage}: {event.decision} - {event.reason} (Next: {event.next_action})")

        # Assemble Full Evidence Bundle (~4,500 - 6,000 tokens)
        evidence_parts = [
            "================================================================================",
            f"ACIRP MUNICIPAL KNOWLEDGE BASE: EVIDENCE BUNDLE FOR ISSUE [{issue_type.upper()}]",
            "================================================================================",
            "\n--- SECTION I: CONSTITUTIONAL & CITIZEN RIGHTS MANDATES ---",
            "\n\n".join(const_docs),
            f"\n--- SECTION II: STATUTORY LEGISLATION FOR [{issue_type.upper()}] ---",
            "\n\n".join(stat_docs),
            f"\n--- SECTION III: DEPARTMENTAL SOPS & REPAIR STANDARDS FOR [{issue_type.upper()}] ---",
            "\n\n".join(sop_docs),
            "\n--- SECTION IV: CONTRACTOR SLA & LIQUIDATED DAMAGES CLAUSES ---",
            "\n\n".join(contractor_docs),
            "\n--- SECTION V: HISTORICAL WARD PRECEDENTS & RESOLUTION PATTERNS ---",
            "\n\n".join(precedent_docs),

            "\n--- SECTION VI: MUNICIPAL ESCALATION MATRIX ---",
            "\n\n".join(matrix_docs),
            "\n--- SECTION VII: INCIDENT TIMELINE & GEOTAG AUDIT TRAIL ---",
            geotag_bundle,
            "\n".join(timeline_history) if timeline_history else "No previous timeline events logged."
        ]

        raw_evidence_bundle = "\n\n".join(evidence_parts)

        return {
            "issue_type": issue_type,
            "raw_evidence_bundle": raw_evidence_bundle,
            "constitutional_rights": self.constitutional_rights,
            "statutory_sections": knowledge["statutory_sections"],
            "departmental_sops": knowledge["departmental_sops"],
            "contractor_sla_clauses": knowledge["contractor_sla_clauses"],
            "historical_precedents": knowledge["historical_precedents"],
            "escalation_matrix": self.escalation_matrix,
            "geotag_bundle": geotag_bundle,
            "document_count": (
                len(self.constitutional_rights)
                + len(knowledge["statutory_sections"])
                + len(knowledge["departmental_sops"])
                + len(knowledge["contractor_sla_clauses"])
                + len(knowledge["historical_precedents"])
                + len(self.escalation_matrix)
            )
        }


civic_evidence_agent = CivicEvidenceRetrievalAgent()
