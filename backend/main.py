from fastapi.staticfiles import StaticFiles
from agents.paritok_optimizer import ParitokContextOptimizer, paritok_session
from pydantic import BaseModel as FastAPIModel
import os
import uuid
import logging
from datetime import datetime, timedelta
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import List, Optional

from models import Incident, TimelineEvent, PlannerDecision

from db.factory import get_db
from db.firebase_db import comp_id_context
from config import GEMINI_API_KEY
from agents.perception import PerceptionAgent
from agents.planner import PlanningAgent
from agents.verification import VerificationAgent
from agents.petition_generator import legal_petition_generator


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("acirp.api")

app = FastAPI(title="ACIRP Backend & Simulator API")

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_competition_context(request: Request, call_next):
    # Retrieve the competition context header (defaults to google if not sent)
    comp_id = request.headers.get("x-competition", "google")
    token = comp_id_context.set(comp_id)
    try:
        response = await call_next(request)
    finally:
        comp_id_context.reset(token)
    return response

# Initialize Mock Database & AI Agents
db = get_db()
perception_agent = PerceptionAgent(api_key=GEMINI_API_KEY)
planner_agent = PlanningAgent(db=db)
verification_agent = VerificationAgent(api_key=GEMINI_API_KEY)

# Directory to save mock image files locally
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploaded_images")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory database representing the external Government Portal Tickets
MOCK_PORTAL_TICKETS = {}

# ---------------------------------------------------------
# 1. CORE CITIZEN PORTAL ENDPOINTS
# ---------------------------------------------------------


@app.post("/api/incidents/submit")
async def create_incident(
    latitude: float = Form(...),
    longitude: float = Form(...),
    complainant_name: str = Form("Anonymous Citizen"),
    image: UploadFile = File(...)
):
    """
    Step 1: Citizen uploads incident image.
    Generates incident document, saves image, runs Perception Agent.
    """
    incident_id = f"inc_{uuid.uuid4().hex[:8]}"

    # Save the uploaded file
    file_ext = image.filename.split(".")[-1]
    image_bytes = await image.read()

    # Try to upload to Firebase Storage
    firebase_url = db.upload_image(image_bytes, f"{incident_id}_before.{file_ext}", image.content_type or "image/jpeg")

    # Save a local backup copy
    image_path = os.path.join(UPLOAD_DIR, f"{incident_id}_before.{file_ext}")
    with open(image_path, "wb") as f:
        f.write(image_bytes)

    # Initialize basic incident state
    incident = Incident(
        id=incident_id,
        status="DETECTED",
        complainant_name=complainant_name,
        latitude=latitude,
        longitude=longitude,
        image_before_url=firebase_url if firebase_url else f"/static/{incident_id}_before.{file_ext}"
    )

    # Append initial detection event
    incident.timeline.append(TimelineEvent(
        timestamp=datetime.now().strftime("%d %b %H:%M"),
        stage="SYSTEM",
        decision="Incident upload received",
        confidence="100%",
        reason="Citizen filed new incident with GPS coordinates.",
        next_action="Trigger Perception Agent Vision classifier"
    ))
    # Run the Perception Agent directly (passing the dynamic MIME type)
    incident = await perception_agent.analyze(image_bytes, incident, mime_type=image.content_type or "image/jpeg", filename=image.filename)

    # Run the Planning Agent strategy determination & Paritok RAG optimization
    if incident.status == "PLANNED":
        incident = await planner_agent.execute_step(incident)

    # Save to mock database
    db.save_incident(incident)
    return incident


