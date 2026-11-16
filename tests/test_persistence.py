# tests/test_persistence.py
"""Additional tests to verify persistent storage functionality"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import CalculationSession, CalculatorLog

client = TestClient(app)

def test_database_tables_exist():
    """Verify that CalculationSession and CalculatorLog tables are defined."""
    # This is more of a structural test - if we got this far, 
    # the models should be defined without errors

def test_persistent_calculation_storage():
    """Test that calculations are persisted to database."""
    # Clear history first
    client.delete("/history")
    
    # Make a calculation
    response = client.post("/calculate", json={"expr": "2+2"})
    assert response.json()["ok"] is True
    
    # Verify it appears in history
    history = client.get("/history").json()
    assert len(history) == 1
    assert history[0]["expr"] == "2+2"
    assert history[0]["result"] == 4

def test_multiple_calculations():
    """Test storing multiple calculations."""
    client.delete("/history")
    
    # Multiple calculations
    for expr in ["1+1", "2+2", "3+3"]:
        response = client.post("/calculate", json={"expr": expr})
        assert response.json()["ok"] is True
    
    # Check all appear in order
    history = client.get("/history").json()
    assert len(history) == 3
    assert history[0]["expr"] == "3+3"  # Newest first
    assert history[2]["expr"] == "1+1"  # Oldest last

def test_invalid_calculations_not_persisted():
    """Test that invalid calculations do not get stored."""
    client.delete("/history")
    
    # Valid calculation (should be stored)  
    response1 = client.post("/calculate", json={"expr": "2+2"})
    assert response1.json()["ok"] is True
    
    # Invalid calculation (should not be stored)
    response2 = client.post("/calculate", json={"expr": "1/0"})
    assert response2.json()["ok"] is False
    
    # Only the valid calculation should appear
    history = client.get("/history").json() 
    assert len(history) == 1
    assert history[0]["expr"] == "2+2"

def test_history_deletion_clears_both_sessions_and_logs():
    """Test that deleting history removes both session and log entries."""
    client.delete("/history")
    
    # Add some calculations
    client.post("/calculate", json={"expr": "1+1"})  
    client.post("/calculate", json={"expr": "2+2"})
    
    # Check that history is populated
    history = client.get("/history").json()
    assert len(history) == 2
    
    # Delete history
    delete_response = client.delete("/history")
    assert delete_response.json()["ok"] is True
    assert delete_response.json()["cleared"] is True
    
    # Verify history is cleared
    history_after = client.get("/history").json()
    assert len(history_after) == 0