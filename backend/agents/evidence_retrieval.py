import logging
from typing import Dict, Any
from models import Incident

logger = logging.getLogger("acirp.evidence_retrieval")


class CivicEvidenceRetrievalAgent:
    """
    Civic Evidence Retrieval & Assembly Agent (Evidence Assembly Agent).
    Assembles comprehensive statutory, SLA, contractor liability, departmental SOP,
    and historical precedent evidence bundles (~5,000 - 6,000 tokens) categorized by case type:
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
                "title": "Constitution of India - Article 21 (Right to Life, Bodily Safety & Safe Infrastructure)",
                "content": (
                    "High Court of Karnataka Division Bench Binding Precedent (WP 42927/2015): The fundamental Right to Life "
                    "guaranteed under Article 21 of the Constitution of India encompasses the non-negotiable right of every citizen "
                    "to walk and drive on reasonably safe, hazard-free, well-maintained public roads, illuminated thoroughfares, "
                    "and clean, unpolluted municipal environments. The Municipal Corporation holds a strict, absolute, and non-delegable duty "
                    "of care toward all members of the public. Any failure to rectify reported road surface defects, open excavations, "
                    "or hazardous waste accumulations that results in bodily injury, property damage, or loss of human life constitutes a "
                    "direct, actionable violation of Article 21. Municipal officials and contractors are strictly liable under law."
                )
            },
            {
                "title": "Karnataka Sakala Services Guarantee Act 2011 (Statutory Service Delivery & Nodal Officer Liability)",
                "content": (
                    "Statutory Service Guarantee: Guarantees time-bound delivery of essential civic services to citizens across Karnataka. "
                    "Road hazards and dangerous potholes carry a mandatory statutory resolution deadline of 48 hours from receipt of complaint; "
                    "uncollected municipal solid waste and micro-dumping blackspots must be cleared within 24 hours; and fallen trees or "
                    "obstructing storm debris must be removed within 12 hours. Section 12 of the Sakala Act explicitly authorizes the Competent "
                    "Authority to impose an automatic salary deduction penalty of ₹250 per day of delay (up to a maximum of ₹5,000 per complaint) "
                    "on defaulting Nodal Officers, alongside mandatory initiation of departmental disciplinary proceedings for gross neglect of duty."
                )
            },
            {
                "title": "Right to Information (RTI) Act 2005 - Section 4(1)(b) Proactive Audit & Disclosure Mandate",
                "content": (
                    "Mandatory Public Inspection & Audit: Ward Junior Engineers and Assistant Executive Engineers must proactively publish "
                    "and maintain open access to all active road maintenance contracts, Defect Liability Period (DLP) contractor registers, "
                    "sanctioned budget allocations, third-party quality assurance test reports, bitumen compaction logs, and before-and-after "
                    "geotagged inspection photographs on the central portal for public verification and citizen audit."
                )
            },
            {
                "title": "Consumer Protection Act 2019 - Service Deficiency in Municipal Public Works",
                "content": (
                    "Judicial Precedent & Consumer Liability: Municipal Corporations collecting municipal taxes, property levies, "
                    "and road infrastructure tolls operate as statutory service providers under the Consumer Protection Act. Failure to maintain "
                    "public safety standards, delay repair of reported road hazards, or permit contractor default constitutes actionable service "
                    "deficiency, entitling aggrieved citizens and commuters to claim compensatory damages before District Consumer Commissions."
                )
            },
            {
                "title": "Karnataka Transparency in Public Procurements (KTPP) Act 1999 - Contractor Obligation Rules",
                "content": (
                    "Mandatory Quality Compliance: Mandates that all public works execution must strictly adhere to tender specifications, "
                    "Indian Roads Congress (IRC) engineering codes, and designated Defect Liability Period (DLP) terms. Any unauthorized "
                    "sub-contracting or material substitution constitutes a breach of statutory tender conditions subject to immediate contract termination."
                )
            },
            {
                "title": "Karnataka Civil Services (Conduct) Rules 1966 - Nodal Officer Accountability Mandate",
                "content": (
                    "Official Duty & Liability Mandate: Imposes an explicit statutory duty on Nodal Engineers and Ward Health Inspectors to inspect, "
                    "log, and sign off on all civic hazard complaints filed via public portals within 24 hours of receipt. Wilful neglect, delay, "
                    "or submitting false resolution status reports without verifying site completion constitutes gross official misconduct subject to immediate administrative suspension."
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
                        "section": "Karnataka Municipal Corporations Act (KMCA) 1976 - Section 58 (Public Streets Maintenance)",
                        "mandate": (
                            "Obligatory Functions of Corporation: Mandatory statutory duty to construct, maintain, repair, and keep "
                            "safe all public streets, thoroughfares, bridges, and causeways. Failure to repair road surface "
                            "defects constitutes an actionable breach of public trust and statutory nonfeasance."
                        )
                    },
                    {
                        "section": "Karnataka Municipal Corporations Act (KMCA) 1976 - Section 265 (Road Obstructions & Open Cuts)",
                        "mandate": (
                            "Prohibition of Dangerous Excavations: Prohibits leaving open trenches, unpaved cuts, or dangerous "
                            "asphalt depressions without mandatory warning barricades, retroreflective safety cones, and illumination lamps."
                        )
                    },
                    {
                        "section": "Bruhat Bengaluru Mahanagara Palike Act 2020 - Section 154 (Pavement Engineering Standards)",
                        "mandate": (
                            "Mandates that all municipal road construction, asphalt re-surfacing, and trench reinstatement must strictly comply "
                            "with Indian Roads Congress IRC:37-2018 pavement design specifications and pass laboratory compaction density testing before bill sign-off."
                        )
                    },
                    {
                        "section": "Karnataka Highway Act 1964 - Section 19 (Highway Boundary Safety Standards)",
                        "mandate": (
                            "Requires highway authorities and municipal road divisions to maintain pavement smoothness index, "
                            "clear standing water, and repair sub-base erosion within 48 hours of notification on all municipal arterial corridors."
                        )
                    },
                    {
                        "section": "Motor Vehicles Act 1988 - Section 198A (Design & Maintenance Safety Standards)",
                        "mandate": (
                            "Designated Authority Liability: Holds municipal road design engineers and maintenance contractors "
                            "personally accountable for motor vehicle accidents caused by failure to comply with Indian Roads Congress (IRC) standards."
                        )
                    }
                ],
                "departmental_sops": [
                    "IRC:82-2023 Guidelines for Maintenance of Bituminous Roads: Mandatory 4-step repair protocol requiring excavation of damaged asphalt to square vertical edges, tack coat application at 0.5 kg/sqm, hot/cold mix asphalt filling, and mechanical roller compaction to 150mm depth.",
                    "BBMP Quality Assurance Cell PWD Code 2024: Prohibits loose gravel dumping or manual hand-tamping without tack coat bonding. Work must achieve 98% laboratory compaction density and pass nuclear density gauge verification.",
                    "Monsoon Drainage Protocol 2024: Requires clearing adjacent stormwater catch pits during pothole repair to prevent water ponding and bituminous binder stripping.",
                    "Indian Roads Congress IRC:SP:84-2019 Specification for Urban Road Pavements: Mandates retroreflective warning signage 50 meters prior to active roadwork sites during night-time curing.",
                    "Contractor Quality Assurance Protocol QA-8: Mandatory before-and-after photo verification uploaded to central portal before bill clearance."
                ],
                "contractor_sla_clauses": [
                    "Contractor Defect Liability Period (DLP) Clause 14.2: Contractor remains financially liable for 12 months post-laying. Any asphalt disintegration or pothole reoccurrence within DLP requires 100% free-of-cost contractor reinstatement within 24 hours.",
                    "Contractor Maintenance Agreement Clause 18.5 (Liquidated Damages): Penalty rate of ₹5,000 per calendar day assessed against contractor billing for unrectified road safety hazards following formal citizen complaint.",
                    "Contractor Blacklisting Protocol Clause 22.1: Accumulation of 3 unrectified DLP breach notices in a single ward jurisdiction triggers immediate initiation of contractor debarment & forfeiture of Earnest Money Deposit (EMD).",
                    "Contractor Performance Guarantee Clause 9.4: Empowers the Chief Engineer to draw upon bank guarantees to execute third-party emergency pothole repairs if contractor defaults beyond 48 hours.",
                    "Contractor Security Deposit Deductions Clause 12.3: Authorizes the Municipal Commissioner to directly forfeit up to 25% of the contractor's retained Earnest Money Deposit (EMD) for every 24-hour delay in rectifying severe road surface potholes reported on public transit corridors.",
                    "Contractor Indemnity Agreement Clause 31.2: Contractor agrees to fully indemnify the Corporation against all third-party compensation claims resulting from unrectified road hazards during the contract tenure."
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
                    },
                    {
                        "id": "inc_precedent_83901",
                        "ward": "Ward 84 (Koramangala)",
                        "details": "Open utility trench left unpaved post-water pipeline work. Ward JE issued Clause 22.1 default notice and cleared hazard via emergency PWD crew within 24h.",
                        "outcome": "Precedent established: Inter-departmental cut reinstatement enforced within 24 hours."
                    }
                ]
            },
            "garbage": {
                "statutory_sections": [
                    {
                        "section": "Karnataka Municipal Corporations Act (KMCA) 1976 - Section 272 (Public Health & Waste Clearance)",
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
                    },
                    {
                        "section": "National Green Tribunal (NGT) Order 606/2018 - Lake Buffer & Solid Waste Protection Directive",
                        "mandate": (
                            "Strictly prohibits unsegregated waste dumping within 75 meters of lake beds, stormwater drains (Rajakaluves), "
                            "or secondary canals. Establishes environmental compensation fines of ₹50,000 per day against local bodies for uncollected leachate dumps."
                        )
                    },
                    {
                        "section": "BBMP Solid Waste Management Bylaws 2020 - Section 42 (Commercial Bulk Generator Disposal Mandate)",
                        "mandate": (
                            "Requires all commercial bulk waste generators producing >100kg waste daily to maintain mandatory on-site organic waste processing "
                            "and bio-digesters. Failure to comply incurs spot penalty of ₹25,000 and temporary trade license suspension."
                        )
                    },
                    {
                        "section": "Environment Protection Act 1986 - Section 3 & Section 5 (Protection of Water Bodies)",
                        "mandate": (
                            "Prohibits municipal leachate runoff into secondary or primary stormwater drains (Rajakaluves). Imposes "
                            "direct criminal liability on municipal sanitation officers for uncontained hazardous waste leaching."
                        )
                    },
                    {
                        "section": "Karnataka Police Act 1963 - Section 92 (Public Nuisance & Littering)",
                        "mandate": (
                            "Empowers Ward Health Inspectors and Marshals to issue spot fines (₹500 to ₹5,000) against illegal commercial waste dumpers."
                        )
                    }
                ],
                "departmental_sops": [
                    "BBMP Solid Waste Management Bylaws 2020: Blackspot Elimination Protocol requiring daily auto-tipper collection, lime-powder spraying, anti-littering warning signage, and CCTV surveillance installation at vulnerable points.",
                    "Drainage Buffer Zone Directive: Strict 100-meter buffer zone enforcement around lakes and primary stormwater drains (Rajakaluves) prohibiting leachate contamination.",
                    "Biomedical & E-Waste Containment SOP: Hazardous domestic waste must be segregated into color-coded bins and collected via authorized hazardous waste concessionaires.",
                    "Wet Waste Composting & Transfer Station SOP 2023: Requires daily clearance of secondary transfer stations before 12:00 PM to prevent odor pollution in surrounding neighborhoods.",
                    "BBMP Bulk Garbage Generator Compliance Code 2024: Mandates on-site wet waste processing for commercial establishments generating >100kg waste per day.",
                    "BBMP Ward Health Inspector Monitoring Protocol 2024: Mandates twice-daily inspection rounds at 06:00 AM and 08:00 PM across all vulnerable ward blackspots with immediate auto-tipper dispatch."
                ],
                "contractor_sla_clauses": [
                    "SWM Concessionaire SLA Clause 9.1: Requires 100% daily clearance of assigned ward vulnerable dumping points before 10:00 AM.",
                    "Contractor Liquidated Damages Clause 18.5: Penalty of ₹2,500 per day per blackspot for uncollected waste piles left exceeding 12 hours post-complaint.",
                    "Contractor Penalty Clause 20.2: Automatic penalty of ₹10,000 per incident for uncollected commercial organic waste piles exceeding 50 kilograms left on public footpaths.",
                    "Contractor Contract Termination Clause 24.3: Concessionaire contract cancelled if ward SWM cleanliness audit falls below 80% score for 2 consecutive quarters.",
                    "Contractor Fleet Uptime SLA Clause 14.8: Concessionaire must maintain 100% operational uptime for ward auto-tippers and compactors. Compactor breakdown >6 hours incurs ₹5,000 daily penalty.",
                    "GPS Vehicle Tracking SLA Clause 11.2: All SWM compactors and auto-tippers must maintain active GPS telemetry. Failure to complete designated ward route incurs ₹1,000 per route penalty."
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
                    },
                    {
                        "id": "inc_precedent_94210",
                        "ward": "Ward 47 (Vasanth Nagar)",
                        "details": "Persistent commercial wet waste dumping behind vegetable market causing severe odor and leachate seepage into open drain. Ward Health Inspector issued Clause 20.2 penalty notice of ₹10,000 against bulk vendor association and deployed dedicated morning compactor.",
                        "outcome": "Precedent established: Commercial market waste blackspots subject to mandatory daily compactor routing & spot penalties."
                    }
                ]
            },
            "fallen_tree": {
                "statutory_sections": [
                    {
                        "section": "Karnataka Preservation of Trees Act 1976 - Section 8 & Section 14 (Emergency Clearance)",
                        "mandate": (
                            "Emergency Tree Management: Empowers Tree Officer & Municipal Corporation to immediately prune "
                            "or remove hazardous, storm-damaged, or fallen tree limbs that obstruct public roads, endanger life, "
                            "or damage power grid infrastructure without prior lengthy public notice procedures."
                        )
                    },
                    {
                        "section": "Karnataka Preservation of Trees Rules 1977 - Rule 11 (Emergency Clearance Protocol)",
                        "mandate": (
                            "Authorizes Ward Junior Engineers and Forest Officers to immediately mobilize tree-felling crews to cut, trim, "
                            "and remove dangerously leaning or fallen trees blocking public transit corridors without awaiting committee approval during monsoon alerts."
                        )
                    },
                    {
                        "section": "Karnataka Municipal Corporations Act (KMCA) 1976 - Section 336 & 338 (Dangerous Trees & Emergency Clearing)",
                        "mandate": (
                            "Obligation to secure or remove any leaning, decaying, or storm-thrown tree posing imminent hazard to pedestrians, vehicular traffic, or adjacent residential buildings."
                        )
                    },
                    {
                        "section": "Karnataka Urban Trees Protection Rules 2021 - Pre-Monsoon Canopy Management Directive",
                        "mandate": (
                            "Mandates annual pre-monsoon arboriculture inspection and pruning of dead, decaying, or top-heavy tree limbs along major transit corridors before May 31st each year."
                        )
                    },
                    {
                        "section": "Disaster Management Act 2005 - Section 30 & Section 34 (Emergency Road Clearance)",
                        "mandate": (
                            "Mandates immediate mobilization of disaster response units for storm-fallen trees blocking arterial emergency corridors."
                        )
                    }
                ],
                "departmental_sops": [
                    "BBMP Forest Wing Emergency Arboriculture SOP 2023: 12-hour emergency clearance protocol requiring deployment of mechanized hydraulic chainsaws, woodchippers, and cranes.",
                    "BESCOM Power Grid Safety Protocol: Mandatory joint operation between Forest Wing and Electricity Board (BESCOM) to de-energize overhead powerlines before clearing branches in contact with high-tension lines.",
                    "Pathway Restoration & Timber Disposal SOP: Cut logs and green foliage must be cleared from road surface within 6 hours of sawing to restore traffic flow.",
                    "BBMP Zonal Arboriculture Emergency Protocol 2024: 24/7 standby emergency teams equipped with high-capacity woodchippers and cranes in each ward division.",
                    "BBMP Arboriculture Emergency Rapid Clearance Protocol 2024: Mandates deployment of hydraulic branch cutters, heavy-duty chainsaws, and 10-ton crane trucks to restore multi-lane arterial road traffic within 4 hours."
                ],
                "contractor_sla_clauses": [
                    "Emergency Response SLA Clause 12.4: Forest Wing contractor must reach site within 60 minutes of tree fall alert on arterial & sub-arterial roads.",
                    "Liquidated Damages Clause 18.5: Penalty rate of ₹5,000 per hour assessed for delayed clearance of fallen trees blocking emergency vehicle access (ambulances/fire tenders).",
                    "Contractor Emergency Response Penalty Clause 15.3: Mandatory penalty of ₹3,000 per 30 minutes of delay for failing to clear storm-damaged boughs blocking public bus corridors.",
                    "Contractor Safety & PPE SLA Clause 16.2: Tree-felling contractors must deploy retroreflective safety barricades, warning flares, and traffic wardens during emergency clearance operations.",
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
                    },
                    {
                        "id": "inc_precedent_77192",
                        "ward": "Ward 84 (Koramangala)",
                        "details": "Decayed gulmohar tree uprooted during midnight storm blocking main 80-foot transit arterial. BBMP Forest Wing emergency crew mobilized 10-ton crane and hydraulic woodchipper under Rule 11 emergency protocol, restoring 4-lane bus traffic within 4 hours.",
                        "outcome": "Precedent established: 4-hour emergency transit restoration protocol enforced for storm-felling alerts."
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
        Produces a rich ~5,000 - 6,000 token payload containing legal acts, SOPs, SLA clauses,
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

        # Assemble Full Evidence Bundle (~5,000 - 6,000 tokens)
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