@app.post("/api/incidents/{incident_id}/verify-resolution")
async def verify_incident_resolution(
    incident_id: str,
    image: UploadFile = File(...)
):
    """
    Step 2: Citizen uploads resolution proof image when portal marks it resolved.
    Triggers Verification Agent to compare before/after images.
    """
    incident = db.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident.status != "VERIFYING":
        raise HTTPException(status_code=400, detail="Incident is not in verification phase")

    # Save resolution file
    file_ext = image.filename.split(".")[-1]
    image_after_bytes = await image.read()

    # Try to upload to Firebase Storage
    firebase_after_url = db.upload_image(
        image_after_bytes, f"{incident_id}_after.{file_ext}", image.content_type or "image/jpeg")

    image_after_path = os.path.join(UPLOAD_DIR, f"{incident_id}_after.{file_ext}")
    with open(image_after_path, "wb") as f:
        f.write(image_after_bytes)

    incident.image_after_url = firebase_after_url if firebase_after_url else f"/static/{incident_id}_after.{file_ext}"

    import mimetypes
    # Read the original before image bytes
    local_files = [f for f in os.listdir(UPLOAD_DIR) if f.startswith(f"{incident_id}_before.")]
    if local_files:
        image_before_path = os.path.join(UPLOAD_DIR, local_files[0])
    else:
        # If it doesn't exist locally (server restarted), download it from the public URL!
        image_before_path = os.path.join(UPLOAD_DIR, f"{incident_id}_before.{file_ext}")
        if incident.image_before_url.startswith("http"):
            try:
                import httpx
                r = httpx.get(incident.image_before_url)
                if r.status_code == 200:
                    with open(image_before_path, "wb") as f:
                        f.write(r.content)
            except Exception as e:
                logger.error(f"Failed to download before image from Firebase: {e}")

    # Determine dynamic MIME types for both files
    before_mime, _ = mimetypes.guess_type(image_before_path)
    if not before_mime:
        before_mime = "image/jpeg"
    after_mime = image.content_type or "image/jpeg"

    with open(image_before_path, "rb") as f:
        image_before_bytes = f.read()

    # Trigger Verification Agent with dynamic MIME types
    incident = await verification_agent.verify(
        image_before_bytes, image_after_bytes, incident,
        before_mime=before_mime, after_mime=after_mime,
        filename=image.filename
    )
    db.save_incident(incident)
    return incident


@app.post("/api/incidents/{incident_id}/approve-escalation")
async def approve_escalation(incident_id: str):
    """
    Step 3: Human-in-the-loop approval to proceed with escalation.
    """
    incident = db.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident.status != "ESCALATED":
        raise HTTPException(status_code=400, detail="Incident does not require escalation approval")

    incident.escalation_level += 1
    escalation_paths = incident.current_strategy.escalation_path if incident.current_strategy else []

    timestamp = datetime.now().strftime("%d %b %H:%M")

    if incident.escalation_level <= len(escalation_paths):
        escalation_target = escalation_paths[incident.escalation_level - 1]

        # Reset status back to monitoring after escalation action
        incident.status = "MONITORING"
        # Grant a fresh 12h SLA window for escalated authority checks
        incident.sla_deadline = (datetime.now() + timedelta(hours=12)).isoformat()

        incident.timeline.append(TimelineEvent(
            timestamp=timestamp,
            stage="ESCALATION",
            decision=f"Escalated to {escalation_target}",
            confidence="100%",
            reason=f"Human approved escalation. Strategy shifting to level {incident.escalation_level}.",
            next_action=f"Monitoring response from {escalation_target}"
        ))
    else:
        # Escalation paths exhausted: suggest direct emergency help
        incident.status = "CLOSED"
        incident.timeline.append(TimelineEvent(
            timestamp=timestamp,
            stage="ESCALATION",
            decision="All escalation routes exhausted",
            confidence="100%",
            reason="Unable to resolve through digital municipal channels.",
            next_action="Recommending user call direct citizen ward helpline."
        ))

    db.save_incident(incident)
    return incident


@app.post("/api/incidents/{incident_id}/re-upload-image")
async def re_upload_image(incident_id: str, image: UploadFile = File(...)):
    """
    Emergency re-upload if perception agent failed to confirm confidence.
    """
    incident = db.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident.status != "AWAITING_REUPLOAD":
        raise HTTPException(status_code=400, detail="Incident not awaiting photo re-upload")

    # Overwrite the original before image
    before_filename = incident.image_before_url.split("/")[-1]
    image_before_path = os.path.join(UPLOAD_DIR, before_filename)

    image_bytes = await image.read()
    with open(image_before_path, "wb") as f:
        f.write(image_bytes)

    incident.status = "DETECTED"
    incident.timeline.append(TimelineEvent(
        timestamp=datetime.utcnow().strftime("%H:%M"),
        stage="SYSTEM",
        decision="Re-uploaded image received",
        confidence="100%",
        reason="Citizen provided higher quality evidence.",
        next_action="Rerunning Perception Agent analysis"
    ))

    incident = await perception_agent.analyze(image_bytes, incident, mime_type=image.content_type or "image/jpeg", filename=image.filename)
    db.save_incident(incident)
    return incident

