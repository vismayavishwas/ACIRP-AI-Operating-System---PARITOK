"""Pipeline proof: evidence bundle flows through Paritok into petition; metrics honest."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # noqa: E402

from models import Incident  # noqa: E402
from agents.paritok_optimizer import paritok_session  # noqa: E402
from agents.petition_generator import legal_petition_generator  # noqa: E402

CASE_ASSERTS = {
    "pothole": "Section 58 (Public Streets Maintenance)",
    "garbage": "Solid Waste Management (SWM) Rules 2016",
    "fallen_tree": "Preservation of Trees Act",
}


def build_incident(issue_type: str) -> Incident:
    return Incident(
        id=f"inc_proof_{issue_type}",
        status="PLANNED",
        issue_type=issue_type,
        latitude=12.9716,
        longitude=77.5946,
        complainant_name="Proof Citizen",
        image_before_url="/static/proof.jpg",
    )


async def run_petition_case(issue_type: str) -> dict:
    incident = build_incident(issue_type)
    res = await legal_petition_generator.generate_petition(
        incident, escalation_target="Ward Junior Engineer & Nodal Officer"
    )
    print("\n" + "=" * 60)
    print(f"ISSUE TYPE: {issue_type.upper()}")
    print(f"Raw evidence tokens:  {res['original_tokens']}")
    print(f"Optimized tokens:     {res['optimized_tokens']}")
    print(f"Tokens saved:         {res['tokens_saved']}")
    print(f"Savings %:            {res['savings_percentage']}%")
    print(f"Optimizer source:     {res['optimizer_source']}")
    print("=" * 60)
    return {"res": res, "html": res["html_petition"]}


async def run_all_cases() -> dict:
    results = {}
    for issue_type in ["pothole", "garbage", "fallen_tree"]:
        results[issue_type] = await run_petition_case(issue_type)
    return results


def test_pipeline_proof_all_issue_types():
    requests_before = paritok_session.total_requests
    orig_before = paritok_session.total_original_tokens
    opt_before = paritok_session.total_optimized_tokens
    saved_before = paritok_session.total_tokens_saved
    results = asyncio.run(run_all_cases())

    for issue_type, data in results.items():
        assert data["res"]["original_tokens"] >= 3000, (
            f"{issue_type}: bundle only {data['res']['original_tokens']} tokens - dropped!"
        )
        assert data["res"]["paritok_metrics"] is not None
        assert "ACIRP MUNICIPAL KNOWLEDGE BASE: EVIDENCE BUNDLE FOR ISSUE" in data["html"]

    for issue_type, expected in CASE_ASSERTS.items():
        assert expected in results[issue_type]["html"]

    assert "Section 58" not in results["garbage"]["html"]
    assert "Section 58" not in results["fallen_tree"]["html"]
    assert "Preservation of Trees Act" not in results["pothole"]["html"]
    assert "SWM Rules 2016" not in results["pothole"]["html"]

    # Session accumulated exactly 3 new petition requests for this test.
    assert paritok_session.total_requests == requests_before + 3

    # This test's own petition metrics are internally consistent (no fabrication).
    delta_orig = paritok_session.total_original_tokens - orig_before
    delta_opt = paritok_session.total_optimized_tokens - opt_before
    delta_saved = paritok_session.total_tokens_saved - saved_before
    assert delta_opt <= delta_orig
    assert delta_saved == max(0, delta_orig - delta_opt)
