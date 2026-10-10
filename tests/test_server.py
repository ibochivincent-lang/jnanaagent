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