# ---------------------------------------------------------
# 2. AGENT ORCHESTRATOR & SIMULATOR CONTROL ENDPOINTS
# ---------------------------------------------------------


@app.get("/api/incidents/{incident_id}/decision")
async def get_agent_brain_decision(incident_id: str) -> PlannerDecision:
    """
    Returns the formatted PlannerDecision model read by the frontend dashboard.
    """
    incident = db.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return planner_agent.get_brain_decision(incident)


@app.get("/api/incidents/{incident_id}")
async def get_incident(incident_id: str) -> Incident:
    incident = db.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@app.get("/api/incidents")
async def list_incidents() -> List[Incident]:
    return db.list_incidents()


@app.post("/api/incidents/{incident_id}/tick")
async def trigger_agent_tick(incident_id: str, mode: str = "api"):
    """
    Forces the central planner orchestrator loop to run a tick (step transition).
    Useful to run via REST or frontend trigger.
    """
    incident = db.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    updated_incident = await planner_agent.execute_step(incident, submission_mode=mode)
    db.save_incident(updated_incident)
    return updated_incident

# ---------------------------------------------------------
# 3. MOCK GOVERNMENT PORTAL SYSTEM
# ---------------------------------------------------------


@app.post("/api/mock-portal/submit")
async def submit_mock_portal_complaint(data: dict):
    """
    The endpoint hit by our portal submission tools (Playwright / direct API).
    Generates a tracking token and maps status.
    """
    incident_id = data.get("incident_id")
    issue_type = data.get("issue_type")

    # Generate unique complaint token
    token = f"BBMP-{uuid.uuid4().hex[:5].upper()}"
    MOCK_PORTAL_TICKETS[token] = {
        "incident_id": incident_id,
        "issue_type": issue_type,
        "status": "PENDING",
        "created_at": datetime.utcnow().isoformat()
    }
    logger.info(f"Mock Portal Ticket Created: {token}")
    return {"status": "success", "complaint_token": token}


@app.get("/api/mock-portal/tickets/{token}")
async def get_mock_portal_ticket(token: str):
    ticket = MOCK_PORTAL_TICKETS.get(token)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket token not found")
    return ticket

# ---------------------------------------------------------
# 4. SIMULATION DASHBOARD TICKET MANIPULATIONS
# ---------------------------------------------------------


@app.post("/api/simulator/mark-resolved/{token}")
async def simulator_mark_resolved(token: str):
    """
    Forces the portal database status of a token to 'RESOLVED'.
    Allows the monitoring agent to detect change and transition state.
    """
    if token not in MOCK_PORTAL_TICKETS:
        raise HTTPException(status_code=404, detail="Token not found in Mock Portal")

    MOCK_PORTAL_TICKETS[token]["status"] = "RESOLVED"

    # Locate the active incident mapping to this token and transition it
    for inc in db.list_incidents():
        if inc.official_token == token:
            inc.status = "VERIFYING"
            inc.timeline.append(TimelineEvent(
                timestamp=datetime.now().strftime("%d %b %H:%M"),
                stage="MONITOR",
                decision="Portal resolution detected",
                confidence="100%",
                reason="External portal marked ticket status as RESOLVED.",
                next_action="Request citizen upload a resolution verification photo"
            ))
            db.save_incident(inc)
            return {"status": "success", "message": "Ticket marked resolved. Incident transitioned to VERIFYING."}

    return {"status": "success", "message": "Ticket status marked RESOLVED in portal database."}


@app.post("/api/simulator/trigger-sla-breach/{incident_id}")
async def simulator_trigger_sla_breach(incident_id: str):
    """
    Fast-forwards time by setting the SLA deadline to 1 hour in the past.
    Next tick of the monitoring agent will trigger an SLA breach and escalate.
    """
    incident = db.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.sla_deadline = (datetime.now() - timedelta(hours=1)).isoformat()
    db.save_incident(incident)
    return {"status": "success", "message": "SLA deadline fast-forwarded. Triggering breach on next agent tick."}


