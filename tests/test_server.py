"""Test FastAPI server routes and SSE event streaming."""

import json
from fastapi.testclient import TestClient
from research_agent.server import app

client = TestClient(app)


def test_api_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["team"]["name"] == "Vincci001"
    assert "integrations" in data


def test_api_reports_list():
    response = client.get("/api/reports")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_web_index_serving():
    response = client.get("/")
    assert response.status_code == 200
    assert "Jnana Agent" in response.text
    assert "Access Terminal" in response.text


def test_spa_catch_all():
    response = client.get("/clients")
    assert response.status_code == 200
    assert "Jnana Agent" in response.text
    assert "Access Terminal" in response.text


def test_terminal_serving():
    response = client.get("/terminal")
    assert response.status_code == 200
    assert "Jnana Agent" in response.text
    assert "Autonomous Codebase Reasoning" in response.text
    assert "Code Fix &" in response.text


def test_reproduce_test_endpoint():
    response = client.post("/api/reproduce-test", json={"issue_ref": "JnanaAgent#482"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["verified"] is True
    assert "1 unpatched failure caught" in data["summary"]


def test_create_pr_endpoint():
    response = client.post(
        "/api/create-pr",
        json={
            "repo": "ibochivincent-lang/jnanaagent",
            "issue_ref": "JnanaAgent#482",
            "title": "fix(cli): test pr creation"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ready", "created"]
    assert "pr_url" in data


def test_github_webhook_get():
    response = client.get("/api/webhook/github")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert "usage" in data


def test_github_webhook_post():
    response = client.post(
        "/api/webhook/github",
        json={"ref": "refs/heads/master", "after": "test_commit_sha"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "triggered"
    assert "Continuous deployment" in data["message"]


def test_github_inspect_endpoint():
    response = client.post(
        "/api/github/inspect",
        json={"repo": "ibochivincent-lang/jnanaagent"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "repo" in data
    assert "diagnosis" in data


def test_export_report_audit():
    # Fetch reports list first to get existing file
    rep_res = client.get("/api/reports")
    assert rep_res.status_code == 200
    reports = rep_res.json()
    if reports:
        fname = reports[0]["filename"]
        aud_res = client.get(f"/api/reports/{fname}/export-audit")
        assert aud_res.status_code == 200
        pkg = aud_res.json()
        assert pkg["standard"] == "Proof of Search / neatHack 2026"
        assert "cryptographic_proof" in pkg
        assert "consensus_matrix" in pkg


def test_vibe_explain_endpoint():
    response = client.post(
        "/api/vibe/explain",
        json={
            "problem_type": "error",
            "content": "TypeError: string indices must be integers in parse_model_arguments",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "step1" in data
    assert "step2" in data
    assert "step3" in data
    assert "step4" in data
    assert "mermaid_syntax" in data["step3"]
    assert "fixed_code" in data["step4"]


def test_neatlogs_detected_issues():
    response = client.get("/api/neatlogs/issues")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "recent_issues" in data
    assert len(data["recent_issues"]) >= 1


def test_vibe_explain_triple_visualizers():
    """Verify that all 3 debugging visualizers (Diagram-Copilot, Mise-en-scène, Vibe-to-Code) are returned."""
    response = client.post(
        "/api/vibe/explain",
        json={
            "problem_type": "error",
            "content": "TypeError: string indices must be integers in parse_model_arguments",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    vis = data.get("step3", {}).get("visualizers") or data.get("step3_visualization", {}).get("visualizers")
    assert vis is not None
    assert "diagram_copilot" in vis
    assert "mise_en_scene" in vis
    assert "vibe_to_code" in vis

    # 1. Diagram-copilot checks
    assert "mermaid_code" in vis["diagram_copilot"]
    assert "graph TD" in vis["diagram_copilot"]["mermaid_code"]

    # 2. Mise-en-scène checks
    assert "svg_markup" in vis["mise_en_scene"]
    assert "<svg" in vis["mise_en_scene"]["svg_markup"]
    assert "MISE-EN-SCÈNE" in vis["mise_en_scene"]["svg_markup"]

    # 3. Vibe-to-code checks
    assert "data" in vis["vibe_to_code"]
    assert "blocks" in vis["vibe_to_code"]["data"]
    assert len(vis["vibe_to_code"]["data"]["blocks"]) >= 3


def test_observability_providers():
    """Verify that /api/observability/providers returns Neatlogs, Langfuse, and Braintrust."""
    response = client.get("/api/observability/providers")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    provider_ids = [p["id"] for p in data["providers"]]
    assert "neatlogs" in provider_ids
    assert "langfuse" in provider_ids
    assert "braintrust" in provider_ids


def test_langfuse_traces():
    """Verify that /api/langfuse/traces returns trace analytics and spans."""
    response = client.get("/api/langfuse/traces")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "summary" in data
    assert "p95_latency_ms" in data["summary"]
    assert len(data["recent_traces"]) >= 1


def test_braintrust_evals():
    """Verify that /api/braintrust/evals returns automated benchmark evaluation matrix."""
    response = client.get("/api/braintrust/evals")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "eval_scores" in data
    assert "ast_accuracy" in data["eval_scores"]
    assert data["eval_scores"]["zero_mock_adherence"] == 1.0


def test_status_includes_langfuse_and_braintrust():
    """Verify that /api/status telemetry integration block contains Langfuse and Braintrust."""
    response = client.get("/api/status")
    assert response.status_code == 200
    integrations = response.json().get("integrations", {})
    assert "langfuse" in integrations
    assert integrations["langfuse"]["active"] is True
    assert "braintrust" in integrations
    assert integrations["braintrust"]["active"] is True



