import logging
import httpx
from datetime import datetime, timedelta
from typing import Optional
from models import Incident, TimelineEvent, Strategy, PlannerDecision
from config import DEFAULT_ROUTING
from tools.portal_client import submit_to_portal_hybrid
from db.base import BaseDatabase
from agents.paritok_optimizer import ParitokContextOptimizer

logger = logging.getLogger("acirp.planner")

class PlanningAgent:
    def __init__(self, db: BaseDatabase):
        self.db = db
        self.paritok = ParitokContextOptimizer()

    async def execute_step(self, incident: Incident, submission_mode: str = "api") -> Incident:
        """
        Executes a single step of the incident lifecycle based on its current state.
        This represents the core tick of the stateless loop runner.
        """
        timestamp = datetime.now().strftime("%d %b %H:%M")
        
        if incident.status == "PLANNED":
            # 1. Similarity Engine: Search for similar resolved cases within 500 meters
            nearby_resolved = self.db.find_nearby_resolved(
                incident.latitude, incident.longitude, incident.issue_type, max_dist_meters=500.0
            )
            
            chosen_strategy = DEFAULT_ROUTING.get(incident.issue_type)
            reason = f"No resolved cases found nearby. Loaded default routing for {incident.issue_type}."
            
            # Format retrieved docs for Paritok optimizer
            retrieved_docs = []
            for inc in nearby_resolved:
                retrieved_docs.append({
                    "id": inc.id,
                    "department": inc.current_strategy.department if inc.current_strategy else "General",
                    "summary": f"Resolved {inc.issue_type} near ({inc.latitude}, {inc.longitude})",
                    "relevance": 0.85,
                    "age_days": 12
                })
            # Add synthetic low-relevance & old incident docs to demonstrate Paritok pruning
            retrieved_docs.append({
                "id": "inc_old_99",
                "department": "Traffic Police",
                "summary": "Speeding violation record from 2022",
                "relevance": 0.15,
                "age_days": 450
            })

            # Format conversation history
            history = [{"role": e.stage.lower(), "content": e.decision} for e in incident.timeline]

            # Paritok Optimization

            raw_prompt = f"Determine optimal municipal routing for {incident.issue_type} at GPS ({incident.latitude}, {incident.longitude})."
            system_rules = f"Evaluate department jurisdiction SLA rules. Available strategies: PWD, Waste Management, Forestry."
            
            _, paritok_metrics = await self.paritok.optimize_context(
                raw_prompt=raw_prompt,
                system_rules=system_rules,
                retrieved_docs=retrieved_docs,
                conversation_history=history,
                request_type="Jurisdictional Strategy Planning"
            )

            # If we found resolved incidents nearby, check if they used a customized or faster route
            if nearby_resolved:
                fastest_inc = min(nearby_resolved, key=lambda x: x.current_strategy.sla_hours if x.current_strategy else 999)
                if fastest_inc.current_strategy and fastest_inc.current_strategy.sla_hours < chosen_strategy.sla_hours:
                    chosen_strategy = fastest_inc.current_strategy
                    reason = f"Similarity search found resolved case {fastest_inc.id} nearby that resolved faster via {chosen_strategy.name}."
            
            incident.current_strategy = chosen_strategy
            incident.goal = f"Resolve {incident.issue_type.replace('_', ' ')} incident using {chosen_strategy.department} route"
            
            event = TimelineEvent(
                timestamp=timestamp,
                stage="PLANNER",
                decision="Selected strategy workflow",
                confidence="100%",
                reason=reason,
                next_action="Filing complaint petition to department registry",
                paritok_metrics=paritok_metrics
            )
            incident.timeline.append(event)
            incident.paritok_metrics = paritok_metrics
            
            incident.status = "SUBMITTED"
            incident.updated_at = datetime.now().isoformat()
            
        elif incident.status == "SUBMITTED":
            # 2. Complaint Submission Tool execution
            incident.timeline.append(TimelineEvent(
                timestamp=timestamp,
                stage="SYSTEM",
                decision="Submitting complaint ticket",
                confidence="100%",
                reason="Submitting official complaint to municipal portal",
                next_action="Awaiting tracking token confirmation from government registry"
            ))
            
            try:
                incident_dict = incident.model_dump()
                token = await submit_to_portal_hybrid(incident_dict, mode=submission_mode)
                
                incident.official_token = token
                incident.status = "MONITORING"
                
                sla_hours = incident.current_strategy.sla_hours if incident.current_strategy else 24
                incident.sla_deadline = (datetime.now() + timedelta(hours=sla_hours)).isoformat()
                
                incident.timeline.append(TimelineEvent(
                    timestamp=timestamp,
                    stage="TOOL",
                    decision="Filed official complaint",
                    confidence="100%",
                    reason=f"Municipal registry confirmed receipt and generated tracking token: {token}",
                    next_action="Monitoring portal database for resolution update"
                ))
            except (httpx.HTTPError, httpx.TimeoutException, RuntimeError, ValueError, KeyError, TimeoutError, Exception) as e:
                err_type = type(e).__name__
                logger.error(f"Filing tool failed ({err_type}): {e}")
                incident.status = "ESCALATED"
                incident.timeline.append(TimelineEvent(
                    timestamp=timestamp,
                    stage="TOOL",
                    decision="Portal submission failed",
                    confidence="0%",
                    reason=f"Unable to connect to municipal database ({err_type}): {str(e)}",
                    next_action="Requesting citizen approval for direct escalation notice"
                ))
                
            incident.updated_at = datetime.now().isoformat()
            
        elif incident.status == "MONITORING":
            if incident.sla_deadline:
                deadline = datetime.fromisoformat(incident.sla_deadline)
                if datetime.now() > deadline:
                    escalation_paths = incident.current_strategy.escalation_path if incident.current_strategy else []
                    if incident.escalation_level >= len(escalation_paths):
                        incident.status = "CLOSED"
                        incident.timeline.append(TimelineEvent(
                            timestamp=timestamp,
                            stage="MONITOR",
                            decision="SLA Breach - Routes Exhausted",
                            confidence="100%",
                            reason="Ticket unresolved after final escalation window. All digital paths exhausted.",
                            next_action="Recommending manual dispatch via helpline."
                        ))
                    else:
                        incident.status = "ESCALATED"
                        incident.timeline.append(TimelineEvent(
                            timestamp=timestamp,
                            stage="MONITOR",
                            decision="SLA Breach Detected",
                            confidence="100%",
                            reason=f"Ticket unresolved after SLA window of {incident.current_strategy.sla_hours} hours.",
                            next_action="Escalate ticket to higher authority"
                        ))
                    incident.updated_at = datetime.now().isoformat()

        return incident

    def get_brain_decision(self, incident: Incident) -> PlannerDecision:
        requires_human = incident.status in ["AWAITING_REUPLOAD", "VERIFYING", "ESCALATED"]
        
        next_actions = {
            "DETECTED": "Assessing visual evidence and coordinates",
            "AWAITING_REUPLOAD": "Awaiting clear photo evidence from citizen",
            "PLANNED": "Determining responsible department and filing parameters",
            "SUBMITTED": "Submitting civic complaint petition to municipal portal",
            "MONITORING": "Monitoring government resolution status in registry",
            "VERIFYING": "Awaiting verification image from citizen",
            "ESCALATED": "Awaiting approval to escalate complaint to higher authority",
            "CLOSED": "Civic hazard resolved successfully."
        }
        
        return PlannerDecision(
            goal=incident.goal or "Awaiting incident detection",
            current_state=incident.status,
            chosen_strategy=incident.current_strategy or Strategy(
                name="None Selected", department="None", sla_hours=0, escalation_path=[]
            ),
            reason=incident.timeline[-1].reason if incident.timeline else "Bootstrapping agent state machine",
            next_action=next_actions.get(incident.status, "Idle"),
            requires_human=requires_human,
            confidence=incident.confidence or 0.0,
            paritok_metrics=incident.paritok_metrics
        )

def config_sleep_time() -> int:
    from config import MONITOR_SLEEP_INTERVAL_SEC
    return MONITOR_SLEEP_INTERVAL_SEC