@app.post("/api/simulator/simulate-crash/{incident_id}")
async def simulator_simulate_crash(incident_id: str):
    """
    Forces the incident into ESCALATED state, simulating a playwright or API portal submission crash.
    """
    incident = db.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.status = "CLOSED"
    incident.timeline.append(TimelineEvent(
        timestamp=datetime.now().strftime("%d %b %H:%M"),
        stage="TOOL",
        decision="Portal submission failed",
        confidence="0%",
        reason="Simulator override: Government submission database returned 504 Gateway Timeout.",
        next_action="Recommending manual dispatch via direct department helpline."
    ))
    incident.updated_at = datetime.now().isoformat()
    db.save_incident(incident)
    return {"status": "success", "message": "Portal crash simulation triggered."}


@app.get("/mock-portal", response_class=HTMLResponse)
async def serve_mock_portal():
    """
    Serves a simple visual HTML Form page representing the government portal.
    This page is loaded and filled in by Playwright browser automation.
    """
    return """
    <html>
        <head>
            <title>BBMP Municipal Incident Registration</title>
            <style>
                body { font-family: sans-serif; background: #0f172a; color: #f1f5f9; padding: 40px; }
                .form-box { max-width: 500px; margin: auto; background: #1e293b; padding: 20px; border-radius: 8px; border: 1px solid #334155; }
                input, select { width: 100%; padding: 8px; margin: 10px 0; background: #0f172a; color: #fff; border: 1px solid #475569; border-radius: 4px; }
                button { background: #10b981; color: white; border: none; padding: 10px 20px; cursor: pointer; border-radius: 4px; width: 100%; font-weight: bold; }
                button:hover { background: #059669; }
            </style>
        </head>
        <body>
            <div class="form-box">
                <h2>Mock BBMP Civic Portal</h2>
                <form id="portal-form" onsubmit="event.preventDefault(); submitForm();">
                    <label>Incident ID:</label>
                    <input type="text" id="incident-id" required>
                    <label>Issue Type:</label>
                    <select id="issue-type">
                        <option value="garbage">Garbage</option>
                        <option value="pothole">Pothole</option>
                        <option value="fallen_tree">Fallen Tree</option>
                    </select>
                    <label>Latitude:</label>
                    <input type="text" id="latitude" required>
                    <label>Longitude:</label>
                    <input type="text" id="longitude" required>
                    <label>Severity:</label>
                    <select id="severity">
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                    </select>
                    <button type="submit" id="submit-btn">File Official Complaint</button>
                </form>
                <div id="result-box" style="margin-top:20px; display:none;">
                    <p>Submission Successful!</p>
                    <label>Tracking Token:</label>
                    <input type="text" id="complaint-token" readonly>
                </div>
            </div>
            <script>
                async function submitForm() {
                    const payload = {
                        incident_id: document.getElementById("incident-id").value,
                        issue_type: document.getElementById("issue-type").value,
                        latitude: parseFloat(document.getElementById("latitude").value),
                        longitude: parseFloat(document.getElementById("longitude").value),
                        severity: document.getElementById("severity").value
                    };
                    const response = await fetch("/api/mock-portal/submit", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload)
                    });
                    const res = await response.json();
                    document.getElementById("complaint-token").value = res.complaint_token;
                    document.getElementById("portal-form").style.display = "none";
                    document.getElementById("result-box").style.display = "block";
                }
            </script>
        </body>
    </html>
    """


@app.get("/api/incidents/{incident_id}/download-form")
async def download_incident_form(incident_id: str):
    incident = db.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    res = await legal_petition_generator.generate_petition(
        incident,
        escalation_target="Ward Junior Engineer & Nodal Officer"
    )
    from fastapi.responses import Response
    return Response(
        content=res["html_petition"],
        media_type="text/html",
        headers={
            "Content-Disposition": f"attachment; filename=ACIRP_Petition_{incident_id}.html"
        }
    )


@app.get("/api/incidents/{incident_id}/download-escalation-letter")
async def download_escalation_letter(incident_id: str):
    incident = db.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    escalation_paths = incident.current_strategy.escalation_path if incident.current_strategy else []
    target_idx = max(0, incident.escalation_level - 1)
    escalation_target = escalation_paths[target_idx] if target_idx < len(
        escalation_paths) else "Zonal Administration Commissioner"

    res = await legal_petition_generator.generate_petition(
        incident,
        escalation_target=escalation_target
    )
    from fastapi.responses import Response
    return Response(
        content=res["html_petition"],
        media_type="text/html",
        headers={
            "Content-Disposition": f"attachment; filename=ACIRP_Escalation_Petition_{incident_id}.html"
        }
    )


# ---------------------------------------------------------
# PARITOK TOKEN-EFFICIENCY API ENDPOINTS
# ---------------------------------------------------------


class OptimizeRequest(FastAPIModel):
    raw_prompt: str
    system_rules: Optional[str] = ""
    retrieved_docs: Optional[List[dict]] = None
    conversation_history: Optional[List[dict]] = None


@app.get("/api/paritok/dashboard")
async def get_paritok_dashboard():
    """
    Returns live cumulative Paritok token metrics, savings percentage, cost saved,
    request history log, and active optimizer source.
    """
    summary = paritok_session.get_summary()
    optimizer = ParitokContextOptimizer()
    source_status = "PARITOK_HOSTED_API" if optimizer.api_key and optimizer.api_key != "dummy_key_for_offline_mock" else "LOCAL_FALLBACK_OPTIMIZER"
    summary["active_optimizer_source"] = source_status
    return summary


@app.post("/api/paritok/optimize")
async def optimize_custom_prompt(req: OptimizeRequest):
    """
    Dedicated endpoint to test Paritok context optimization on any custom text or RAG prompt.
    Returns before vs after prompt, token counts, savings %, efficiency score, and pruned chunk reasons.
    """
    optimizer = ParitokContextOptimizer()
    optimized_prompt, metrics = await optimizer.optimize_context(
        raw_prompt=req.raw_prompt,
        system_rules=req.system_rules or "",
        retrieved_docs=req.retrieved_docs or [],
        conversation_history=req.conversation_history or [],
        request_type="Custom Prompt Sandbox Optimization"
    )
    return {
        "original_prompt": metrics.original_prompt,
        "optimized_prompt": optimized_prompt,
        "metrics": metrics
    }


@app.post("/api/paritok/compare")
async def compare_with_without_paritok(req: OptimizeRequest):
    """
    Benchmark endpoint comparing request execution WITH vs WITHOUT Paritok side-by-side.
    """
    optimizer = ParitokContextOptimizer()
    optimized_prompt, metrics = await optimizer.optimize_context(
        raw_prompt=req.raw_prompt,
        system_rules=req.system_rules or "",
        retrieved_docs=req.retrieved_docs or [],
        conversation_history=req.conversation_history or [],
        request_type="With vs Without Paritok Benchmark"
    )

    cost_without = round((metrics.original_tokens / 1000.0) * optimizer.token_cost, 6)
    cost_with = round((metrics.optimized_tokens / 1000.0) * optimizer.token_cost, 6)

    return {
        "without_paritok": {
            "prompt": metrics.original_prompt,
            "tokens": metrics.original_tokens,
            "estimated_cost_usd": cost_without,
            "status": "Full uncompressed context with boilerplate noise"
        },
        "with_paritok": {
            "prompt": optimized_prompt,
            "tokens": metrics.optimized_tokens,
            "tokens_saved": metrics.tokens_saved,
            "savings_percentage": metrics.savings_percentage,
            "estimated_cost_usd": cost_with,
            "cost_saved_usd": metrics.cost_saved_usd,
            "efficiency_score": metrics.efficiency_score,
            "status": "Paritok optimized context (essential facts retained)"
        },
        "optimizer_source": metrics.optimizer_source,
        "pruned_chunks": metrics.pruned_chunks
    }


@app.get("/api/incidents/{incident_id}/paritok-metrics")
async def get_incident_paritok_metrics(incident_id: str):
    """
    Returns Paritok token metrics and Before vs After prompt inspection details for a specific incident.
    """
    incident = db.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident.paritok_metrics or {
        "message": "Paritok metrics pending for this incident."
    }


@app.get("/api/paritok/dashboard")
async def get_paritok_dashboard_metrics():
    """
    Returns real-time Paritok hosted GPU server metrics and session summary.
    """
    from agents.paritok_optimizer import paritok_session, PARITOK_API_KEY, PARITOK_BASE_URL
    summary = paritok_session.get_summary()
    return {
        "active_optimizer_source": "PARITOK_HOSTED_API" if PARITOK_API_KEY else "LOCAL_FALLBACK_OPTIMIZER",
        "paritok_api_key_configured": bool(PARITOK_API_KEY),
        "paritok_gpu_server_base_url": PARITOK_BASE_URL or "https://www.paritok.com/api",
        "summary": summary
    }


# ---------------------------------------------------------
# STATIC FILE SERVING FOR UPLOADED IMAGES
# ---------------------------------------------------------
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")
